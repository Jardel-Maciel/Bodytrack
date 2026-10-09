import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { useUnread } from "@/hooks/useUnread";
import * as noticeService from "@/services/noticeService";
import type { AppNotice } from "@/types";

const ICONS: Record<string, string> = {
  workout_new: "🏋️",
  workout_updated: "✏️",
  workout_removed: "🗑️",
  link_accepted: "🤝",
  consent_changed: "🔐",
  link_ended: "👋",
};

const formatWhen = (iso: string) =>
  new Date(iso).toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });

export default function NoticesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { notices, noticeCount, chatCount } = useUnread();

  const markRead = useMutation({
    mutationFn: (ids?: string[]) => noticeService.markRead(ids),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notices"] }),
  });

  const open = (n: AppNotice) => {
    if (!n.read) markRead.mutate([n.id]);
    if (n.link_path) navigate(n.link_path);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Avisos</h1>
        {noticeCount > 0 && (
          <button type="button" onClick={() => markRead.mutate(undefined)} className="text-xs text-accent hover:underline">
            Marcar todos como lidos
          </button>
        )}
      </div>

      {chatCount > 0 && (
        <p className="rounded-xl border border-accent/40 bg-accent-muted/20 px-3 py-2 text-sm">
          💬 Você tem {chatCount} {chatCount === 1 ? "mensagem nova" : "mensagens novas"} no chat.
        </p>
      )}

      {notices.length === 0 && (
        <div className="card text-sm text-foreground-muted">
          Nenhum aviso por enquanto. Quando seu personal atualizar um treino, ou um aluno responder a um convite, aparece aqui.
        </div>
      )}

      <div className="space-y-2">
        {notices.map((n) => (
          <button
            key={n.id}
            type="button"
            onClick={() => open(n)}
            className={`card flex w-full items-start gap-3 text-left hover:border-accent ${n.read ? "opacity-70" : ""}`}
          >
            <span className="text-xl" aria-hidden>{ICONS[n.kind] ?? "🔔"}</span>
            <span className="flex-1">
              <span className={`block text-sm ${n.read ? "" : "font-semibold"}`}>{n.title}</span>
              {n.body && <span className="block text-xs text-foreground-muted">{n.body}</span>}
              <span className="mt-1 block text-[11px] text-foreground-muted">{formatWhen(n.at)}</span>
            </span>
            {!n.read && <span className="mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full bg-accent" aria-label="não lido" />}
          </button>
        ))}
      </div>
    </div>
  );
}
