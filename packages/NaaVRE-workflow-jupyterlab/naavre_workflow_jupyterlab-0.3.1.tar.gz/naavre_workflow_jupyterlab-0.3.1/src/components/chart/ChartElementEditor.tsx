import * as React from 'react';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import {
  IChart,
  IConfig,
  IFlowChartCallbacks,
  ILink,
  INode
} from '@mrblenny/react-flow-chart';

import { CellInfo } from '../common/CellInfo';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import { ReactNode } from 'react';

function EditorHeader({
  children,
  onClose
}: {
  children: ReactNode;
  onClose: () => void;
}) {
  return (
    <div
      className="naavre-workflow-section-header"
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}
    >
      <p style={{ margin: '0' }}>{children}</p>
      <IconButton
        aria-label="Close"
        style={{ color: 'white', borderRadius: '100%' }}
        onClick={onClose}
      >
        <CloseIcon />
      </IconButton>
    </div>
  );
}

function LinkEditor({ link, onClose }: { link: ILink; onClose: () => void }) {
  return <EditorHeader onClose={onClose}>Link</EditorHeader>;
}

function NodeEditor({ node, onClose }: { node: INode; onClose: () => void }) {
  let title: string = '';
  switch (node.type) {
    case 'splitter':
      title = 'Splitter';
      break;
    case 'merger':
      title = 'Merger';
      break;
    case 'visualizer':
      title = 'Visualizer';
      break;
    case 'workflow-cell':
      title = node.properties.cell.title;
      break;
  }

  return (
    <>
      <EditorHeader onClose={onClose}>{title}</EditorHeader>
      {node.type === 'workflow-cell' && (
        <CellInfo cell={node.properties.cell} />
      )}
    </>
  );
}

export function ChartElementEditor({
  chart,
  setChart,
  callbacks,
  config
}: {
  chart: IChart;
  setChart: (chart: IChart) => void;
  callbacks: IFlowChartCallbacks;
  config: IConfig;
}) {
  // when no chart element is selected, chart.selected === {}
  if (!chart.selected.id) {
    return <></>;
  }

  function onClose() {
    setChart({
      ...chart,
      selected: {}
    });
  }

  return (
    <Paper
      elevation={6}
      sx={{
        position: 'absolute',
        top: 20,
        right: 20,
        width: 380,
        maxHeight: 'calc(100% - 40px)',
        overflowX: 'clip',
        overflowY: 'scroll'
      }}
    >
      {chart.selected.type === 'link' && (
        <LinkEditor
          link={chart.links[chart.selected.id as string]}
          onClose={onClose}
        />
      )}
      {chart.selected.type === 'node' && (
        <NodeEditor
          node={chart.nodes[chart.selected.id as string]}
          onClose={onClose}
        />
      )}
      <div style={{ margin: '15px' }}>
        <Button
          variant="contained"
          onClick={() => {
            return callbacks.onDeleteKey({ config: config });
          }}
        >
          Delete
        </Button>
      </div>
    </Paper>
  );
}
