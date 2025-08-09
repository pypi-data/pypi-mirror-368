import { IBaseAsset } from './BaseAssets';

export interface IBaseImage {
  build: string;
  runtime: string;
}

export interface IDependency {
  name: string;
  module?: string;
  asname?: string;
}

export interface IBaseVariable {
  name: string;
  type: string | null;
}

export interface IInput extends IBaseVariable {}

export interface IOutput extends IBaseVariable {}

export interface IConf {
  name: string;
  assignation: string;
}

export interface IParam extends IBaseVariable {
  default_value?: string;
}

export interface ISecret extends IBaseVariable {}

export interface ICell extends IBaseAsset {
  container_image: string;
  base_container_image?: IBaseImage;
  dependencies: Array<IDependency>;
  inputs: Array<IInput>;
  outputs: Array<IOutput>;
  confs: Array<IConf>;
  params: Array<IParam>;
  secrets: Array<ISecret>;
  kernel?: string;
  source_url?: string;
}
