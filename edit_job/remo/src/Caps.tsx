import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {C,Fonts,sp} from './common';
import plan from '../../plan/edit_plan.json';
export const Caps:React.FC=()=>{
  const f=useCurrentFrame();const t=f/30;
  const w=(plan as any).words as [string,number,number][];
  const cur=w.find(x=>t>=x[1]&&t<x[2]+0.02);
  if(!cur)return <AbsoluteFill><Fonts/></AbsoluteFill>;
  const words=cur[0].split(' ');const n=words.length;
  const act=Math.min(n-1,Math.floor((t-cur[1])/(cur[2]-cur[1])*n));
  const st=Math.round(cur[1]*30);
  const pop=sp(f,st,{damping:11,stiffness:200});
  return <AbsoluteFill><Fonts/>
    <div style={{position:'absolute',left:60,right:140,top:1480,display:'flex',flexWrap:'wrap',justifyContent:'center',gap:'0 44px',transform:`scale(${0.9+0.1*pop})`,opacity:Math.min(1,pop*1.5)}}>
      {words.map((x,i)=>{const on=i===act;const wp=on?sp(f,Math.round((cur[1]+(cur[2]-cur[1])*i/n)*30),{damping:9,stiffness:260}):1;
        return <span key={i} style={{fontFamily:'Anton',fontSize:96,lineHeight:1.12,letterSpacing:1,textTransform:'uppercase',color:on?C.red:'#fff',WebkitTextStroke:`7px ${C.ink}`,paintOrder:'stroke fill',textShadow:'0 8px 22px rgba(0,0,0,0.45)',transform:`scale(${on?1+0.14*Math.min(1.3,wp):1})`,display:'inline-block'}}>{x}</span>;})}
    </div></AbsoluteFill>;
};
