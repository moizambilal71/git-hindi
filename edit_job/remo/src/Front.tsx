import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {C,Fonts,fr,sp,ez,glass,Sweep,Icon} from './common';
const Tile:React.FC<{f:number,s:number,e:number,x:number,y:number,size:number,icon:string,label?:string,rx?:number,ry?:number,scale?:number,dim?:number,glow?:boolean,seed?:number}>=
({f,s,e,x,y,size,icon,label,rx=10,ry=-14,scale=1,dim=1,glow=false,seed=0})=>{
  if(f<s||f>e)return null;
  const p=sp(f,s,{damping:9,stiffness:170});const ex=ez(f,e-7,e);
  const fl=Math.sin((f+seed*13)/16)*10;
  const sc=p*(1-ex*0.5)*scale;
  return <div style={{position:'absolute',left:x,top:y,width:size,height:size,opacity:(1-ex)*dim,filter:ex>0?`blur(${ex*6}px)`:undefined,
    transform:`translateY(${fl}px) perspective(1000px) rotateX(${rx}deg) rotateY(${ry}deg) scale(${sc})`}}>
    <div style={{...glass(size*0.22),position:'absolute',inset:0,boxShadow:(glass(1).boxShadow as string)+(glow?`,0 0 60px ${C.red}aa`:'')}}>
      <Sweep f={f} r={size*0.22} w={size} h={size}/>
      <div style={{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center'}}>
        <div style={{width:size*0.46,height:size*0.46,borderRadius:'50%',background:glow?C.red:'rgba(225,6,0,0.92)',display:'flex',alignItems:'center',justifyContent:'center',boxShadow:'0 8px 20px rgba(0,0,0,0.35),inset 0 2px 2px rgba(255,255,255,0.5)'}}><Icon n={icon} s={size*0.28}/></div>
      </div>
    </div>
    {label?<div style={{position:'absolute',left:'50%',top:size+18,transform:'translateX(-50%)',fontFamily:'InterX',fontWeight:800,fontSize:30,letterSpacing:3,color:'#fff',background:C.ink,padding:'8px 22px',borderRadius:40,whiteSpace:'nowrap'}}>{label}</div>:null}
  </div>;
};
const Search:React.FC<{f:number}>=({f})=>{
  const s=fr(2.45),e=fr(4.05);if(f<s||f>e)return null;
  const p=sp(f,s,{damping:12});const ex=ez(f,e-7,e);
  const txt='customers near me';
  const n=Math.max(0,Math.min(txt.length,Math.floor(((f/30)-2.58)/(3.72-2.58)*txt.length)));
  const pin=sp(f,fr(3.45),{damping:8});
  return <div style={{position:'absolute',left:100,top:1130,width:880,height:130,transform:`scale(${p*(1-ex*0.4)}) translateY(${Math.sin(f/15)*7}px)`,opacity:1-ex,filter:`blur(${ex*6}px)`}}>
    <div style={{...glass(65),position:'absolute',inset:0,background:'linear-gradient(135deg,rgba(255,255,255,0.88),rgba(255,255,255,0.7))'}}><Sweep f={f} r={65} w={880} h={130}/>
      <div style={{position:'absolute',left:38,top:0,bottom:0,display:'flex',alignItems:'center',gap:22}}>
        <Icon n="search" s={56} c={C.ink}/>
        <span style={{fontFamily:'InterX',fontWeight:600,fontSize:48,color:C.ink}}>{txt.slice(0,n)}<span style={{opacity:Math.floor(f/8)%2?0:1,color:C.red}}>|</span></span>
      </div></div>
    <div style={{position:'absolute',right:-22,top:-52,width:96,height:96,borderRadius:'50%',background:C.red,display:'flex',alignItems:'center',justifyContent:'center',transform:`scale(${pin})`,boxShadow:'0 14px 30px rgba(0,0,0,0.4),inset 0 2px 2px rgba(255,255,255,0.5)'}}><Icon n="pin" s={52}/></div>
  </div>;
};
const STEPS=[['download','DOWNLOAD',8.32],['user','PROFILE',9.14],['list','MENU',10.32],['live','GO LIVE',11.48]] as const;
const Steps:React.FC<{f:number}>=({f})=>{
  const s=fr(8.3),e=fr(12.05);if(f<s||f>e)return null;
  const t=f/30;let act=-1;STEPS.forEach((x,i)=>{if(t>=x[2])act=i;});
  const gx=ez(f,e-6,e);
  return <div style={{opacity:1-gx,transform:`translateY(${gx*30}px)`}}>
    {STEPS.map((x,i)=>{const st=fr(x[2]);const isA=i===act;
      return <Tile key={i} f={f} s={st-0 > s ? st : s+i*4} e={e} x={84+i*234} y={1090} size={210} icon={x[0]} label={isA?x[1]:undefined}
        scale={isA?1.08:0.96} dim={isA||i>act?1:0.6} glow={isA} rx={8} ry={i<2?-12:12} seed={i}/>;})}
  </div>;
};
const Chart:React.FC<{f:number}>=({f})=>{
  const s=fr(12.02),e=fr(14.79);if(f<s||f>e)return null;
  const p=sp(f,s,{damping:11});
  const hs=[0.3,0.45,0.58,0.78,1];
  return <div style={{position:'absolute',left:190,top:1060,width:700,height:360,transform:`perspective(1100px) rotateX(8deg) rotateY(-10deg) scale(${p}) translateY(${Math.sin(f/14)*8}px)`}}>
    <div style={{...glass(40),position:'absolute',inset:0}}><Sweep f={f} r={40} w={700} h={360}/>
      <div style={{position:'absolute',left:50,right:50,bottom:44,top:70,display:'flex',alignItems:'flex-end',gap:26}}>
        {hs.map((h,i)=>{const q=sp(f,s+4+i*4,{damping:9,stiffness:210,mass:0.7});
          return <div key={i} style={{flex:1,height:`${Math.max(0,h*q)*100}%`,borderRadius:40,background:i===4?`linear-gradient(180deg,#ff5a4d,${C.red})`:`linear-gradient(180deg,rgba(225,6,0,${0.55+i*0.1}),rgba(120,0,0,0.75))`,boxShadow:'inset 0 3px 3px rgba(255,255,255,0.6),0 10px 20px rgba(0,0,0,0.25)'}}/>;})}
      </div>
      <div style={{position:'absolute',left:44,top:22,display:'flex',alignItems:'center',gap:12}}><Icon n="trend" s={38}/><span style={{fontFamily:'InterX',fontWeight:800,fontSize:30,color:'#fff',letterSpacing:3}}>EARNINGS</span></div>
    </div></div>;
};
export const Front:React.FC=()=>{
  const f=useCurrentFrame();
  return <AbsoluteFill><Fonts/>
    <Search f={f}/>
    <Tile f={f} s={fr(4.55)} e={fr(5.45)} x={700} y={1050} size={250} icon="utensils" label="PLATFORM" ry={-16}/>
    <Tile f={f} s={fr(6.40)} e={fr(7.45)} x={110} y={1050} size={250} icon="check" label="REGISTER" ry={16}/>
    <Steps f={f}/>
    <Chart f={f}/>
  </AbsoluteFill>;
};
