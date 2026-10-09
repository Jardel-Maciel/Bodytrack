import { api } from "./api";
import type {
  InviteRead,
  ProgressPhoto,
  StudentProgress,
  StudentSummary,
  TrainerWorkout,
  TrainerWorkoutInput,
} from "@/types";

const base = (linkId: string) => `/trainer/students/${linkId}`;

export async function createInvite(studentLabel: string) {
  const { data } = await api.post<InviteRead>("/trainer/invites", { student_label: studentLabel || null });
  return data;
}

export async function listStudents() {
  const { data } = await api.get<StudentSummary[]>("/trainer/students");
  return data;
}

export async function removeStudent(linkId: string) {
  await api.delete(base(linkId));
}

export async function listWorkouts(linkId: string) {
  const { data } = await api.get<TrainerWorkout[]>(`${base(linkId)}/workouts`);
  return data;
}

export async function createWorkout(linkId: string, input: TrainerWorkoutInput) {
  const { data } = await api.post<TrainerWorkout>(`${base(linkId)}/workouts`, input);
  return data;
}

export async function updateWorkout(linkId: string, workoutId: string, input: TrainerWorkoutInput) {
  const { data } = await api.put<TrainerWorkout>(`${base(linkId)}/workouts/${workoutId}`, input);
  return data;
}

/** "deleted" = apagado de vez; "archived" = o aluno já tem histórico nele, então só saiu da lista. */
export async function deleteWorkout(linkId: string, workoutId: string) {
  const { data } = await api.delete<{ result: "deleted" | "archived" }>(`${base(linkId)}/workouts/${workoutId}`);
  return data.result;
}

export async function getProgress(linkId: string) {
  const { data } = await api.get<StudentProgress>(`${base(linkId)}/progress`);
  return data;
}

export async function listPhotos(linkId: string) {
  const { data } = await api.get<ProgressPhoto[]>(`${base(linkId)}/photos`);
  return data;
}

/** A rota da foto exige o token, então baixamos como blob e criamos uma URL local. */
export async function getPhotoObjectUrl(linkId: string, photoId: string) {
  const { data } = await api.get(`${base(linkId)}/photos/${photoId}/file`, { responseType: "blob" });
  return URL.createObjectURL(data as Blob);
}

/** Extrai a mensagem de erro da API (ex.: 409 "o aluno já registrou séries em ..."). */
export function errorMessage(err: unknown, fallback: string) {
  return (err as any)?.response?.data?.detail && typeof (err as any).response.data.detail === "string"
    ? (err as any).response.data.detail
    : fallback;
}
