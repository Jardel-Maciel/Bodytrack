import { useQuery } from "@tanstack/react-query";

import { useAuth } from "@/contexts/AuthContext";
import * as chatService from "@/services/chatService";
import * as noticeService from "@/services/noticeService";

const POLL_MS = 30_000;

/**
 * Contadores do sino. Consulta a cada 30s (e ao voltar para a aba) — simples e
 * suficiente para avisos; sem websocket/push nesta versão. Se a consulta falhar
 * (offline), os números ficam como estavam em vez de quebrar a tela.
 */
export function useUnread() {
  const { user } = useAuth();
  const enabled = Boolean(user);
  const notices = useQuery({ queryKey: ["notices"], queryFn: noticeService.list, enabled, refetchInterval: POLL_MS });
  const chat = useQuery({ queryKey: ["chat-unread"], queryFn: chatService.unread, enabled, refetchInterval: POLL_MS });

  const noticeCount = notices.data?.unread_count ?? 0;
  const chatByLink = chat.data?.by_link ?? {};
  const chatCount = chat.data?.total ?? 0;
  return { noticeCount, chatCount, chatByLink, total: noticeCount + chatCount, notices: notices.data?.items ?? [] };
}
