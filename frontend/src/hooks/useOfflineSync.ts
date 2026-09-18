import { useEffect, useState } from "react";

import * as offlineQueue from "@/services/offlineQueue";

/**
 * Tenta sincronizar a fila offline: ao montar o app, quando o
 * navegador dispara o evento "online", e a cada 30s como rede de
 * segurança (o evento "online" nem sempre dispara de forma confiável
 * em todos os navegadores/dispositivos).
 */
export function useOfflineSync(): number {
  const [pending, setPending] = useState(() => offlineQueue.pendingCount());

  useEffect(() => {
    let cancelled = false;

    const trySync = async () => {
      if (!navigator.onLine) return;
      await offlineQueue.flushQueue();
      if (!cancelled) setPending(offlineQueue.pendingCount());
    };

    trySync();
    window.addEventListener("online", trySync);
    const interval = window.setInterval(trySync, 30_000);

    return () => {
      cancelled = true;
      window.removeEventListener("online", trySync);
      window.clearInterval(interval);
    };
  }, []);

  return pending;
}
