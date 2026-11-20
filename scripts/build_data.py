"""Generate public, source-labeled NFL data. Run on GitHub Actions; no API keys required.
Never substitutes fabricated values for missing NFL data.
"""
import json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public'/'data'/'nfl.json'
SEASON=int(os.getenv('NFL_SEASON','2026'))
HEAD={'User-Agent':'NFLPropLabResearch/1.0 (public data downloader)'}
BASE='https://github.com/nflverse/nflverse-data/releases/download'

def parquet(tag, filename):
    url=f'{BASE}/{tag}/{filename}'
    print('Fetching',url,flush=True)
    r=requests.get(url,headers=HEAD,timeout=110)
    r.raise_for_status()
    from io import BytesIO
    return pd.read_parquet(BytesIO(r.content))

def clean(x):
    if pd.isna(x):return None
    if isinstance(x,(int,float)) and not isinstance(x,bool):return round(float(x),3)
    return str(x)

def col(row,*names):
    for n in names:
        if n in row and pd.notna(row[n]):return clean(row[n])
    return None

def normalize(name):return re.sub('[^a-z0-9]','',str(name).lower())

payload={'season':SEASON,'updatedAt':datetime.now(timezone.utc).isoformat(),'sources':{},'players':{},'defense':{},'script':{},'injuries':{},'depth':{},'coverage':{},'notes':[]}
# Load current and previous season: last 20 regular-season games can span years.
try:
    frames=[parquet('stats_player',f'stats_player_week_{s}.parquet') for s in [SEASON-1,SEASON]]
    df=pd.concat(frames,ignore_index=True)
    if 'season_type' in df:df=df[df.season_type=='REG']
    df=df.sort_values(['season','week'])
    fields=['passing_yards','passing_attempts','passing_tds','interceptions','rushing_yards','carries','rushing_tds','receiving_yards','receptions','targets','receiving_tds','receiving_air_yards','receiving_yards_after_catch','completions','passing_completions','sacks_suffered','rushing_attempts','fantasy_points','fantasy_points_ppr']
    for _,r in df.iterrows():
        name=col(r,'player_display_name','player_name')
        if not name:continue
        key=normalize(name)
        obj=payload['players'].setdefault(key,{'name':name,'team':col(r,'team','recent_team'),'position':col(r,'position'),'headshot':col(r,'headshot_url'),'games':[]})
        obj['team']=col(r,'team','recent_team') or obj['team']
        obj['position']=col(r,'position') or obj['position']
        game={'season':int(r['season']),'week':int(r['week']),'opponent':col(r,'opponent_team'),'team':col(r,'team','recent_team')}
        for f in fields:
            if f in r and pd.notna(r[f]):game[f]=clean(r[f])
        if 'rushing_attempts' in game and 'carries' not in game:game['carries']=game['rushing_attempts']
        if 'passing_completions' in game and 'completions' not in game:game['completions']=game['passing_completions']
        obj['games'].append(game)
    for obj in payload['players'].values():obj['games']=obj['games'][-22:]
    payload['sources']['players']='nflverse stats_player weekly parquet; previous and current seasons; regular season'
except Exception as e:payload['notes'].append('Player stats unavailable: '+str(e)[:180]);print(payload['notes'][-1],file=sys.stderr)

# PBP allows reproducible team pass/run splits and opponent allowed production.
try:
    pbp=parquet('pbp',f'play_by_play_{SEASON}.parquet')
    pbp=pbp[(pbp['season_type']=='REG') & (pbp['play_type'].isin(['pass','run'])) & (pbp['posteam'].notna()) & (pbp['defteam'].notna())]
    pbp['score_differential']=pd.to_numeric(pbp.get('score_differential'),errors='coerce')
    pbp['yards_gained']=pd.to_numeric(pbp.get('yards_gained'),errors='coerce').fillna(0)
    for team,grp in pbp.groupby('posteam'):
        states={}
        for label,subset in [('leading',grp[grp.score_differential>=7]),('close',grp[grp.score_differential.abs()<7]),('trailing',grp[grp.score_differential<=-7]),('all',grp)]:
            total=len(subset)
            states[label]={'plays':total,'passRate':round(100*(subset.play_type=='pass').sum()/total,1) if total else None,'runRate':round(100*(subset.play_type=='run').sum()/total,1) if total else None}
        payload['script'][str(team)]=states
    for team,grp in pbp.groupby('defteam'):
        passes=grp[grp.play_type=='pass'];runs=grp[grp.play_type=='run']
        payload['defense'][str(team)]={'plays':len(grp),'passPlays':len(passes),'rushPlays':len(runs),'passYardsPerPlay':round(passes.yards_gained.mean(),2) if len(passes) else None,'rushYardsPerPlay':round(runs.yards_gained.mean(),2) if len(runs) else None,'passRateFaced':round(len(passes)*100/len(grp),1)}
    payload['sources']['script']='nflverse 2026 play-by-play; score differential at snap; designed pass/run classification'
    payload['sources']['defense']='nflverse 2026 play-by-play; yards per play allowed (not coverage grades)'
