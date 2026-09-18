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

// O endpoint de listagem não tem filtro por data (só o de check-ins
// tem), então filtramos no cliente. Usado para pré-carregar o
// formulário de medidas com o que já foi salvo para a data escolhida,
// evitando apagar campos antigos ao salvar só um campo novo (o upsert
// do backend substitui o registro inteiro).
export async function getByDate(projectId: string, date: string) {
  const rows = await list(projectId);
  return rows.find((m) => m.date === date) ?? null;
}

export async function progress(projectId: string) {
  const { data } = await api.get<{ fields: MeasurementProgressField[] }>(
    `/projects/${projectId}/measurements/progress`
  );
  return data.fields;
}
