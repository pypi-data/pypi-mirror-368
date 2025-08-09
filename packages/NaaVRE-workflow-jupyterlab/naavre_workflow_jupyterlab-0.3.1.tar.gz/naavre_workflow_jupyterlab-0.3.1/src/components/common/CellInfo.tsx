import React, { ReactNode } from 'react';
import Box from '@mui/material/Box';
import Link from '@mui/material/Link';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';

import { ICell } from '../../naavre-common/types/NaaVRECatalogue/WorkflowCells';
import { getVariableColor } from '../../utils/chart';

function PropsTable({
  title,
  children
}: {
  title?: string;
  children: ReactNode;
}) {
  return (
    <>
      {title && (
        <Typography
          component="h4"
          sx={{ marginTop: '16px', marginBottom: '16px' }}
        >
          {title}
        </Typography>
      )}
      <Paper elevation={1}>
        <TableContainer>
          <Table>
            <TableBody>{children}</TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </>
  );
}

function PropsTableRow({ cells }: { cells: Array<ReactNode> }) {
  return (
    <TableRow>
      {cells.map(cell => (
        <TableCell>{cell}</TableCell>
      ))}
    </TableRow>
  );
}

function IOVarDot({ name }: { name: string }) {
  return (
    <div
      style={{
        width: '20px',
        height: '20px',
        background: getVariableColor(name),
        borderRadius: '50%'
      }}
    />
  );
}

export function CellInfo({ cell }: { cell: ICell }) {
  return (
    <Box sx={{ margin: '15px' }}>
      <PropsTable>
        {cell.container_image && (
          <PropsTableRow cells={['Image name', cell.container_image]} />
        )}
        {cell.base_container_image && (
          <>
            <PropsTableRow
              cells={['Base image (build)', cell.base_container_image.build]}
            />
            <PropsTableRow
              cells={[
                'Base image (runtime)',
                cell.base_container_image.runtime
              ]}
            />
          </>
        )}
        {cell.kernel && <PropsTableRow cells={['Kernel', cell.kernel]} />}
        {cell.source_url && (
          <PropsTableRow
            cells={[
              'Source',
              <Link href={cell.source_url} target="_blank" rel="noreferrer">
                {cell.source_url}
              </Link>
            ]}
          />
        )}
      </PropsTable>

      {cell.inputs.length > 0 && (
        <>
          <PropsTable title="Inputs">
            {cell.inputs.map(v => (
              <PropsTableRow
                cells={[<IOVarDot name={v.name} />, v.name, v.type]}
              />
            ))}
          </PropsTable>
        </>
      )}

      {cell.outputs.length > 0 && (
        <>
          <PropsTable title="Outputs">
            {cell.outputs.map(v => (
              <PropsTableRow
                cells={[<IOVarDot name={v.name} />, v.name, v.type]}
              />
            ))}
          </PropsTable>
        </>
      )}

      {cell.params.length > 0 && (
        <>
          <PropsTable title="Parameters">
            {cell.params.map(v => (
              <PropsTableRow cells={[v.name, v.type, v.default_value]} />
            ))}
          </PropsTable>
        </>
      )}

      {cell.secrets.length > 0 && (
        <>
          <PropsTable title="Secrets">
            {cell.secrets.map(v => (
              <PropsTableRow cells={[v.name]} />
            ))}
          </PropsTable>
        </>
      )}
    </Box>
  );
}
