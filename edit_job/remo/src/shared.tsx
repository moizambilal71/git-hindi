import React,{useEffect,useState} from 'react';
import {continueRender,delayRender,staticFile,useCurrentFrame} from 'remotion';
import plan from './plan.json';
export const P:any=plan;
export const COL:Record<string,string>={lime:'#FF8733',cyan:'#EA6513',white:'#FFFFFF',red:'#FFFFFF'};
export const ANTON='AntonX', SERIF='SerifX', INTER='InterX', MONO='MonoX';
export const useFonts=()=>{
  const [h]=useState(()=>delayRender('fonts'));
  const [ok,setOk]=useState(false);
  useEffect(()=>{
    (async()=>{
      const list:[string,string,string][]=[[ANTON,'anton-latin-400-normal.woff2','normal'],[SERIF,'instrument-serif-latin-400-italic.woff2','italic'],[INTER,'inter-latin-800-normal.woff2','normal'],[MONO,'jetbrains-mono-latin-700-normal.woff2','normal']];
      for(const [n,f,s] of list){const ff=new FontFace(n,`url(${staticFile(f)})`,{style:s});await ff.load();document.fonts.add(ff);}
      setOk(true);continueRender(h);
    })();
  },[h]);
  return ok;
};
export const ease=(t:number)=>t<0?0:t>1?1:1-Math.pow(1-t,3);
export const easeIO=(t:number)=>t<0?0:t>1?1:t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
export const clamp=(v:number,a=0,b=1)=>Math.max(a,Math.min(b,v));
export const useSec=()=>useCurrentFrame()/30;
