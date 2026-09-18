import { api } from "./api";
import type { Project } from "@/types";

export interface NewProjectInput {
  name: string;
  goal_description?: string | null;
  start_date: string;
  end_date: string;
  initial_weight_kg?: number | null;
}

export async function list() {
  const { data } = await api.get<Project[]>("/projects");
  return data;
}

export async function create(input: NewProjectInput) {
  const { data } = await api.post<Project>("/projects", input);
  return data;
}

export async function get(id: string) {
  const { data } = await api.get<Project>(`/projects/${id}`);
  return data;
}
