import React, { CSSProperties, ForwardedRef } from 'react';
import styled from 'styled-components';
import Tooltip from '@mui/material/Tooltip';
import { INodeDefaultProps } from '@mrblenny/react-flow-chart';

const NodeContainer = styled.div<{ width?: string; height?: string }>`
  position: absolute;
  background: white;
  width: ${props => props.width || '250px'};
  height: ${props => props.height || '150px'};
  border-radius: 5px;
  border: 1px solid lightgray;
`;

function NodeTitle({
  title,
  backgroundColor
}: {
  title: string;
  backgroundColor: CSSProperties['color'];
}) {
  return (
    <Tooltip title={title} placement="bottom" arrow>
      <div
        style={{
          borderTopLeftRadius: '5px',
          borderTopRightRadius: '5px',
          padding: '5px',
          textAlign: 'center',
          backgroundColor: backgroundColor
        }}
      >
        <div
          style={{
            fontSize: 'small',
            display: 'inline-block',
            maxWidth: '200px',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis'
          }}
        >
          {title}
        </div>
      </div>
    </Tooltip>
  );
}

function NodeCustomElement(
  { node, children, ...otherProps }: INodeDefaultProps,
  ref: ForwardedRef<HTMLDivElement>
) {
  const is_special_node = node.type !== 'workflow-cell';

  let width = '250px';
  let height = '150px';
  if (node.type === 'splitter' || node.type === 'merger') {
    width = '200px';
    height = '100px';
  } else if (node.type === 'visualizer') {
    width = '200px';
    height = '250px';
  }

  return (
    <NodeContainer width={width} height={height} ref={ref} {...otherProps}>
      <NodeTitle
        title={node.properties.cell.title}
        backgroundColor={
          is_special_node ? 'rgb(195, 235, 202)' : 'rgb(229,252,233)'
        }
      />
      {children}
    </NodeContainer>
  );
}

export const NodeCustom = React.forwardRef(
  (
    { node, children, ...otherProps }: INodeDefaultProps,
    ref: ForwardedRef<HTMLDivElement>
  ) => {
    return NodeCustomElement({ node, children, ...otherProps }, ref);
  }
);
