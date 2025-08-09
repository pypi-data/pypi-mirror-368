import * as React from 'react';
import CallMergeIcon from '@mui/icons-material/CallMerge';
import CallSplitIcon from '@mui/icons-material/CallSplit';
import ImageIcon from '@mui/icons-material/Image';
import { SxProps } from '@mui/material/styles';
import { INodeInnerDefaultProps } from '@mrblenny/react-flow-chart';

function SpecialCellIcon({ nodeType, sx }: { nodeType: string; sx: SxProps }) {
  switch (nodeType) {
    case 'splitter':
      return <CallSplitIcon sx={{ transform: 'rotate(90deg)', ...sx }} />;
    case 'merger':
      return <CallMergeIcon sx={{ transform: 'rotate(90deg)', ...sx }} />;
    case 'visualizer':
      return <ImageIcon sx={sx} />;
    default:
      return <></>;
  }
}

export function NodeInnerCustom({ node }: INodeInnerDefaultProps) {
  return (
    <div
      style={{
        width: '190px',
        padding: '5px',
        display: 'flex',
        justifyContent: 'center'
      }}
    >
      <SpecialCellIcon nodeType={node.type} sx={{ fontSize: '50px' }} />
    </div>
  );
}
