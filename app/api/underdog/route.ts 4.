import {NextResponse} from 'next/server';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
const ENDPOINT = 'https://underdogapi.com/api/v1/projections';
type Offer = {id:string;player:string;team:string;opponent:string;stat:string;line:number;starts_at:string;observed_at:string;higher_available:boolean;lower_available:boolean;status:string};
let cached: {time:number; offers:Offer[]} | null = null;
export async function GET(){
 const key=process.env.UNDERDOG_API_KEY;
 if(!key)return NextResponse.json({error:'UNDERDOG_API_KEY is not configured on Vercel.',offers:[]},{status:503});
 if(cached && Date.now()-cached.time<24*60*60*1000)return NextResponse.json({offers:cached.offers,source:'Underdog API (cached)',cachedAt:new Date(cached.time).toISOString(),partial:true});
 try{
  const url=new URL(ENDPOINT);url.searchParams.set('league','NFL');url.searchParams.set('view','compact');url.searchParams.set('limit','100');
  const response=await fetch(url,{headers:{'x-api-key':key,'Authorization':`Bearer ${key}`,'Accept':'application/json'},cache:'no-store',signal:AbortSignal.timeout(12000)});
  if(!response.ok)return NextResponse.json({error:`Underdog provider returned HTTP ${response.status}. Check key and allowance.`,offers:[]},{status:502});
  const body=await response.json();
  const raw=Array.isArray(body)?body:Array.isArray(body.projections)?body.projections:Array.isArray(body.data)?body.data:Array.isArray(body.results)?body.results:[];
  const offers:Offer[]=raw.filter((x:Record<string,unknown>)=>x&&typeof x==='object'&&Number.isFinite(Number(x.line))&&x.player).map((x:Record<string,unknown>)=>({id:String(x.id??x.line_id??''),player:String(x.player??''),team:String(x.team??''),opponent:String(x.opponent??''),stat:String(x.stat??''),line:Number(x.line),starts_at:String(x.starts_at??''),observed_at:String(x.observed_at??''),higher_available:x.higher_available!==false,lower_available:x.lower_available!==false,status:String(x.status??'')}));
  cached={time:Date.now(),offers};
  return NextResponse.json({offers,source:'Underdog API',cachedAt:new Date(cached.time).toISOString(),partial:true});
 }catch{return NextResponse.json({error:'Could not reach Underdog provider.',offers:[]},{status:502})}
}
