import React from 'react';
import {Composition} from 'remotion';
import {Back} from './Back';
import {Front} from './Front';
import {Caps} from './Caps';
import {Top} from './Top';
import {End} from './End';
const D=392;
export const Root:React.FC=()=>{
  const p={durationInFrames:D,fps:30,width:1080,height:1920};
  return <>
    <Composition id="Back" component={Back} {...p}/>
    <Composition id="Front" component={Front} {...p}/>
    <Composition id="Caps" component={Caps} {...p}/>
    <Composition id="Top" component={Top} {...p}/>
    <Composition id="End" component={End} durationInFrames={117} fps={30} width={1080} height={1920}/>
  </>;
};
