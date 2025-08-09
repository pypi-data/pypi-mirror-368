import { ICell } from '../naavre-common/types/NaaVRECatalogue/WorkflowCells';

export interface ISpecialCell extends ICell {
  type: string;
}

export const specialCells: Array<ISpecialCell> = [
  {
    id: 'splitter',
    title: 'Splitter',
    type: 'splitter',
    container_image: '',
    dependencies: [],
    inputs: [{ name: 'splitter_source', type: 'list' }],
    outputs: [{ name: 'splitter_target', type: 'list' }],
    confs: [],
    params: [],
    secrets: []
  },
  {
    id: 'merger',
    title: 'Merger',
    type: 'merger',
    container_image: '',
    dependencies: [],
    inputs: [{ name: 'merger_source', type: 'list' }],
    outputs: [{ name: 'merger_target', type: 'list' }],
    confs: [],
    params: [],
    secrets: []
  },
  {
    id: 'visualizer',
    title: 'Visualizer',
    type: 'visualizer',
    container_image: '',
    dependencies: [],
    inputs: [
      { name: 'hostname', type: 'string' },
      { name: 'username', type: 'string' },
      { name: 'password', type: 'string' },
      { name: 'remote', type: 'string' },
      { name: 'num', type: 'string' },
      { name: 'mode', type: 'string' },
      { name: 'output', type: 'string' }
    ],
    outputs: [],
    confs: [],
    params: [],
    secrets: []
  }
];
