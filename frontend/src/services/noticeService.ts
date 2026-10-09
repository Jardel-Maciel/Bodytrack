import { api } from "./api";
import type { NoticeList } from "@/types";

export async function list() {
  const { data } = await api.get<NoticeList>("/notifications");
  return data;
}

/** Sem `ids` marca todos como lidos. */
export async function markRead(ids?: string[]) {
  const { data } = await api.post<{ unread_count: number }>("/notifications/read", { ids: ids ?? null });
  return data.unread_count;
}
