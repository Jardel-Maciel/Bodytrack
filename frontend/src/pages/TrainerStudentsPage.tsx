import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useAuth } from "@/contexts/AuthContext";
import { useUnread } from "@/hooks/useUnread";
import * as trainerService from "@/services/trainerService";
import type { InviteRead } from "@/types";

const formatDate = (iso: string) => iso.split("-").reverse().join("/");

export default function TrainerStudentsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const { chatByLink } = useUnread();
  const [label, setLabel] = useState("");
  const [invite, setInvite] = useState<InviteRead | null>(null);
  const [copied, setCopied] = useState(false);

  const { data: students, isLoading } = useQuery({
    queryKey: ["trainer-students"],
    queryFn: trainerService.listStudents,
    enabled: user?.role === "trainer",
  });

  const createInvite = useMutation({
    mutationFn: () => trainerService.createInvite(label.trim()),
    onSuccess: (data) => {
      setInvite(data);
      setLabel("");
      setCopied(false);
      queryClient.invalidateQueries({ queryKey: ["trainer-students"] });
    },
  });

  const cancelInvite = useMutation({
    mutationFn: (linkId: string) => trainerService.removeStudent(linkId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["trainer-students"] }),
  });

  if (user?.role !== "trainer") {
    return (
      <div className="card text-sm text-foreground-muted">
        Esta área é exclusiva para contas de personal. Ative o modo personal em <b>Perfil</b>.
      </div>
    );
  }

  const shareText = (code: string) =>
    `Entre no BodyTrack, vá em Perfil › Meu personal e digite o código ${code} para vincular sua conta ao meu acompanhamento. Você escolhe o que compartilha comigo.`;

  const copy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  };

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    createInvite.mutate();
  };

  const active = students?.filter((s) => s.status === "active") ?? [];
  const pending = students?.filter((s) => s.status === "pending") ?? [];

  return (
    <div className="space-y-5">
      <h1 className="text-lg font-semibold">Meus alunos</h1>

      <form onSubmit={onSubmit} className="card space-y-3">
        <p className="stat-label">Adicionar aluno</p>
        <div className="flex gap-2">
          <input
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="Nome do aluno (opcional)"
            className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
          />
          <button
            type="submit"
            disabled={createInvite.isPending}
            className="shrink-0 rounded-xl bg-accent px-4 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60"
          >
            Gerar convite
          </button>
        </div>

        {invite && (
          <div className="space-y-2 rounded-xl border border-accent/40 bg-accent-muted/20 p-3">
            <p className="text-xs text-foreground-muted">Envie este código ao aluno (vale por 14 dias, uso único):</p>
            <p className="text-center text-2xl font-bold tracking-[0.3em]">{invite.invite_code}</p>
            <button
              type="button"
              onClick={() => copy(shareText(invite.invite_code))}
              className="w-full rounded-lg border border-border py-2 text-sm hover:border-accent"
            >
              {copied ? "✓ Mensagem copiada" : "Copiar mensagem para enviar"}
            </button>
          </div>
        )}
      </form>

      {isLoading && <p className="text-sm text-foreground-muted">Carregando…</p>}

      {!isLoading && active.length === 0 && pending.length === 0 && (
        <div className="card text-sm text-foreground-muted">
          Você ainda não tem alunos. Gere um convite acima e envie o código para o primeiro.
        </div>
      )}

      <div className="space-y-3">
        {active.map((s) => (
          <Link key={s.link_id} to={`/alunos/${s.link_id}`} className="card block hover:border-accent">
            <div className="flex items-center justify-between">
              <p className="font-medium">{s.display_name}</p>
              <span className="flex items-center gap-2 text-xs text-accent">
                {(chatByLink[s.link_id] ?? 0) > 0 && (
                  <span className="rounded-full bg-danger px-1.5 py-0.5 text-[10px] font-bold text-white">
                    💬 {chatByLink[s.link_id]}
                  </span>
                )}
                abrir ›
              </span>
            </div>
            <p className="text-xs text-foreground-muted">{s.project_name ?? "Sem projeto ativo"}</p>
            <div className="mt-2 flex flex-wrap gap-1.5 text-[11px]">
              <span className={`rounded-full px-2 py-0.5 ${s.share_photos ? "bg-success/15 text-success" : "bg-border text-foreground-muted"}`}>
                {s.share_photos ? `📷 ${s.photos_count ?? 0} fotos` : "📷 fotos não compartilhadas"}
              </span>
              <span className={`rounded-full px-2 py-0.5 ${s.share_progress ? "bg-success/15 text-success" : "bg-border text-foreground-muted"}`}>
                {s.share_progress
                  ? s.last_session_date
                    ? `🏋️ último treino ${formatDate(s.last_session_date)}`
                    : "🏋️ sem sessões ainda"
                  : "🏋️ evolução não compartilhada"}
              </span>
            </div>
          </Link>
        ))}
      </div>

      {pending.length > 0 && (
        <div className="space-y-2">
          <p className="stat-label">Convites pendentes</p>
          {pending.map((s) => (
            <div key={s.link_id} className="card flex items-center justify-between gap-2">
              <div>
                <p className="text-sm font-medium">{s.display_name}</p>
                <p className="text-xs tracking-widest text-foreground-muted">{s.invite_code}</p>
              </div>
              <button
                type="button"
                onClick={() => cancelInvite.mutate(s.link_id)}
                className="text-xs text-danger hover:underline"
              >
                cancelar
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
