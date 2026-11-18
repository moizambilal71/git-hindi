import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {C,Fonts,fr,sp,ez} from './common';
type L={t:string,s:number,c:string};
type B={s:number,e:number,lines:L[],style:string,sub?:string,cy:number,sizeMax?:number};
const R=C.red,W=C.paper;
const BACK:B[]=[
 {s:0.05,e:2.35,style:'rise',sub:'if you run a registered',cy:570,lines:[{t:'HOME',s:0.05,c:W},{t:'KITCHEN',s:1.16,c:R}]},
 {s:4.05,e:5.45,style:'slice',cy:640,lines:[{t:'DHABA',s:4.06,c:W},{t:'UNCLE',s:4.26,c:R}]},
 {s:5.55,e:7.30,style:'blur',cy:640,sub:'',lines:[{t:'JHATPAT',s:5.55,c:W},{t:'REGISTER',s:6.40,c:R}]},
 {s:7.70,e:11.30,style:'mask',cy:640,lines:[{t:'4',s:7.70,c:R},{t:'STEPS',s:8.0,c:W}],sizeMax:430},
 {s:11.45,e:13.04,style:'split',cy:640,lines:[{t:'GO LIVE',s:11.5,c:W},{t:'EARNING',s:12.3,c:R}]},
];
const measure=(t:string)=>{const c=document.createElement('canvas').getContext('2d')!;c.font='100px Anton';return c.measureText(t).width/100;};
const Line:React.FC<{l:L,f:number,b:B,fs:number,i:number,exit:number}>=({l,f,b,fs,i,exit})=>{
  const st=fr(l.s);const p=sp(f,st,{damping:14});const k=ez(f,st,st+14);
  const base:React.CSSProperties={fontFamily:'Anton',fontSize:fs,lineHeight:0.92,letterSpacing:-fs*0.01,color:l.c,whiteSpace:'nowrap',textTransform:'uppercase',
    textShadow:l.c===C.red?'0 10px 40px rgba(120,0,0,0.45)':'0 12px 44px rgba(0,0,0,0.45)',
    backgroundImage:'radial-gradient(rgba(0,0,0,0.16) 1.6px,transparent 2px)',backgroundSize:'9px 9px',WebkitBackgroundClip:'text' as any};
  let el:React.ReactNode;let wrapper:React.CSSProperties={};
  if(f<st) return <div style={{height:fs*0.92}}/>;
  if(b.style==='rise'){
    el=<div style={{overflow:'hidden',padding:'0 0 '+fs*0.06+'px'}}><div style={{display:'flex',justifyContent:'center'}}>{l.t.split('').map((ch,j)=>{const q=sp(f,st+j*1.2,{damping:13});return <span key={j} style={{...base,display:'inline-block',transform:`translateY(${(1-q)*115}%) rotate(${(1-q)*6}deg)`}}>{ch}</span>;})}</div></div>;
  } else if(b.style==='slice'){
    const x=(1-ez(f,st,st+12))*100;const dir=i%2?1:-1;
    el=<div style={{...base,clipPath:`inset(0 ${x}% 0 0)`,transform:`translateX(${(1-ez(f,st,st+12))*dir*120}px)`}}>{l.t}</div>;
  } else if(b.style==='blur'){
    const q=ez(f,st,st+12);
    el=<div style={{...base,transform:`scale(${0.8+0.2*q})`,filter:`blur(${(1-q)*26}px)`,opacity:q}}>{l.t}</div>;
  } else if(b.style==='mask'){
    el=<div style={{overflow:'hidden',padding:fs*0.04+'px 0'}}><div style={{...base,transform:`translateY(${(1-p)*105}%)`}}>{l.t}</div></div>;
  } else {
    const q=ez(f,st,st+14);const d=(1-q)*60;
    el=<div style={{position:'relative'}}>
      <div style={{...base,clipPath:'inset(0 0 50% 0)',transform:`translateX(${-d*12/6}px)`,opacity:q}}>{l.t}</div>
      <div style={{...base,position:'absolute',left:0,top:0,clipPath:'inset(50% 0 0 0)',transform:`translateX(${d*12/6}px)`,opacity:q}}>{l.t}</div></div>;
  }
  return <div style={wrapper}>{el}</div>;
};
export const Back:React.FC=()=>{
  const f=useCurrentFrame();
  return <AbsoluteFill><Fonts/>
    {BACK.map((b,bi)=>{
      const s=fr(b.s),e=fr(b.e);if(f<s||f>e)return null;
      const age=f-s,dur=e-s;
      const drift=ez(f,s,e,0,1);
      const exitK=ez(f,e-6,e);
      const maxW=940;
      const fs=Math.min(b.sizeMax??400,...b.lines.map(l=>maxW/measure(l.t)/1.0));
      const sc=1+0.045*drift;
      return <div key={bi} style={{position:'absolute',left:0,right:0,top:b.cy,transform:`translateY(-50%) translateY(${-35*drift-exitK*50}px) scale(${sc})`,opacity:1-exitK,filter:`blur(${exitK*8}px)`,display:'flex',flexDirection:'column',alignItems:'center'}}>
        {b.sub?<div style={{fontFamily:'ISerif',fontStyle:'italic',fontSize:96,color:'#fff',marginBottom:-6,opacity:ez(f,s,s+10),transform:`translateY(${(1-ez(f,s,s+10))*30}px)`,textShadow:'0 6px 30px rgba(0,0,0,0.5)'}}>{b.sub}</div>:null}
        {b.lines.map((l,i)=><Line key={i} l={l} f={f} b={b} fs={fs} i={i} exit={exitK}/>)}
      </div>;
    })}
  </AbsoluteFill>;
};
