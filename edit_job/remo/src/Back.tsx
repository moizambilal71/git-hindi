import React from 'react';
import {AbsoluteFill,spring,useCurrentFrame} from 'remotion';
import {fitText} from '@remotion/layout-utils';
import {P,COL,ANTON,SERIF,useFonts,ease,clamp} from './shared';

const Line:React.FC<{l:any;col:string;t:number;fs:number;ent:number}>=({l,col,t,fs,ent})=>{
  const filled=t>=l.fill;
  const since=(t-l.fill)*30;
  const pop=filled?1+0.07*Math.max(0,1-since/7):1;
  const isSerif=l.k==='serif';
  const dots='radial-gradient(rgba(0,0,0,.22) 1.6px, transparent 2.2px) 0 0/11px 11px';
  const style:React.CSSProperties={
    fontFamily:isSerif?SERIF:ANTON,fontSize:fs,lineHeight:isSerif?1.05:0.96,letterSpacing:isSerif?0:'0.01em',
    whiteSpace:'nowrap',textAlign:'center',transform:`scale(${pop})`,
    textShadow:isSerif?'0 4px 24px rgba(0,0,0,.7), 0 0 40px rgba(0,0,0,.5)':filled?`0 0 50px ${col}55, 0 28px 55px rgba(0,0,0,.5)`:'none',
    opacity:filled?1:0.7,
  };
  if(isSerif){style.color=filled?'#fff':'rgba(255,255,255,.75)';style.fontStyle='italic';}
  else if(filled){style.background=`${dots}, linear-gradient(${col},${col})`;style.WebkitBackgroundClip='text';style.backgroundClip='text';style.color='transparent';style.filter=`drop-shadow(0 22px 34px rgba(0,0,0,.45))`;}
  else {style.color='transparent';(style as any).WebkitTextStroke=`3px ${col}`;}
  return <div style={style}>{l.t}</div>;
};

export const Back:React.FC=()=>{
  const ok=useFonts();const frame=useCurrentFrame();const t=frame/30;
  if(!ok) return null;
  return <AbsoluteFill>
    {P.back.map((b:any)=>{
      const s=b.s*30,e=b.e*30; if(frame<s||frame>e) return null;
      const f=frame-s;
      const sp=spring({frame:f,fps:30,config:{damping:16,stiffness:120,mass:.8}});
      const exitP=clamp((frame-(e-6))/6);
      const dur=e-s, prog=f/dur;
      const sc=(0.82+0.18*sp)*(1+0.04*prog)*(1-0.04*exitP);
      const blur=(1-clamp(f/8))*22+exitP*10;
      const dy=-40*prog+ (1-sp)*40 - exitP*30;
      const op=clamp(f/5)*(1-exitP);
      const col=COL[b.c];
      return <div key={b.id} style={{position:'absolute',left:0,width:1080,top:b.y,transform:`translateY(-50%) translateY(${dy}px) scale(${sc})`,opacity:op,filter:`blur(${blur}px)`,display:'flex',flexDirection:'column',alignItems:'center',gap:6}}>
        {b.lines.map((l:any,i:number)=>{
          const isS=l.k==='serif';
          const frac=isS?Math.min(0.95,(l.scale??1)*2.2):(l.scale??1);
          const w=920*frac;
          const fs=Math.min(isS?170:360,fitText({text:l.t,withinWidth:w,fontFamily:isS?SERIF:ANTON,fontStyle:isS?'italic':'normal'}).fontSize);
          return <Line key={i} l={l} col={col} t={t} fs={fs} ent={sp}/>;
        })}
      </div>;
    })}
  </AbsoluteFill>;
};
