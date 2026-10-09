import { useEffect, useRef, useState } from "react";

import { useGamification } from "@/hooks/useGamification";

/**
 * Aviso "+N pontos" quando o total sobe. Compara com o total anterior; a primeira
 * leitura da sessão só guarda o valor (senão todo mundo veria um toast ao abrir o app).
 */
export default function PointsToast() {
  const { data } = useGamification();
  const previous = useRef<number | null>(null);
  const [gained, setGained] = useState<number | null>(null);

  useEffect(() => {
    if (!data) return;
    if (previous.current !== null && data.total_points > previous.current) {
      setGained(data.total_points - previous.current);
      const timer = window.setTimeout(() => setGained(null), 3500);
      previous.current = data.total_points;
      return () => window.clearTimeout(timer);
    }
    previous.current = data.total_points;
  }, [data?.total_points]); // eslint-disable-line react-hooks/exhaustive-deps

  if (gained === null) return null;
  return (
    <div
      role="status"
      className="fixed inset-x-0 top-4 z-50 mx-auto w-fit rounded-full bg-success px-4 py-2 text-sm font-semibold text-white shadow-lg"
    >
      🎉 +{gained} {gained === 1 ? "ponto" : "pontos"}!
    </div>
  );
}
