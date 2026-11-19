import React from 'react';
import {AbsoluteFill,spring,useCurrentFrame,random,Img,staticFile} from 'remotion';
import {P,COL,ANTON,INTER,MONO,SERIF,useFonts,ease,easeIO,clamp} from './shared';

const ICONS:Record<string,React.ReactNode>={
  scooter:<><circle cx="6" cy="17" r="2.6"/><circle cx="18.5" cy="17" r="2.6"/><path d="M8.6 17h7.3M16 17l-2.4-9.5H10.5M13.2 7.5h3.6l1.9 9.5M4 12h5.5"/></>,
  chef:<><path d="M7 13.5V20h10v-6.5"/><path d="M7 13.5a4 4 0 0 1-.6-7.7 4 4 0 0 1 7.2-.6 4 4 0 0 1 3.4 8.3"/><path d="M7 17h10"/></>,
  phone:<><rect x="7" y="2.5" width="10" height="19" rx="2.4"/><path d="M10.5 5h3"/><path d="M9.5 15.5c0-3 5-1 5-5"/><circle cx="14.5" cy="9.8" r=".9"/></>,
  shield:<><path d="M12 3l7.5 3v5.3c0 4.4-3.2 8-7.5 9.7-4.3-1.700-7.5-5.300-7.500-9.700V6z"/></>,
  wheel:<><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.2"/><path d="M3.200 10.500l6.600.8M20.800 10.500l-6.600.8M12 14.200V21"/></>,
};
const useLocal=(s:number,e:number)=>{
  const frame=useCurrentFrame();const S=s*30,E=e*30;
  const f=frame-S;const vis=frame>=S&&frame<=E;
  const pop=spring({frame:f,fps:30,config:{damping:9,stiffness:150,mass:.7}});
  const exitP=clamp((frame-(E-6))/6);
  return {frame,f,vis,pop,exitP,sc:(Math.max(0,pop))*(1-0.35*easeIO(exitP)),op:clamp(f/3)*(1-exitP),blur:exitP*10};
};
const Glass:React.FC<{w:number;h:number;col:string;tilt:[number,number];s:number;e:number;x:number;y:number;children:React.ReactNode;glow?:number}>=({w,h,col,tilt,s,e,x,y,children,glow=1})=>{
  const L=useLocal(s,e);if(!L.vis) return null;
  const t=L.frame/30;
  const fl=Math.sin(t*2.6)*10;
  const rx=tilt[0]+Math.sin(t*1.7)*2.5,ry=tilt[1]+Math.cos(t*1.3)*3;
  const sweep=((L.frame%60)/60)*260-80;
  return <div style={{position:'absolute',left:x,top:y,width:w,height:h,perspective:1000,opacity:L.op,filter:`blur(${L.blur}px)`}}>
    <div style={{position:'relative',width:'100%',height:'100%',transformStyle:'preserve-3d',transform:`translateY(${fl}px) rotateX(${rx}deg) rotateY(${ry}deg) scale(${L.sc})`}}>
      <div style={{position:'absolute',inset:0,borderRadius:38,transform:'translate(9px,12px)',background:'rgba(255,255,255,.14)',border:'1.5px solid rgba(255,255,255,.22)'}}/>
      <div style={{position:'absolute',inset:0,borderRadius:38,overflow:'hidden',background:'linear-gradient(145deg, rgba(255,255,255,.36), rgba(255,255,255,.10) 52%, rgba(255,255,255,.2)), rgba(8,10,14,.58)',border:'2px solid rgba(255,255,255,.45)',boxShadow:`0 36px 70px rgba(0,0,0,.38), 0 10px 20px rgba(0,0,0,.28), inset 0 2px 0 rgba(255,255,255,.6), 0 0 ${70*glow}px ${col}44`}}>
        <div style={{position:'absolute',top:-40,bottom:-40,left:`${sweep}%`,width:'22%',transform:'skewX(-20deg)',background:'linear-gradient(90deg,transparent,rgba(255,255,255,.38),transparent)'}}/>
        <div style={{position:'absolute',left:0,top:0,right:0,height:'46%',background:'linear-gradient(180deg,rgba(255,255,255,.22),transparent)'}}/>
        {children}
      </div>
    </div>
  </div>;
};
const Label:React.FC<{text:string;s:number;e:number;x:number;y:number;col:string;w?:number}>=({text,s,e,x,y,col,w})=>{
  const L=useLocal(s+0.08,e);if(!L.vis) return null;
  return <div style={{position:'absolute',left:x,top:y,width:w,transform:`translateY(${(1-ease(L.f/8))*18}px)`,opacity:L.op}}>
    <div style={{display:'inline-flex',alignItems:'center',gap:12,padding:'12px 22px',borderRadius:40,background:'rgba(8,10,12,.72)',border:'1.5px solid rgba(255,255,255,.28)',fontFamily:INTER,fontSize:27,letterSpacing:1.5,color:'#fff',boxShadow:'0 10px 26px rgba(0,0,0,.35)'}}>
      <span style={{width:13,height:13,borderRadius:7,background:col,boxShadow:`0 0 14px ${col}`}}/>{text}
    </div>
  </div>;
};
const InLabel:React.FC<{text:string;col:string}>=({text,col})=>(
  <div style={{position:'absolute',left:0,right:0,bottom:20,display:'flex',justifyContent:'center',alignItems:'center',gap:9,fontFamily:INTER,fontSize:21,letterSpacing:1.2,color:'#fff'}}>
    <span style={{width:11,height:11,borderRadius:6,background:col,boxShadow:`0 0 12px ${col}`}}/>{text}
  </div>);
