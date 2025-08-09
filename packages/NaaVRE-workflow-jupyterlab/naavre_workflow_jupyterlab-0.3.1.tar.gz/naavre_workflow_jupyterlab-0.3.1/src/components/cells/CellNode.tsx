import React, { ReactNode, useEffect, useRef, useState } from 'react';
import IconButton from '@mui/material/IconButton';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { REACT_FLOW_CHART } from '@mrblenny/react-flow-chart';

import { ICell } from '../../naavre-common/types/NaaVRECatalogue/WorkflowCells';
import { ISpecialCell } from '../../utils/specialCells';
import { cellToChartNode } from '../../utils/chart';
import Tooltip from '@mui/material/Tooltip';

function CellTitle({ cell }: { cell: ICell | ISpecialCell }) {
  const [isOverflowed, setIsOverflow] = useState(false);
  const ref = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    ref.current &&
      setIsOverflow(ref.current.scrollWidth > ref.current.clientWidth);
  }, []);

  let title: ReactNode;
  const regex = new RegExp(`-${cell.owner}$`);
  if (cell.owner && cell.title.match(regex)) {
    title = (
      <>
        {cell.title.replace(regex, '')}
        <span style={{ color: '#6c6c6c' }}>-{cell.owner}</span>
      </>
    );
  } else {
    title = cell.title;
  }
  return (
    <Tooltip
      title={cell.title}
      disableHoverListener={!isOverflowed}
      placement="bottom"
      arrow
    >
      <span
        ref={ref}
        style={{
          overflow: 'hidden',
          whiteSpace: 'nowrap',
          textOverflow: 'ellipsis'
        }}
      >
        {title}
      </span>
    </Tooltip>
  );
}

export function CellNode({
  cell,
  selectedCellInList,
  setSelectedCell
}: {
  cell: ICell | ISpecialCell;
  selectedCellInList: ICell | null;
  setSelectedCell: (c: ICell | null, n: HTMLDivElement | null) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const node = cellToChartNode(cell);
  const is_special_node = node.type !== 'workflow-cell';

  function onClick() {
    selectedCellInList === cell
      ? setSelectedCell(null, null)
      : setSelectedCell(cell, ref.current || null);
  }

  return (
    <div
      ref={ref}
      onClick={onClick}
      draggable={true}
      onDragStart={(event: any) => {
        event.dataTransfer.setData(
          REACT_FLOW_CHART,
          JSON.stringify({
            type: node.type,
            ports: node.ports,
            properties: node.properties
          })
        );
      }}
      style={{
        margin: '10px',
        fontSize: '14px',
        display: 'flex',
        height: '25px',
        border: '1px solid lightgray',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgb(195, 235, 202)',
        backgroundColor: is_special_node
          ? 'rgb(195, 235, 202)'
          : 'rgb(229,252,233)',
        borderRadius: '5px',
        padding: '10px',
        cursor: 'move'
      }}
    >
      <CellTitle cell={cell} />
      <IconButton aria-label="Info" style={{ borderRadius: '100%' }}>
        <InfoOutlinedIcon />
      </IconButton>
    </div>
  );
}
