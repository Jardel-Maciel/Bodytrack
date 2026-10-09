import { Link } from "react-router-dom";

import { useUnread } from "@/hooks/useUnread";

/** Sino no topo de todas as telas: leva para /avisos e mostra o total de pendências (avisos + mensagens). */
export default function NoticeBell() {
  const { total } = useUnread();
  return (
    <Link
      to="/avisos"
      aria-label={total ? `Avisos: ${total} não lidos` : "Avisos"}
      className="relative inline-flex h-9 w-9 items-center justify-center rounded-full border border-border text-base hover:border-accent"
    >
      <span aria-hidden>🔔</span>
      {total > 0 && (
        <span className="absolute -right-1 -top-1 min-w-[18px] rounded-full bg-danger px-1 text-center text-[10px] font-bold leading-[18px] text-white">
          {total > 9 ? "9+" : total}
        </span>
      )}
    </Link>
  );
}
