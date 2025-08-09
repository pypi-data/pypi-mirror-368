export interface IBaseAsset {
  id: string;
  title: string;
  description?: string;
  created?: string;
  modified?: string;
  owner?: string;
  virtual_lab?: string | null;
}
