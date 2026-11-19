import React from 'react';
import {Composition} from 'remotion';
import {Back} from './Back';
import {Front} from './Front';
export const Root:React.FC=()=>{
  const common={width:1080,height:1920,fps:30,durationInFrames:501} as const;
  return <><Composition id="Back" component={Back} {...common}/><Composition id="Front" component={Front} {...common}/></>;
};
