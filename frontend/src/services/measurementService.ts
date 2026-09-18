import { api } from "./api";
import type { BodyMeasurement } from "@/types";

export interface MeasurementProgressField {
  field: string;
  initial_value: number | null;
  current_value: number | null;
  variation: number | null;
  variation_pct: number | null;
}

export async function upsert(
  projectId: string,
  input: Omit<BodyMeasurement, "id" | "project_id">
) {
  const { data } = await api.post<BodyMeasurement>(`/projects/${projectId}/measurements`, {
    ...input,
    project_id: projectId,
  });
  return data;
}

export async function list(projectId: string) {
  const { data } = await api.get<BodyMeasurement[]>(`/projects/${projectId}/measurements`);
  return data;
}

export async function progress(projectId: string) {
  const { data } = await api.get<{ fields: MeasurementProgressField[] }>(
    `/projects/${projectId}/measurements/progress`
  );
  return data.fields;
}
