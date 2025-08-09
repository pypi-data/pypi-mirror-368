import React from 'react';
import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';

import {
  getPageNumberAndCount,
  ICellsCatalogueResponse
} from '../../utils/catalog';

export function PageNav({
  cellsListResponse,
  setCellsListUrl
}: {
  cellsListResponse: ICellsCatalogueResponse;
  setCellsListUrl: (u: string | null) => void;
}) {
  const [currentPage, pageCount] = getPageNumberAndCount(cellsListResponse);
  return (
    <Stack
      direction="row"
      spacing={1}
      sx={{
        justifyContent: 'center',
        alignItems: 'center'
      }}
    >
      <IconButton
        aria-label="Previous"
        style={{ borderRadius: '100%' }}
        onClick={() => setCellsListUrl(cellsListResponse.previous)}
        sx={{
          visibility: cellsListResponse.previous === null ? 'hidden' : 'visible'
        }}
      >
        <NavigateBeforeIcon />
      </IconButton>
      <p>
        Page {currentPage} of {pageCount}
      </p>
      <IconButton
        aria-label="Next"
        style={{ borderRadius: '100%' }}
        onClick={() => setCellsListUrl(cellsListResponse.next)}
        sx={{
          visibility: cellsListResponse.next === null ? 'hidden' : 'visible'
        }}
      >
        <NavigateNextIcon />
      </IconButton>
    </Stack>
  );
}
