import { api } from "./api";
import * as offlineQueue from "./offlineQueue";
import type { DailyCheckin } from "@/types";

export type CheckinInput = Omit<DailyCheckin, "id" | "project_id"> & { project_id: string };

export interface UpsertResult {
  data: DailyCheckin | null;
  queued: boolean;
}

/**
 * Se a rede falhar (sem `response` no erro do axios — timeout, DNS,
 * offline de verdade), o check-in não é perdido: entra na fila offline
 * e `queued: true` avisa a tela para mostrar "salvo, será sincronizado"
 * em vez de um erro. Um erro de VALIDAÇÃO (400/422, que tem `response`)
 * continua sendo lançado normalmente — esse é um erro de verdade, não
 * um problema de conectividade.
 */
export async function upsert(projectId: string, input: Omit<CheckinInput, "project_id">): Promise<UpsertResult> {
  const payload = { ...input, project_id: projectId };
  try {
    const { data } = await api.post<DailyCheckin>(`/projects/${projectId}/checkins`, payload);
    return { data, queued: false };
  } catch (err: any) {
    if (!err?.response) {
      offlineQueue.enqueueCheckin(projectId, payload);
      return { data: null, queued: true };
    }
    throw err;
  }
}

export async function list(projectId: string, params?: { start?: string; end?: string }) {
  const { data } = await api.get<DailyCheckin[]>(`/projects/${projectId}/checkins`, { params });
  return data;
}

export async function getByDate(projectId: string, date: string) {
  const rows = await list(projectId, { start: date, end: date });
  return rows[0] ?? null;
}
