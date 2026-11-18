import React from 'react';
import {staticFile,spring,interpolate,Easing,delayRender,continueRender} from 'remotion';
export const C={ink:'#0E0E10',red:'#E10600',paper:'#F4EFE9'};
export const FPS=30;
export const fr=(s:number)=>Math.round(s*FPS);
const css=`
@font-face{font-family:Anton;src:url(${staticFile('fonts/Anton.ttf')})}
@font-face{font-family:ISerif;src:url(${staticFile('fonts/InstrumentSerif.ttf')})}
@font-face{font-family:InterX;src:url(${staticFile('fonts/Inter.ttf')});font-weight:100 900}
@font-face{font-family:Pix;src:url(${staticFile('fonts/PressStart.ttf')})}`;
export const Fonts:React.FC=()=>{
  const [h]=React.useState(()=>delayRender('fonts'));
  React.useEffect(()=>{Promise.all(['100px Anton','100px ISerif','100px InterX','100px Pix'].map(f=>(document as any).fonts.load(f))).then(()=>continueRender(h));},[]);
  return <style>{css}</style>;
};
export const sp=(frame:number,start:number,cfg:any={})=>spring({frame:frame-start,fps:FPS,config:{damping:12,mass:0.6,stiffness:150,...cfg}});
export const ez=(f:number,a:number,b:number,from=0,to=1)=>interpolate(f,[a,b],[from,to],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.bezier(0.22,1,0.36,1)});
// shared glass look (no real backdrop in a transparent layer, so it is tinted + highlighted)
export const glass=(r=36):React.CSSProperties=>({
  borderRadius:r,
  background:'linear-gradient(135deg,rgba(255,255,255,0.34) 0%,rgba(255,255,255,0.12) 45%,rgba(20,20,26,0.32) 100%)',
  border:'1.5px solid rgba(255,255,255,0.5)',
  boxShadow:'0 30px 60px rgba(0,0,0,0.32),0 8px 18px rgba(0,0,0,0.25),inset 0 2px 1px rgba(255,255,255,0.6),inset 0 -10px 24px rgba(0,0,0,0.18)',
});
export const Sweep:React.FC<{f:number,r:number,w:number,h:number}>=({f,r,w,h})=>{
  const x=((f%60)/60)*2.4-0.7; // specular sweep every 2s
  return <div style={{position:'absolute',inset:0,borderRadius:r,overflow:'hidden',pointerEvents:'none'}}>
    <div style={{position:'absolute',top:-h*0.3,height:h*1.6,width:w*0.22,left:x*w,transform:'rotate(20deg)',background:'linear-gradient(90deg,transparent,rgba(255,255,255,0.55),transparent)'}}/>
  </div>;
};
const P={fill:'none',stroke:'#fff',strokeWidth:2,strokeLinecap:'round',strokeLinejoin:'round'} as any;
export const Icon:React.FC<{n:string,s:number,c?:string}>=({n,s,c='#fff'})=>{
  const pr={...P,stroke:c};
  const paths:Record<string,React.ReactNode>={
    search:<><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></>,
    pin:<><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0116 0z"/><circle cx="12" cy="10" r="3"/></>,
    utensils:<><path d="M3 2v7a3 3 0 003 3v10M7 2v7M11 2v7a3 3 0 01-3 3"/><path d="M21 2c-3 2-4 5-4 9h4v11"/></>,
    check:<><circle cx="12" cy="12" r="10"/><path d="M8 12.5l3 3 5-6"/></>,
    download:<><path d="M12 3v12M7 10l5 5 5-5M4 20h16"/></>,
    user:<><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/></>,
    list:<><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></>,
    live:<><circle cx="12" cy="12" r="2.4"/><path d="M7.5 7.5a6.4 6.4 0 000 9M16.5 7.5a6.4 6.4 0 010 9M4.5 4.5a10.6 10.6 0 000 15M19.5 4.5a10.6 10.6 0 010 15"/></>,
    trend:<><path d="M3 17l6-6 4 4 8-8M15 7h6v6"/></>,
  };
  return <svg width={s} height={s} viewBox="0 0 24 24" {...pr}>{paths[n]}</svg>;
};
