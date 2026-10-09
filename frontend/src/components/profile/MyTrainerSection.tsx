import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useAuth } from "@/contexts/AuthContext";
import { useUnread } from "@/hooks/useUnread";
import * as trainerLinkService from "@/services/trainerLinkService";
import * as trainerService from "@/services/trainerService";

const key = ["my-trainers"];

/** Perfil › "Meu personal": vincular por código, escolher o que compartilha e encerrar. Também liga/desliga o modo personal. */
export default function MyTrainerSection() {
  const { user, updateProfile } = useAuth();
  const queryClient = useQueryClient();
  const { chatByLink } = useUnread();
  const [code, setCode] = useState("");
  const [sharePhotos, setSharePhotos] = useState(false);
  const [shareProgress, setShareProgress] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: links } = useQuery({ queryKey: key, queryFn: trainerLinkService.list });

  const accept = useMutation({
    mutationFn: () => trainerLinkService.accept({ code: code.trim(), share_photos: sharePhotos, share_progress: shareProgress }),
    onSuccess: () => {
      setCode("");
      setError(null);
      queryClient.invalidateQueries({ queryKey: key });
      queryClient.invalidateQueries({ queryKey: ["workouts"] });
    },
    onError: (err) => setError(trainerService.errorMessage(err, "Não foi possível usar este código.")),
  });

  const consent = useMutation({
    mutationFn: (v: { id: string; share_photos?: boolean; share_progress?: boolean }) =>
      trainerLinkService.updateConsent(v.id, { share_photos: v.share_photos, share_progress: v.share_progress }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: key }),
  });

  const end = useMutation({
    mutationFn: (id: string) => trainerLinkService.end(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: key }),
  });

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (code.trim()) accept.mutate();
  };

  const toggleClass = "flex items-center gap-2 text-sm";

  return (
    <div className="card space-y-3">
      <p className="stat-label">Meu personal</p>

      {links?.map((l) => (
        <div key={l.link_id} className="space-y-2 rounded-xl border border-border p-3">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">{l.trainer_name}</p>
            <Link to={`/chat/${l.link_id}`} className="text-xs text-accent">
              💬 Conversar{(chatByLink[l.link_id] ?? 0) > 0 ? ` (${chatByLink[l.link_id]})` : ""}
            </Link>
          </div>
          <label className={toggleClass}>
            <input
              type="checkbox"
              checked={l.share_photos}
              onChange={(e) => consent.mutate({ id: l.link_id, share_photos: e.target.checked })}
            />
            Compartilhar minhas fotos
          </label>
          <label className={toggleClass}>
            <input
              type="checkbox"
              checked={l.share_progress}
              onChange={(e) => consent.mutate({ id: l.link_id, share_progress: e.target.checked })}
            />
            Compartilhar minha evolução (peso, medidas, treinos feitos)
          </label>
          <button
            type="button"
            onClick={() =>
              window.confirm(`Encerrar o vínculo com ${l.trainer_name}? Ele perde o acesso na hora; os treinos que montou continuam com você.`) &&
              end.mutate(l.link_id)
            }
            className="text-xs text-danger hover:underline"
          >
            Encerrar vínculo
          </button>
        </div>
      ))}

      <form onSubmit={onSubmit} className="space-y-2">
        <p className="text-xs text-foreground-muted">
          {links?.length ? "Tem outro código?" : "Seu personal te enviou um código? Digite aqui para vincular."}
        </p>
        <input
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          placeholder="CÓDIGO"
          maxLength={16}
          autoCapitalize="characters"
          className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-center text-sm tracking-[0.25em] outline-none focus:border-accent"
        />
        {code.trim() && (
          <div className="space-y-1.5 rounded-xl border border-border p-3">
            <p className="text-xs text-foreground-muted">O que você quer compartilhar com ele? (dá para mudar depois)</p>
            <label className={toggleClass}>
              <input type="checkbox" checked={sharePhotos} onChange={(e) => setSharePhotos(e.target.checked)} />
              Minhas fotos de evolução
            </label>
            <label className={toggleClass}>
              <input type="checkbox" checked={shareProgress} onChange={(e) => setShareProgress(e.target.checked)} />
              Minha evolução (peso, medidas, treinos feitos)
            </label>
          </div>
        )}
        {error && <p className="text-sm text-danger">{error}</p>}
        <button
          type="submit"
          disabled={!code.trim() || accept.isPending}
          className="w-full rounded-xl bg-accent py-2 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-50"
        >
          {accept.isPending ? "Vinculando…" : "Vincular ao personal"}
        </button>
      </form>

      <div className="border-t border-border pt-3">
        {user?.role === "trainer" ? (
          <div className="flex items-center justify-between text-sm">
            <span className="text-foreground-muted">Modo personal ativo</span>
            <Link to="/alunos" className="text-accent">Ir para Meus alunos ›</Link>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => updateProfile({ role: "trainer" })}
            className="text-xs text-accent hover:underline"
          >
            Sou personal trainer — ativar área do personal
          </button>
        )}
      </div>
    </div>
  );
}
