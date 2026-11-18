import React from 'react';
import {AbsoluteFill,Img,staticFile,useCurrentFrame,random} from 'remotion';
import {Fonts,sp,ez,Icon} from './common';
const OR='#F26A0C',INK='#0E0E10';
export const End:React.FC=()=>{
  const f=useCurrentFrame();
  const logo=sp(f,10,{damping:9,stiffness:140,mass:0.8});
  const fl=Math.sin(f/18)*9;
  const word='Coming Soon';
  const dots=[0,1,2].map(i=>f>=62+i*5?1:0);
  const pill=sp(f,70,{damping:12,stiffness:150});
  return <AbsoluteFill style={{background:'radial-gradient(circle at 50% 42%,#FFF8F1 0%,#FFEBD6 55%,#FFDDBA 100%)'}}><Fonts/>
    {/* soft drifting sparkles */}
    {Array.from({length:14}).map((_,i)=>{const x=random('x'+i)*1080,y0=random('y'+i)*1920,s=8+random('s'+i)*16;
      const y=(y0-f*(0.8+random('v'+i)*1.4)+1920)%1920;const o=ez(f,5,25)*0.5*(0.5+0.5*Math.sin(f/10+i));
      return <div key={i} style={{position:'absolute',left:x,top:y,width:s,height:s,borderRadius:'50%',background:OR,opacity:o}}/>;})}
    {/* halo rings */}
    {[0,1,2].map(i=>{const t=((f-14-i*16)%60+60)%60/60;const on=f>=14+i*16;
      return <div key={i} style={{position:'absolute',left:540-300,top:800-300,width:600,height:600,borderRadius:'50%',border:`4px solid ${OR}`,opacity:on?(1-t)*0.45:0,transform:`scale(${0.9+t*0.75})`}}/>;})}
    <div style={{position:'absolute',left:540-290,top:800-290+fl,width:580,height:580,transform:`scale(${logo}) rotate(${(1-logo)*-14}deg)`,filter:'drop-shadow(0 30px 50px rgba(242,106,12,0.35))'}}>
      <Img src={staticFile('logo.png')} style={{width:'100%',height:'100%'}}/></div>
    <div style={{position:'absolute',left:0,right:0,top:1140,display:'flex',justifyContent:'center',alignItems:'baseline',overflow:'hidden',padding:'10px 0'}}>
      {word.split('').map((ch,i)=>{const q=sp(f,34+i*1.6,{damping:13});
        return <span key={i} style={{fontFamily:'InterX',fontWeight:900,fontSize:130,color:OR,whiteSpace:'pre',letterSpacing:-3,display:'inline-block',transform:`translateY(${(1-q)*120}%)`,opacity:Math.min(1,q*2)}}>{ch}</span>;})}
      {dots.map((d,i)=><span key={'d'+i} style={{fontFamily:'InterX',fontWeight:900,fontSize:130,color:OR,opacity:d,transform:`scale(${d?1:0.4})`}}>.</span>)}
    </div>
    <div style={{position:'absolute',left:0,right:0,top:1330,display:'flex',justifyContent:'center'}}>
      <div style={{transform:`translateY(${(1-pill)*80}px) scale(${0.85+0.15*pill})`,opacity:Math.min(1,pill*1.6),display:'flex',alignItems:'center',gap:22,background:INK,borderRadius:90,padding:'26px 56px',boxShadow:'0 24px 50px rgba(14,14,16,0.3)'}}>
        <Icon n="live" s={0} c={OR}/>
        <svg width="54" height="54" viewBox="0 0 24 24" fill="none" stroke={OR} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M8 3v4M16 3v4M3 10h18"/></svg>
        <span style={{fontFamily:'ISerif',fontStyle:'italic',fontSize:60,color:'#fff'}}>On</span>
        <span style={{fontFamily:'InterX',fontWeight:900,fontSize:64,color:'#fff',letterSpacing:1}}>7 DEC 2026</span>
      </div>
    </div>
  </AbsoluteFill>;
};
