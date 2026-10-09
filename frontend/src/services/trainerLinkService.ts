import { api } from "./api";
import type { MyTrainerLink } from "@/types";

export async function list() {
  const { data } = await api.get<MyTrainerLink[]>("/trainer-links");
  return data;
}

export async function accept(input: { code: string; share_photos: boolean; share_progress: boolean }) {
  const { data } = await api.post<MyTrainerLink>("/trainer-links/accept", input);
  return data;
}

export async function updateConsent(linkId: string, input: { share_photos?: boolean; share_progress?: boolean }) {
  const { data } = await api.patch<MyTrainerLink>(`/trainer-links/${linkId}`, input);
  return data;
}

export async function end(linkId: string) {
  await api.delete(`/trainer-links/${linkId}`);
}
