import { useEffect, useRef, useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import * as chatService from "@/services/chatService";
import * as trainerService from "@/services/trainerService";

const formatTime = (iso: string) => {
  const d = new Date(iso);
  const today = new Date().toDateString() === d.toDateString();
  const time = d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  return today ? time : `${d.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" })} ${time}`;
};

/**
 * Conversa entre personal e aluno. Atualiza a cada 8s enquanto a tela está
 * aberta; abrir a conversa marca as mensagens recebidas como lidas (o servidor
 * faz isso na própria leitura), então o contador do sino é atualizado em seguida.
 */
export default function ChatPanel({ linkId, otherName }: { linkId: string; otherName: string }) {
  const queryClient = useQueryClient();
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  const key = ["chat", linkId];
  const { data: messages, isLoading } = useQuery({
    queryKey: key,
    queryFn: () => chatService.listMessages(linkId),
    refetchInterval: 8_000,
  });

  // Depois de cada leitura, o servidor já marcou como lidas: atualiza o contador do sino.
  useEffect(() => {
    if (messages) queryClient.invalidateQueries({ queryKey: ["chat-unread"] });
  }, [messages?.length, queryClient]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [messages?.length]);

  const send = useMutation({
    mutationFn: (body: string) => chatService.send(linkId, body),
    onSuccess: () => {
      setText("");
      setError(null);
      queryClient.invalidateQueries({ queryKey: key });
    },
    onError: (err) => setError(trainerService.errorMessage(err, "Não foi possível enviar.")),
  });

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    const body = text.trim();
    if (body && !send.isPending) send.mutate(body);
  };

  return (
    <div className="card flex h-[60vh] flex-col gap-3 p-3">
      <div className="flex-1 space-y-2 overflow-y-auto pr-1" aria-live="polite">
        {isLoading && <p className="text-sm text-foreground-muted">Carregando conversa…</p>}
        {!isLoading && messages?.length === 0 && (
          <p className="pt-6 text-center text-sm text-foreground-muted">
            Nenhuma mensagem ainda. Diga um oi para {otherName}!
          </p>
        )}
        {messages?.map((m) => (
          <div key={m.id} className={`flex ${m.mine ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] whitespace-pre-wrap break-words rounded-2xl px-3 py-2 text-sm ${
                m.mine ? "rounded-br-sm bg-accent text-white" : "rounded-bl-sm bg-border"
              }`}
            >
              {m.body}
              <span className={`mt-0.5 block text-right text-[10px] ${m.mine ? "text-white/70" : "text-foreground-muted"}`}>
                {formatTime(m.created_at)}
              </span>
            </div>
          </div>
        ))}
        <div ref={endRef} />
      </div>

      {error && <p className="text-xs text-danger">{error}</p>}
      <form onSubmit={onSubmit} className="flex gap-2">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={`Mensagem para ${otherName}`}
          maxLength={2000}
          className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
        />
        <button
          type="submit"
          disabled={!text.trim() || send.isPending}
          className="shrink-0 rounded-xl bg-accent px-4 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-50"
        >
          Enviar
        </button>
      </form>
    </div>
  );
}