const Icon:React.FC<{name:string;col:string;size:number}>=({name,col,size})=>
  <svg viewBox="0 0 24 24" width={size} height={size} fill="none" stroke={col} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" style={{filter:`drop-shadow(0 0 14px ${col}99)`}}>{ICONS[name]}</svg>;

const Tile:React.FC<{o:any}>=({o})=>{
  const col=COL[o.col];const frame=useCurrentFrame();
  const chk=o.check?clamp((frame-o.check*30)/10):0;
  const strike=o.strike?clamp((frame-o.strike*30)/6):0;
  const sz=o.size;
  const hot=o.check||o.strike? 1:1;
  return <>
    <Glass w={sz} h={sz} col={col} tilt={o.tilt} s={o.s} e={o.e} x={o.x} y={o.y}>
      <InLabel text={o.label} col={o.strike&&strike>0?COL.red:col}/>
      <div style={{position:'absolute',left:0,right:0,top:0,bottom:46,display:'flex',alignItems:'center',justifyContent:'center'}}>
        <div style={{position:'relative'}}>
          <Icon name={o.icon} col={col} size={sz*0.52}/>
          {o.check!==undefined&&<svg viewBox="0 0 24 24" width={sz*0.52} height={sz*0.52} style={{position:'absolute',left:0,top:0}} fill="none" stroke={col} strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round"><path d="M8 12.2l2.8 2.8L16.4 9.2" strokeDasharray={20} strokeDashoffset={20*(1-ease(chk))} style={{filter:`drop-shadow(0 0 10px ${col})`}}/></svg>}
          {o.strike!==undefined&&<svg viewBox="0 0 24 24" width={sz*0.52} height={sz*0.52} style={{position:'absolute',left:0,top:0}} fill="none" stroke={COL.red} strokeWidth={1.9} strokeLinecap="round"><path d="M4.500 19.500L19.500 4.500" strokeDasharray={22} strokeDashoffset={22*(1-ease(strike))} style={{filter:`drop-shadow(0 0 10px ${COL.red})`}}/></svg>}
        </div>
      </div>
    </Glass>
  </>;
};
const Plus:React.FC<{o:any}>=({o})=>{
  const L=useLocal(o.s,o.e);if(!L.vis) return null;
  return <div style={{position:'absolute',left:o.x,top:o.y,width:110,height:110,borderRadius:55,transform:`translate(-50%,-50%) scale(${L.sc}) rotate(${(1-clamp(L.f/12))*-90}deg)`,opacity:L.op,background:COL.lime,boxShadow:`0 0 50px ${COL.lime}aa, 0 14px 30px rgba(0,0,0,.4)`,display:'flex',alignItems:'center',justifyContent:'center'}}>
    <svg width="60" height="60" viewBox="0 0 24 24" stroke="#0A0D10" strokeWidth="3.4" strokeLinecap="round"><path d="M12 4v16M4 12h16"/></svg>
  </div>;
};
const Route:React.FC<{o:any}>=({o})=>{
  const col=COL[o.col];const frame=useCurrentFrame();const f=frame-o.s*30;
  const w=o.size,h=o.size*1.1;
  const P0=[60,h-110],P1=[30,h*0.4],P2=[w-30,h*0.6],P3=[w-60,70];
  const bz=(t:number,i:number)=>{const u=1-t;return u*u*u*P0[i]+3*u*u*t*P1[i]+3*u*t*t*P2[i]+t*t*t*P3[i];};
  const draw=ease(clamp((f-4)/18));
  const pts=Array.from({length:41},(_,k)=>[bz(k/40*draw,0),bz(k/40*draw,1)]);
  const d='M'+pts.map(p=>p.join(' ')).join(' L');
  const car=[bz(draw,0),bz(draw,1)];
  const pin=(p:number[],c:string,k:number)=>{const sp=spring({frame:f-k,fps:30,config:{damping:8,stiffness:160}});return <g transform={`translate(${p[0]} ${p[1]}) scale(${Math.max(0,sp)})`}><circle r="26" fill={c} opacity=".25"/><circle r="14" fill={c}/><circle r="5.500" fill="#0A0D10"/></g>;};
  return <>
    <Glass w={w} h={h} col={col} tilt={[-8,14]} s={o.s} e={o.e} x={o.x} y={o.y}>
      <svg width={w} height={h} style={{position:'absolute',inset:0}}>
        {Array.from({length:6}).map((_,i)=><line key={i} x1={0} x2={w} y1={50+i*h/6} y2={50+i*h/6} stroke="rgba(255,255,255,.10)"/>)}
        {Array.from({length:5}).map((_,i)=><line key={i} y1={0} y2={h} x1={50+i*w/5} x2={50+i*w/5} stroke="rgba(255,255,255,.10)"/>)}
        <path d={d} fill="none" stroke={col} strokeWidth={8} strokeLinecap="round" strokeDasharray="1 0" style={{filter:`drop-shadow(0 0 12px ${col})`}}/>
        <path d={d} fill="none" stroke="#fff" strokeWidth={3} strokeLinecap="round" strokeDasharray="4 16" strokeDashoffset={-frame*2} opacity=".8"/>
        {pin(P0,'#fff',0)}{pin(P3,col,14)}
        {draw>0.02&&<circle cx={car[0]} cy={car[1]} r={11} fill="#fff" style={{filter:`drop-shadow(0 0 12px ${col})`}}/>}
      </svg>
    </Glass>
  </>;
};
const Ring:React.FC<{o:any}>=({o})=>{
  const col=COL[o.col];const frame=useCurrentFrame();
  const p=easeIO(clamp((frame-o.fillStart*30)/((o.fillEnd-o.fillStart)*30)));
  const sz=o.size,r=sz*0.3,c=2*Math.PI*r;
  const done=p>=1;const since=frame-o.fillEnd*30;
  const pulse=done?1+0.08*Math.max(0,1-since/8):1;
  return <>
    <Glass w={sz} h={sz} col={col} tilt={[-8,14]} s={o.s} e={o.e} x={o.x} y={o.y} glow={done?2:1}>
      <svg width={sz} height={sz} style={{position:'absolute',inset:0,transform:`scale(${pulse})`}}>
        <circle cx={sz/2} cy={sz/2} r={r} fill="none" stroke="rgba(255,255,255,.2)" strokeWidth={18}/>
        <circle cx={sz/2} cy={sz/2} r={r} fill="none" stroke={col} strokeWidth={18} strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c*(1-p)} transform={`rotate(-90 ${sz/2} ${sz/2})`} style={{filter:`drop-shadow(0 0 14px ${col})`}}/>
        <text x={sz/2} y={sz/2+10} textAnchor="middle" fontFamily={ANTON} fontSize={sz*0.19} fill="#fff">{Math.round(p*100)}%</text>
      </svg>
      <InLabel text="PROBLEMS SOLVED" col={col}/>
    </Glass>
  </>;
};
const Cta:React.FC<{o:any}>=({o})=>{
  const L=useLocal(o.s,o.e);if(!L.vis) return null;
  const pulse=1+0.025*Math.sin(L.f/30*Math.PI*2*1.3);
  const sweep=((L.f%50)/50)*140-20;
  return <>
    <div style={{position:'absolute',left:540-520,top:o.y+o.h/2-520,width:1040,height:1040,borderRadius:'50%',background:`radial-gradient(circle, ${COL.lime}55 0%, ${COL.lime}00 62%)`,opacity:L.op*clamp(L.f/10)}}/>
    <div style={{position:'absolute',left:o.x,top:o.y,width:o.w,height:o.h,opacity:L.op,filter:`blur(${L.blur}px)`,transform:`scale(${L.sc*pulse}) translateY(${(1-ease(L.f/10))*60}px)`}}>
      <div style={{position:'relative',width:'100%',height:'100%',borderRadius:o.h/2,overflow:'hidden',background:`linear-gradient(180deg,#FFB070,${COL.lime} 55%,#EF6B16)`,boxShadow:`0 0 70px ${COL.lime}88, 0 26px 50px rgba(0,0,0,.45), inset 0 3px 0 rgba(255,255,255,.7)`,display:'flex',alignItems:'center',justifyContent:'center',gap:26}}>
        <div style={{position:'absolute',top:0,bottom:0,left:`${sweep}%`,width:'18%',transform:'skewX(-20deg)',background:'linear-gradient(90deg,transparent,rgba(255,255,255,.6),transparent)'}}/>
        <span style={{fontFamily:ANTON,fontSize:68,color:'#0A0D10',letterSpacing:1.5}}>USE DABBA UNCLE PARTNER</span>
        <svg width="62" height="62" viewBox="0 0 24 24" fill="none" stroke="#0A0D10" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg>
      </div>
    </div>
  </>;
};
const Logo:React.FC<{o:any}>=({o})=>{
  const L=useLocal(o.s,o.e);if(!L.vis) return null;
  const pulse=1+0.04*Math.sin(L.f/30*Math.PI*2*1.2);
  return <div style={{position:'absolute',left:o.x,top:o.y,width:o.size,height:o.size,opacity:L.op,filter:`blur(${L.blur}px)`,transform:`scale(${L.sc*pulse})`}}>
    <div style={{position:'absolute',inset:-40,borderRadius:'50%',background:`radial-gradient(circle, ${COL.lime}88, ${COL.lime}00 70%)`}}/>
    <div style={{position:'relative',width:'100%',height:'100%',borderRadius:'50%',overflow:'hidden',background:'#fff',border:'4px solid #fff',boxShadow:`0 0 50px ${COL.lime}99, 0 20px 40px rgba(0,0,0,.4)`}}>
      <Img src={staticFile('logo.jpg')} style={{position:'absolute',left:'-2%',top:'-2%',width:'104%',height:'104%',objectFit:'cover'}}/>
    </div>
  </div>;
};
const Captions:React.FC=()=>{
  const frame=useCurrentFrame();const t=frame/30;
  const g=P.captions.find((c:any)=>t>=c.s&&t<c.e);if(!g) return null;
  const f=frame-g.s*30;
  const nch=g.words.map((w:any)=>w.w).join(' ').length;const cfs=Math.min(104,Math.floor(900/(nch*0.47)));
  return <div style={{position:'absolute',left:60,right:140,top:1480,display:'flex',justifyContent:'center',flexWrap:'nowrap',gap:'4px 22px',transform:`translateY(${(1-ease(f/5))*22}px)`,opacity:clamp(f/3)}}>
    {g.words.map((w:any,i:number)=>{
      const act=t>=w.s&&t<w.e+0.0001; const past=t>=w.e;
      const since=(t-w.s)*30; const pop=act?1+0.14*Math.max(0,1-since/6):1;
      return <span key={i} style={{fontFamily:ANTON,fontSize:cfs,textTransform:'uppercase',color:act?COL.lime:'#fff',opacity:t<w.s?0.55:1,WebkitTextStroke:'11px #0A0D10',paintOrder:'stroke fill',transform:`scale(${pop})`,textShadow:act?`0 0 30px ${COL.lime}88`:'0 8px 18px rgba(0,0,0,.5)',letterSpacing:2,display:'inline-block'}}>{w.w.replace(/[,]/g,'')}</span>;
    })}
  </div>;
};
const Trans:React.FC=()=>{
  const frame=useCurrentFrame();
  return <>{P.transitions.map((tr:any)=>{
    const f=frame-Math.round(tr.t*30);const N=9; if(f<0||f>=N) return null;
    const p=f/(N-1);
    if(tr.k==='glass'){
      const x=-700+p*2500;
      return <div key={tr.k} style={{position:'absolute',top:-100,bottom:-100,left:x,width:520,transform:'skewX(-18deg)',background:`linear-gradient(90deg, transparent, ${COL.lime}66 35%, rgba(255,255,255,.7) 50%, ${COL.lime}66 65%, transparent)`,borderLeft:'2px solid rgba(255,255,255,.6)',borderRight:'2px solid rgba(255,255,255,.6)'}}/>;
    }
    if(tr.k==='halftone'){
      const r=21*Math.sin(Math.PI*p);
      return <svg key={tr.k} width="1080" height="1920" style={{position:'absolute',inset:0,opacity:.95}}><defs><pattern id="ht" width="42" height="42" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><circle cx="21" cy="21" r={Math.max(0,r)} fill={COL.cyan}/></pattern></defs><rect width="1080" height="1920" fill="url(#ht)"/></svg>;
    }
    if(tr.k==='pixel'){
      const S=120,cols=9,rows=16;
      return <>{Array.from({length:cols*rows}).map((_,i)=>{
        const th=random('px'+i)*0.55;const on=clamp((p-th)/0.18)*(1-clamp((p-th-0.3)/0.18));
        if(on<=0) return null;
        return <div key={i} style={{position:'absolute',left:(i%cols)*S,top:Math.floor(i/cols)*S,width:S,height:S,background:i%3?COL.lime:'#fff',opacity:on*.9,transform:`scale(${.5+.5*on})`}}/>;
      })}</>;
    }
    return null;
  })}</>;
};
export const Front:React.FC=()=>{
  const ok=useFonts();const frame=useCurrentFrame();
  if(!ok) return null;
  const prog=frame/(P.duration*30);
  return <AbsoluteFill>
    {P.front.map((o:any)=>{
      if(o.type==='tile') return <Tile key={o.id} o={o}/>;
      if(o.type==='plus') return <Plus key={o.id} o={o}/>;
      if(o.type==='route') return <Route key={o.id} o={o}/>;
      if(o.type==='ring') return <Ring key={o.id} o={o}/>;
      if(o.type==='cta') return <Cta key={o.id} o={o}/>;
      if(o.type==='logo') return <Logo key={o.id} o={o}/>;
      return null;
    })}
    <Trans/>
    <Captions/>
    <div style={{position:'absolute',left:150,top:96,width:780,height:6,borderRadius:3,background:'rgba(255,255,255,.22)'}}><div style={{width:`${prog*100}%`,height:'100%',borderRadius:3,background:COL.lime,boxShadow:`0 0 12px ${COL.lime}`}}/></div>
  </AbsoluteFill>;
};
