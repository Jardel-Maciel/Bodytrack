import { api } from "./api";

/**
 * Fila offline simples (Etapa 12 — PWA/offline).
 *
 * Por que localStorage em vez de IndexedDB: o volume de dados aqui é
 * minúsculo (alguns check-ins não sincronizados, cada um um JSON de
 * poucas centenas de bytes), então a API mais simples já resolve sem
 * puxar uma dependência extra. Se o app crescer para also enfileirar
 * fotos (arquivos grandes) offline, isso migra para IndexedDB.
 *
 * O ponto central: se `checkinService.upsert` falhar por falta de
 * rede, o check-in entra nesta fila em vez de se perder — e é
 * reenviado automaticamente quando a conexão volta (ver useOfflineSync).
 */
const QUEUE_KEY = "bodytrack.offline_checkin_queue";

interface QueuedCheckin {
  projectId: string;
  payload: Record<string, unknown>;
  queuedAt: number;
}

function readQueue(): QueuedCheckin[] {
  try {
    const raw = localStorage.getItem(QUEUE_KEY);
    return raw ? (JSON.parse(raw) as QueuedCheckin[]) : [];
  } catch {
    return [];
  }
}

function writeQueue(queue: QueuedCheckin[]): void {
  try {
    localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
  } catch {
    // Armazenamento indisponível (modo privado, cota excedida...) — a
    // fila offline vira best-effort, mas não derruba o app por isso.
  }
}

export function enqueueCheckin(projectId: string, payload: Record<string, unknown>): void {
  const queue = readQueue();
  queue.push({ projectId, payload, queuedAt: Date.now() });
  writeQueue(queue);
}

export function pendingCount(): number {
  return readQueue().length;
}

export async function flushQueue(): Promise<{ synced: number; failed: number }> {
  const queue = readQueue();
  if (queue.length === 0) return { synced: 0, failed: 0 };

  const remaining: QueuedCheckin[] = [];
  let synced = 0;

  for (const item of queue) {
    try {
      await api.post(`/projects/${item.projectId}/checkins`, item.payload);
      synced += 1;
    } catch {
      remaining.push(item);
    }
  }

  writeQueue(remaining);
  return { synced, failed: remaining.length };
}
