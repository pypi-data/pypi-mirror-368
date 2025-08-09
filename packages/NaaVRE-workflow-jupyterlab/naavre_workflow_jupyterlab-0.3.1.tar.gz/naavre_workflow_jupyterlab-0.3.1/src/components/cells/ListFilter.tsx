import React, { useEffect, useState } from 'react';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import { InputAdornment, Menu, MenuItem } from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';
import SearchIcon from '@mui/icons-material/Search';
import SwapVertIcon from '@mui/icons-material/SwapVert';
import IconButton from '@mui/material/IconButton';
import { useDebouncedValue } from '@mantine/hooks';

function updateSearchParams(
  url: string | null,
  params: { [key: string]: string | null }
): string | null {
  if (url === null) {
    return null;
  }
  const newUrl = new URL(url);
  for (const [key, value] of Object.entries(params)) {
    if (value === null || value === '') {
      newUrl.searchParams.delete(key);
    } else {
      newUrl.searchParams.set(key, value);
    }
  }
  return newUrl.toString();
}

function SearchField({
  search,
  setSearch
}: {
  search: string | null;
  setSearch: (v: string | null) => void;
}) {
  return (
    <TextField
      value={search}
      onChange={e => setSearch(e.target.value)}
      slotProps={{
        input: {
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
          endAdornment: search && (
            <InputAdornment position="end">
              <IconButton
                aria-label="clear search"
                onClick={() => setSearch('')}
                edge="end"
                style={{
                  borderRadius: '100%'
                }}
              >
                <ClearIcon />
              </IconButton>
            </InputAdornment>
          )
        }
      }}
      size="small"
      sx={{
        '& .MuiInputBase-root': {
          borderRadius: '100px'
        }
      }}
    />
  );
}

const orderingOptions = [
  { value: 'modified', label: 'First modified' },
  { value: '-modified', label: 'Last modified' },
  { value: 'title', label: 'A-Z' },
  { value: '-title', label: 'Z-A' }
];

function OrderingMenu({
  ordering,
  setOrdering
}: {
  ordering: string | null;
  setOrdering: (v: string | null) => void;
}) {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  return (
    <>
      <IconButton
        id="ordering-button"
        aria-label="ordering"
        aria-controls={open ? 'ordering-menu' : undefined}
        aria-expanded={open ? 'true' : undefined}
        aria-haspopup="true"
        style={{
          borderRadius: '100%'
        }}
        onClick={e => setAnchorEl(e.currentTarget)}
      >
        <SwapVertIcon />
      </IconButton>
      <Menu
        id="ordering-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={() => setAnchorEl(null)}
        slotProps={{
          list: {
            'aria-labelledby': 'ordering-button'
          }
        }}
      >
        {orderingOptions.map(option => (
          <MenuItem
            key={option.value}
            selected={option.value === ordering}
            onClick={() => {
              setOrdering(option.value);
              setAnchorEl(null);
            }}
          >
            {option.label}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}

export function ListFilter({
  url,
  setUrl
}: {
  url: string | null;
  setUrl: (u: string | null) => void;
}) {
  const [search, setSearch] = useState<string | null>(null);
  const [ordering, setOrdering] = useState<string | null>('-modified');

  const [debouncedSearch] = useDebouncedValue(search, 200);

  useEffect(() => {
    const newUrl = updateSearchParams(url, {
      search: debouncedSearch,
      ordering: ordering,
      page: null
    });
    setUrl(newUrl);
  }, [debouncedSearch, ordering]);

  return (
    <Stack
      direction="row"
      spacing={1}
      sx={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: '10px'
      }}
    >
      <SearchField search={search} setSearch={setSearch} />
      <OrderingMenu ordering={ordering} setOrdering={setOrdering} />
    </Stack>
  );
}