except Exception as e:payload['notes'].append('PBP unavailable: '+str(e)[:180]);print(payload['notes'][-1],file=sys.stderr)

# Injury data is weekly, not a reliable source of confirmed depth-chart replacements.
try:
    injuries=parquet('injuries',f'injuries_{SEASON}.parquet')
    print('Injury columns:',list(injuries.columns))
    week_field=next((c for c in ['week','Week'] if c in injuries),None)
    if week_field:
        injuries=injuries[injuries[week_field]==injuries[week_field].max()]
    for _,r in injuries.iterrows():
        team=col(r,'team','Team');name=col(r,'full_name','player_name','name','Name')
        if not team or not name:continue
        payload['injuries'].setdefault(team,[]).append({'name':name,'position':col(r,'position','Position'),'status':col(r,'report_status','game_status','status'),'practice':col(r,'practice_status'),'injury':col(r,'report_primary_injury','primary_injury','injury'),'week':col(r,'week','Week')})
    payload['sources']['injuries']='nflverse weekly injury reports; latest published week (not official starting lineup)'
except Exception as e:payload['notes'].append('Injury report unavailable: '+str(e)[:180]);print(payload['notes'][-1],file=sys.stderr)

# Depth chart can list possible CB backups, but does NOT confirm replacement assignments.
try:
    depth=parquet('depth_charts',f'depth_charts_{SEASON}.parquet')
    print('Depth columns:',list(depth.columns))
    week_field=next((c for c in ['week','Week'] if c in depth),None)
    if week_field:depth=depth[depth[week_field]==depth[week_field].max()]
    for _,r in depth.iterrows():
        team=col(r,'club_code','team','Team');position=col(r,'position','pos_abb','position_group')
        if not team or not position or str(position).upper() not in ['CB','LCB','RCB','DB','NB']:continue
        payload['depth'].setdefault(team,[]).append({'name':col(r,'full_name','player_name','name'),'position':position,'depth':col(r,'depth_team','depth_position','depth_order')})
    payload['sources']['depth']='nflverse published depth charts; potential CB depth only, not verified one-to-one replacements'
except Exception as e:payload['notes'].append('Depth chart unavailable: '+str(e)[:180]);print(payload['notes'][-1],file=sys.stderr)

# Optional user-authored CB coverage entries; provenance and sample size required.
coverage_file=ROOT/'data'/'coverage_manual.json'
if coverage_file.exists():
    try:
        vals=json.loads(coverage_file.read_text())
        payload['coverage']={k:v for k,v in vals.items() if isinstance(v,dict) and all(x in v for x in ('player','team','targets','receptionsAllowed','yardsAllowed','source','asOf')) and all(isinstance(v[x],(int,float)) for x in ('targets','receptionsAllowed','yardsAllowed'))}
        if payload['coverage']:payload['sources']['coverage']='Manually entered, attributed and dated cornerback coverage samples; not official PFF grades'
    except Exception as e:payload['notes'].append('Coverage manual data invalid: '+str(e))

# Optional user-authored, properly sourced PFF values: no scraping or bypassing paywalls.
manual=ROOT/'data'/'pff_manual.json'
if manual.exists():
    try:
        vals=json.loads(manual.read_text())
        payload['pff']={k:v for k,v in vals.items() if isinstance(v,dict) and v.get('source') and v.get('asOf') and isinstance(v.get('grade'),(int,float))}
        payload['sources']['pff']='User-supplied, individually attributed and dated grades; NOT automatically retrieved'
    except Exception as e:payload['notes'].append('PFF manual data invalid: '+str(e))
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(payload,separators=(',',':'),ensure_ascii=False))
print('Wrote',OUT,'players',len(payload['players']),'script',len(payload['script']),'injuries',len(payload['injuries']))
if not payload['players']:sys.exit('No player data downloaded; do not overwrite existing dataset with empty data')
