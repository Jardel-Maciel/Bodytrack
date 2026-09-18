import { api } from "./api";
import type { PhotoAngle, ProgressPhoto } from "@/types";

export async function upload(
  projectId: string,
  input: { angle: PhotoAngle; date: string; week_number?: number | null; file: File }
) {
  const form = new FormData();
  form.append("angle", input.angle);
  form.append("date", input.date);
  if (input.week_number != null) form.append("week_number", String(input.week_number));
  form.append("file", input.file);

  const { data } = await api.post<ProgressPhoto>(`/projects/${projectId}/photos`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function list(projectId: string) {
  const { data } = await api.get<ProgressPhoto[]>(`/projects/${projectId}/photos`);
  return data;
}

/** Busca o binário da foto autenticado e devolve uma URL de blob local (a rota não é pública). */
export async function getPhotoObjectUrl(projectId: string, photoId: string) {
  const { data } = await api.get(`/projects/${projectId}/photos/${photoId}/file`, {
    responseType: "blob",
  });
  return URL.createObjectURL(data as Blob);
}

export async function remove(projectId: string, photoId: string) {
  await api.delete(`/projects/${projectId}/photos/${photoId}`);
}

export async function compareWeeks(projectId: string, weekA: number, weekB: number) {
  const { data } = await api.get(`/projects/${projectId}/photos/compare`, {
    params: { week_a: weekA, week_b: weekB },
  });
  return data as { week_a: number; week_b: number; photos_a: ProgressPhoto[]; photos_b: ProgressPhoto[] };
}
