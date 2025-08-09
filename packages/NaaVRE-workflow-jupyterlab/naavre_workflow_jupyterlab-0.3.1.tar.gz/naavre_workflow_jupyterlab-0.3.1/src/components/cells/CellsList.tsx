import React, { ReactNode } from 'react';

import { ICell } from '../../naavre-common/types/NaaVRECatalogue/WorkflowCells';
import { CellNode } from './CellNode';

export function CellsList({
  title,
  cells,
  minHeightInCells,
  selectedCellInList,
  setSelectedCell,
  button,
  filter,
  pageNav
}: {
  title: string;
  cells: Array<ICell>;
  minHeightInCells?: number;
  selectedCellInList: ICell | null;
  setSelectedCell: (c: ICell | null, n: HTMLDivElement | null) => void;
  button?: ReactNode;
  filter?: ReactNode;
  pageNav?: ReactNode;
}) {
  // CellNode height (height + padding + border) and margin, as defined in ./CellNode
  const cellNodeHeight = 25 + 20 + 2;
  const cellNodeMargin = 10;
  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          minHeight: '40px',
          paddingRight: '10px',
          paddingLeft: '10px',
          background: '#3c8f49',
          color: 'white',
          fontSize: 'medium'
        }}
      >
        <span
          style={{
            overflow: 'hidden',
            textOverflow: 'ellipsis'
          }}
        >
          {title}
        </span>
        {button && button}
      </div>
      {filter && filter}
      <div
        style={{
          minHeight: minHeightInCells
            ? minHeightInCells * (cellNodeHeight + cellNodeMargin)
            : undefined
        }}
      >
        {cells.map(cell => (
          <CellNode
            cell={cell}
            selectedCellInList={selectedCellInList}
            setSelectedCell={setSelectedCell}
          />
        ))}
      </div>
      {pageNav && pageNav}
    </div>
  );
}
