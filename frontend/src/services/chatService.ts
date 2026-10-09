import { api } from "./api";
import type { ChatMessage, ChatUnread } from "@/types";

export async function listMessages(linkId: string) {
  const { data } = await api.get<ChatMessage[]>(`/chat/${linkId}/messages`);
  return data;
}

export async function send(linkId: string, body: string) {
  const { data } = await api.post<ChatMessage>(`/chat/${linkId}/messages`, { body });
  return data;
}

export async function unread() {
  const { data } = await api.get<ChatUnread>("/chat/unread");
  return data;
}
