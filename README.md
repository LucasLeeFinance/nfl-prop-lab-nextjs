NFL Prop Lab V4 — Real-data research terminal
What works
Next.js interactive six-section dark research terminal, searchable and sortable Underdog prop board, all returned players and markets, custom prop lines, L5/L10/L20, game-by-game bars, hit rate, usage, opponent team defense, team game-script splits, named secondary injuries and potential CB depth-chart options.
Existing secure `/api/underdog` route uses the Vercel `UNDERDOG_API_KEY` environment variable. API returns a partial board and may use paid API quota; it is not a guaranteed daily single call.
GitHub Actions downloads real weekly player statistics and play-by-play from nflverse and writes `public/data/nfl.json`. Player history includes prior season. The app never uses the old illustrative demo numbers.
Injury/depth data are attempted from nflverse releases, with errors shown in dataset notes if the specific feeds are unavailable. A depth-chart option is not a confirmed injury replacement.
Manual, attributed coverage statistics and PFF grade fields are supported via `data/coverage_manual.json` and `data/pff_manual.json`. No PFF grade is supplied and no premium data is scraped.
Install from V2 (you do not need V3)
Extract this ZIP. In your existing GitHub repo, replace `app/page.tsx`, `app/globals.css`, `app/layout.tsx`, `package.json`, and the other included top-level config files only if needed. The easiest approach is uploading the extracted project contents into your existing repo with the same folder paths; do not upload the ZIP as a single file.
Keep your existing `UNDERDOG_API_KEY` in Vercel. The included `app/api/underdog/route.ts` is compatible with your working V2 route.
Add new folders `.github/workflows`, `scripts`, `public/data` and new files `data/pff_manual.json`, `data/coverage_manual.json`. Preserve the paths.
Commit to `main` and wait for Vercel deployment. Initially, the verified game-history areas will correctly show data pending.
In GitHub, go to Actions → Refresh free NFL research data → Run workflow. The workflow fetches NFL data and commits `public/data/nfl.json`. This commit triggers another Vercel deployment.
Check Actions for errors. In Settings → Actions → General → Workflow permissions, select Read and write permissions if the bot cannot push the data file. Your GitHub plan must permit Actions for the repo.
Refresh your website and open Data Sources. It should show player counts, the last refresh, and any missing feeds. The refresh runs daily at 13:23 UTC. If upstream releases are unavailable, the workflow fails rather than publishing fake data.
Important limitations
PFF: PFF grades are proprietary and generally require paid access. `data/pff_manual.json` accepts entries such as `{"playernormalized":{"grade":82.3,"source":"Official PFF page citation","asOf":"2026-11-19"}}` only when you have permission to use the data. Empty by default.
Coverage: `data/coverage_manual.json` can accept sourced player coverage records with `player`, `team`, `targets`, `receptionsAllowed`, `yardsAllowed`, `source`, `asOf`. Empty by default. Team defensive yards/play are not CB coverage stats.
Injuries: NFL injury feeds may be delayed or absent. When present, names/status are shown, and CB depth names are potential options, not confirmed replacements.
Game script: Team pass/run rate is based on play-by-play with 7+ lead/trail thresholds, not player-specific route or coverage splits.
Period props: Quarter/half game logs are deliberately not inferred from full-game stats.
Historical match: Stats and Underdog offer naming may differ, so some players will have no matched logs.
Free tiers: GitHub Actions, Vercel Hobby and upstream endpoints have limits. No new paid services are required to use the available public-data functionality.
Local developer test
```bash
npm install
npm run build
```
For the data pipeline:
```bash
pip install -r scripts/requirements.txt
python scripts/build_data.py
```
Source: nflverse releases. PFF data source: PFF grades.
