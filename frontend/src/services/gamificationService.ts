import { api } from "./api";
import type { GamificationSummary } from "@/types";

export async function getSummary() {
  const { data } = await api.get<GamificationSummary>("/gamification/summary");
  return data;
}
