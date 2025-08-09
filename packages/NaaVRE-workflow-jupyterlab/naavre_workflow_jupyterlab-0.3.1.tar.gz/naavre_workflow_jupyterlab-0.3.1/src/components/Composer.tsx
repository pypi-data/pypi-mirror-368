import * as React from 'react';
import { mapValues } from 'lodash';
import { Dialog, ReactWidget } from '@jupyterlab/apputils';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { ThemeProvider } from '@mui/material/styles';
import * as actions from '@mrblenny/react-flow-chart/src/container/actions';
import {
  FlowChart,
  IChart,
  IConfig,
  INodeDefaultProps
} from '@mrblenny/react-flow-chart';

import { ICell } from '../naavre-common/types/NaaVRECatalogue/WorkflowCells';
import { NaaVREExternalService } from '../naavre-common/handler';
import { defaultChart } from '../utils/chart';
import { theme } from '../Theme';
import { IWorkflowWidgetSettings } from '../widget';
import { NodeCustom } from './chart/NodeCustom';
import { NodeInnerCustom } from './chart/NodeInnerCustom';
import { PortCustom } from './chart/PortCustom';
import { ChartElementEditor } from './chart/ChartElementEditor';
import { RunWorkflowDialog } from './workflowRunDialog/RunWorkflowDialog';
import { CellsSideBar } from './cells/CellsSideBar';
import { CellPopup } from './cells/CellPopup';

export interface IProps {
  settings: IWorkflowWidgetSettings;
}

export interface IState {
  chart: IChart;
  selectedCellInList: ICell | null;
  selectedCellNode: HTMLDivElement | null;
}

export const DefaultState: IState = {
  chart: defaultChart,
  selectedCellInList: null,
  selectedCellNode: null
};

export class Composer extends React.Component<IProps, IState> {
  state = DefaultState;

  constructor(props: IProps) {
    super(props);
  }

  chartStateActions = mapValues(actions, (func: any) => (...args: any) => {
    const newChartTransformer = func(...args);
    const newChart = newChartTransformer(this.state.chart);
    this.setState({
      chart: { ...this.state.chart, ...newChart }
    });
  }) as typeof actions;

  chartConfig: IConfig = {
    // This is needed because onDeleteKey assumes config.readonly is defined...
    // https://github.com/MrBlenny/react-flow-chart/blob/0.0.14/src/container/actions.ts#L182
    readonly: false
  };

  setSelectedCell = (cell: ICell | null, cellNode: HTMLDivElement | null) => {
    this.setState({
      selectedCellInList: cell,
      selectedCellNode: cellNode
    });
  };

  setChart = (chart: IChart) => {
    this.setState({ chart: chart });
  };

  getRunWorkflowDialogOptions = (): Partial<Dialog.IOptions<any>> => {
    return {
      title: 'Run Workflow',
      body: ReactWidget.create(
        <RunWorkflowDialog
          chart={this.state.chart}
          settings={this.props.settings}
        />
      ) as Dialog.IBodyWidget<any>,
      buttons: [],
      hasClose: true
    };
  };

  exportWorkflow = async (browserFactory: IFileBrowserFactory) => {
    NaaVREExternalService(
      'POST',
      `${this.props.settings.workflowServiceUrl}/convert`,
      {},
      {
        virtual_lab: this.props.settings.virtualLab,
        naavrewf2: this.state.chart
      }
    )
      .then(resp => {
        browserFactory.tracker.currentWidget?.model.upload(
          new File([resp.content], 'workflow.yaml')
        );
      })
      .catch(error => {
        const msg = `Error exporting the workflow: ${String(error)}`;
        console.log(msg);
        alert(msg);
      });
  };

  componentDidUpdate() {
    // TODO: Implement chart sanity checks
  }

  render(): React.ReactElement {
    return (
      <ThemeProvider theme={theme}>
        <div
          style={{
            display: 'flex',
            flexDirection: 'row',
            flex: 1,
            maxWidth: '100vw',
            maxHeight: '100vh'
          }}
        >
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              flex: '1',
              overflow: 'hidden'
            }}
          >
            <FlowChart
              chart={this.state.chart}
              callbacks={this.chartStateActions}
              config={this.chartConfig}
              Components={{
                Node: NodeCustom as React.FunctionComponent<INodeDefaultProps>,
                NodeInner: NodeInnerCustom,
                Port: PortCustom
              }}
            />
            {this.state.chart.selected.id && (
              <ChartElementEditor
                chart={this.state.chart}
                setChart={this.setChart}
                callbacks={this.chartStateActions}
                config={this.chartConfig}
              />
            )}
            {this.state.selectedCellInList && (
              <CellPopup
                cell={this.state.selectedCellInList}
                cellNode={this.state.selectedCellNode}
                onClose={() => this.setSelectedCell(null, null)}
              />
            )}
            <CellsSideBar
              settings={this.props.settings}
              selectedCellInList={this.state.selectedCellInList}
              setSelectedCell={this.setSelectedCell}
            />
          </div>
        </div>
      </ThemeProvider>
    );
  }
}
