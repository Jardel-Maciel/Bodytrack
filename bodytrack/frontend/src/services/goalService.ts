import { api } from "./api";
import type { Goal, GoalType } from "@/types";

export async function create(projectId: string, input: { type: GoalType; target_value: number; target_exercise_name?: string | null }) {
  const { data } = await api.post<Goal>(`/projects/${projectId}/goals`, input);
  return data;
}

export async function list(projectId: string) {
  const { data } = await api.get<Goal[]>(`/projects/${projectId}/goals`);
  return data;
}

export async function update(projectId: string, goalId: string, input: Partial<Pick<Goal, "target_value" | "achieved">>) {
  const { data } = await api.patch<Goal>(`/projects/${projectId}/goals/${goalId}`, input);
  return data;
}

export async function remove(projectId: string, goalId: string) {
  await api.delete(`/projects/${projectId}/goals/${goalId}`);
}
