import React, { CSSProperties, ReactNode } from 'react';
import Tooltip from '@mui/material/Tooltip';
import { IPortDefaultProps } from '@mrblenny/react-flow-chart';

function PortDot({ color }: { color: CSSProperties['color'] }) {
  return (
    <div
      style={{
        width: '20px',
        height: '20px',
        background: color,
        borderRadius: '50%',
        cursor: 'pointer'
      }}
    />
  );
}

function PortDotSpecial() {
  return (
    <div
      style={{
        marginTop: '20px',
        width: '20px',
        height: '20px',
        background: '#3c8f49',
        borderRadius: '5px',
        cursor: 'pointer'
      }}
    />
  );
}

function PortLabel({ children }: { children: ReactNode }) {
  return (
    <div
      style={{
        display: 'inline-block',
        maxWidth: '100px',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        marginLeft: '5px',
        marginRight: '5px'
      }}
    >
      {children}
    </div>
  );
}

export const PortCustom = (props: IPortDefaultProps) => {
  if (
    props.port.properties.parentNodeType === 'splitter' ||
    props.port.properties.parentNodeType === 'merger'
  ) {
    return <PortDotSpecial />;
  }

  return (
    <Tooltip title={props.port.id} placement="bottom" arrow>
      <div
        style={{
          display: 'flex',
          justifyContent: props.port.type === 'left' ? 'flex-start' : 'flex-end'
        }}
      >
        {props.port.type === 'right' && <PortLabel>{props.port.id}</PortLabel>}
        <PortDot color={props.port.properties.color} />
        {props.port.type === 'left' && <PortLabel>{props.port.id}</PortLabel>}
      </div>
    </Tooltip>
  );
};
