import React from 'react';
import {AbsoluteFill,useCurrentFrame,random} from 'remotion';
import {C,fr,ez} from './common';
const Halftone:React.FC<{f:number}>=({f})=>{
  const s=fr(5.38),e=fr(5.70);if(f<s||f>e)return null;
  const k=(f-s)/(e-s);const cell=54,cols=Math.ceil(1080/cell),rows=Math.ceil(1920/cell);const out:any[]=[];
  for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){
    const sweep=(c/cols)*0.5+(r/rows)*0.2;const loc=(k*1.5-sweep);
    const rad=cell*0.78*Math.max(0,Math.sin(Math.max(0,Math.min(1,loc))*Math.PI));
    if(rad>0.5)out.push(<circle key={r*100+c} cx={c*cell+cell/2} cy={r*cell+cell/2} r={rad} fill={(r+c)%5===0?C.red:C.ink}/>);}
  return <svg width={1080} height={1920} style={{position:'absolute',inset:0}}>{out}</svg>;
};
const Glitch:React.FC<{f:number}>=({f})=>{
  const s=fr(7.95),e=fr(8.15);if(f<s||f>e)return null;
  const bars=[];for(let i=0;i<9;i++){const y=random('y'+i+f)*1800,h=20+random('h'+i+f)*110;const col=i%3===0?C.red:i%3===1?'#00e5ff':'#fff';
    bars.push(<div key={i} style={{position:'absolute',left:(random('x'+i+f)-0.5)*160,top:y,width:1300,height:h,background:col,opacity:0.5,mixBlendMode:'screen'}}/>);}
  return <AbsoluteFill>{bars}<AbsoluteFill style={{background:'#fff',opacity:f===s+2?0.6:0}}/></AbsoluteFill>;
};
const GlassWipe:React.FC<{f:number}>=({f})=>{
  const s=fr(10.22),e=fr(10.45);if(f<s||f>e)return null;
  const x=ez(f,s,e,-500,1700);
  return <div style={{position:'absolute',top:-200,height:2400,width:420,left:x,transform:'rotate(14deg)',background:'linear-gradient(90deg,transparent,rgba(255,255,255,0.7),rgba(255,255,255,0.9),rgba(255,255,255,0.7),transparent)',filter:'blur(8px)'}}/>;
};
const Pixels:React.FC<{f:number}>=({f})=>{
  const s=fr(11.38),e=fr(11.62);if(f<s||f>e)return null;
  const k=(f-s)/(e-s);const g=90;const out=[];
  for(let r=0;r<22;r++)for(let c=0;c<12;c++){const th=random(`p${r}-${c}`);const on=k>th*0.6&&k<th*0.6+0.4;
    if(on)out.push(<div key={r*20+c} style={{position:'absolute',left:c*g,top:r*g,width:g,height:g,background:(r+c)%3===0?C.red:(r+c)%3===1?C.ink:C.paper}}/>);}
  return <AbsoluteFill>{out}</AbsoluteFill>;
};
export const Top:React.FC=()=>{
  const f=useCurrentFrame();
  const flash=[fr(3.60),fr(5.52)].some(c=>f>=c&&f<c+3)?0.35:0;
  const prog=f/391;
  return <AbsoluteFill>
    <Halftone f={f}/><Glitch f={f}/><GlassWipe f={f}/><Pixels f={f}/>
    <AbsoluteFill style={{background:'#fff',opacity:flash}}/>
    <div style={{position:'absolute',left:60,right:60,top:46,height:6,borderRadius:3,background:'rgba(255,255,255,0.3)'}}><div style={{width:`${prog*100}%`,height:'100%',borderRadius:3,background:C.red}}/></div>
    <svg width={1080} height={1920} style={{position:'absolute',inset:0,opacity:0.07,mixBlendMode:'overlay'}}>
      <filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={f%7}/><feColorMatrix type="saturate" values="0"/></filter>
      <rect width="1080" height="1920" filter="url(#n)"/></svg>
  </AbsoluteFill>;
};
