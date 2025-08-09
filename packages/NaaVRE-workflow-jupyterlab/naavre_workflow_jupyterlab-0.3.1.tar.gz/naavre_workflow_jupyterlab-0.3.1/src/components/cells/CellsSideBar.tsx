import React, { useCallback, useEffect, useState } from 'react';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import RefreshIcon from '@mui/icons-material/Refresh';

import { ICell } from '../../naavre-common/types/NaaVRECatalogue/WorkflowCells';
import { specialCells } from '../../utils/specialCells';
import {
  getCellsFromCatalogue,
  ICellsCatalogueResponse
} from '../../utils/catalog';
import { CellsList } from './CellsList';
import { PageNav } from './PageNav';
import { ListFilter } from './ListFilter';
import { IWorkflowWidgetSettings } from '../../widget';

export function CellsSideBar({
  settings,
  selectedCellInList,
  setSelectedCell
}: {
  settings: IWorkflowWidgetSettings;
  selectedCellInList: ICell | null;
  setSelectedCell: (c: ICell | null, n: HTMLDivElement | null) => void;
}) {
  const defaultQuery = `?ordering=-modified&virtual_lab=${settings.virtualLab}`;

  const [cellsListUrl, setCellsListUrl] = useState<string | null>(
    settings.catalogueServiceUrl
      ? `${settings.catalogueServiceUrl}/workflow-cells/${defaultQuery}`
      : null
  );

  useEffect(() => {
    setCellsListUrl(
      `${settings.catalogueServiceUrl}/workflow-cells/${defaultQuery}`
    );
  }, [settings.catalogueServiceUrl]);

  const [cellsListResponse, setcellsListResponse] =
    useState<ICellsCatalogueResponse>({
      count: 0,
      next: null,
      previous: null,
      results: []
    });

  const getCatalogItems = useCallback((cellsListUrl: string | null) => {
    if (cellsListUrl) {
      getCellsFromCatalogue(cellsListUrl).then(resp =>
        setcellsListResponse(resp)
      );
    }
  }, []);

  useEffect(
    () => getCatalogItems(cellsListUrl),
    [getCatalogItems, cellsListUrl]
  );

  return (
    <Paper
      elevation={12}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: 250,
        height: '100%',
        overflowX: 'hidden',
        overflowY: 'scroll',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 0
      }}
    >
      <CellsList
        title="Cells Catalog"
        cells={cellsListResponse.results}
        minHeightInCells={10}
        selectedCellInList={selectedCellInList}
        setSelectedCell={setSelectedCell}
        button={
          <Tooltip title="Refresh" arrow>
            <IconButton
              aria-label="Reload"
              style={{ color: 'white', borderRadius: '100%' }}
              onClick={() => getCatalogItems(cellsListUrl)}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        }
        filter={<ListFilter url={cellsListUrl} setUrl={setCellsListUrl} />}
        pageNav={
          <PageNav
            cellsListResponse={cellsListResponse}
            setCellsListUrl={setCellsListUrl}
          />
        }
      />
      <CellsList
        title="Special cells"
        cells={specialCells}
        selectedCellInList={selectedCellInList}
        setSelectedCell={setSelectedCell}
      />
    </Paper>
  );
}
