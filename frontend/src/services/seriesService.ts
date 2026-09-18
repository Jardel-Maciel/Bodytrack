import { api } from "./api";

export interface SeriesPoint {
  date: string;
  value: number;
}

export interface Series {
  metric: string;
  period: string;
  points: SeriesPoint[];
}

export async function getSeries(projectId: string, metric: string, period: string) {
  const { data } = await api.get<Series>(`/projects/${projectId}/series`, {
    params: { metric, period },
  });
  return data;
}
