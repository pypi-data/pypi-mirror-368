import React, { ChangeEvent, useEffect, useState } from 'react';
import AutoModeIcon from '@mui/icons-material/AutoMode';
import Button from '@mui/material/Button';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import Stack from '@mui/material/Stack';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableRow from '@mui/material/TableRow';
import TextField from '@mui/material/TextField';
import { green } from '@mui/material/colors';
import { grey } from '@mui/material/colors';
import { ThemeProvider } from '@mui/material/styles';
import { IChart } from '@mrblenny/react-flow-chart';

import {
  IParam,
  ISecret
} from '../../naavre-common/types/NaaVRECatalogue/WorkflowCells';
import { NaaVREExternalService } from '../../naavre-common/handler';
import { theme } from '../../Theme';
import { IWorkflowWidgetSettings } from '../../widget';
import WorkflowRepeatPicker from '../WorkflowRepeatPicker';

interface IParamValue {
  value: string | null;
  default_value?: string;
}

interface ISecretValue {
  value: string | null;
}

export function RunWorkflowDialog({
  chart,
  settings
}: {
  chart: IChart;
  settings: IWorkflowWidgetSettings;
}) {
  const [params, setParams] = useState<{ [name: string]: IParamValue }>({});
  const [secrets, setSecrets] = useState<{ [name: string]: ISecretValue }>({});
  const [cron, setCron] = useState<string | null>(null);
  const [submittedWorkflow, setSubmittedWorkflow] = useState<any>(null);

  const setParam = (name: string, value: IParamValue) => {
    setParams(prevState => ({ ...prevState, [name]: value }));
  };
  const setSecret = (name: string, value: ISecretValue) => {
    setSecrets(prevState => ({ ...prevState, [name]: value }));
  };

  useEffect(() => {
    Object.values(chart.nodes).forEach(node => {
      node.properties.cell.params.forEach((param: IParam) => {
        setParam(param.name, {
          value: null,
          default_value: param.default_value
        });
      });
      node.properties.cell.secrets.forEach((secret: ISecret) => {
        setSecret(secret.name, { value: null });
      });
    });
  }, [chart.nodes]);

  const updateParamValue = async (
    event: ChangeEvent<{ value: string }>,
    key: string
  ) => {
    setParam(key, {
      value: event.target.value,
      default_value: params[key].default_value
    });
  };

  const updateSecretValue = async (
    event: ChangeEvent<{ value: string }>,
    key: string
  ) => {
    setSecret(key, { value: event.target.value });
  };

  const allValuesFilled = () => {
    let all_filled = true;
    Object.values(params).forEach(param => {
      all_filled = all_filled && param.value !== null;
    });
    Object.values(secrets).forEach(secret => {
      all_filled = all_filled && secret.value !== null;
    });
    return all_filled;
  };

  const getValuesFromCatalog = async () => {
    Object.entries(params).forEach(([k, v]) => {
      setParam(k, {
        value: v.default_value || null,
        default_value: v.default_value
      });
    });
  };

  const runWorkflow = async (
    params: { [name: string]: any },
    secrets: { [name: string]: any }
  ) => {
    NaaVREExternalService(
      'POST',
      `${settings.workflowServiceUrl}/submit`,
      {},
      {
        virtual_lab: settings.virtualLab,
        naavrewf2: chart,
        params: params,
        secrets: secrets,
        cron_schedule: cron
      }
    )
      .then(resp => {
        if (resp.status_code !== 200) {
          throw `${resp.status_code} ${resp.reason}`;
        }
        const data = JSON.parse(resp.content);
        setSubmittedWorkflow(data);
      })
      .catch(error => {
        const msg = `Error running the workflow: ${error}`;
        console.log(msg);
        alert(msg);
      });
  };

  return (
    <ThemeProvider theme={theme}>
      <div
        style={{
          display: 'flex',
          overflow: 'scroll',
          flexDirection: 'column'
        }}
      >
        {submittedWorkflow ? (
          <div
            style={{
              padding: '10px',
              alignItems: 'center',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <CheckCircleOutlineIcon
              fontSize="large"
              sx={{ color: green[500] }}
            />
            <p style={{ fontSize: 'large' }}>
              Workflow submitted! You can track it{' '}
              <a target={'_blank'} href={submittedWorkflow.run_url}>
                here
              </a>
            </p>
          </div>
        ) : (
          <div>
            {Object.keys(params).length !== 0 && (
              <div
                style={{
                  textAlign: 'right',
                  padding: '10px 15px 0 0'
                }}
              >
                <Button
                  disabled={false}
                  onClick={getValuesFromCatalog}
                  size="small"
                  variant="text"
                  endIcon={<AutoModeIcon fontSize="inherit" />}
                  style={{ color: grey[900], textTransform: 'none' }}
                >
                  Use default parameter values
                </Button>
              </div>
            )}
            <TableContainer>
              <Table stickyHeader aria-label="sticky table">
                <TableBody>
                  {Object.entries(params).map(([k, v]) => (
                    <TableRow hover role="checkbox" tabIndex={-1} key={k}>
                      <TableCell key={k} align={'right'}>
                        {k}
                      </TableCell>
                      <TableCell component="th" scope="row">
                        <TextField
                          value={params[k].value}
                          onChange={e => updateParamValue(e, k)}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                  {Object.entries(secrets).map(([k, v]) => (
                    <TableRow hover role="checkbox" tabIndex={-1} key={k}>
                      <TableCell key={k} align={'right'}>
                        {k}
                      </TableCell>
                      <TableCell component="th" scope="row">
                        <TextField
                          type="password"
                          autoComplete="off"
                          value={secrets[k].value}
                          onChange={e => updateSecretValue(e, k)}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Stack
              direction="row"
              spacing={2}
              style={{
                float: 'right',
                marginTop: '2rem',
                alignItems: 'center'
              }}
            >
              <WorkflowRepeatPicker setCron={setCron} />
              <Button
                variant="contained"
                className={'lw-panel-button'}
                onClick={() => runWorkflow(params, secrets)}
                color="primary"
                disabled={!allValuesFilled()}
                style={{
                  float: 'right'
                }}
              >
                Run
              </Button>
            </Stack>
          </div>
        )}
      </div>
    </ThemeProvider>
  );
}
