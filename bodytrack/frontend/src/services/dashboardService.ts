import { api } from "./api";

export interface DashboardSummary {
  project_name: string;
  day_of_project: number;
  week_of_project: number;
  total_weeks: number;
  percent_complete: number;
  days_remaining: number;
  streak_days: number;
  consistency_pct_last_7_days: number;
  last_checkin_date: string | null;
  initial_weight_kg: number | null;
  current_weight_kg: number | null;
  weight_variation_kg: number | null;
  bmi: number | null;
  waist_cm: number | null;
  abdomen_cm: number | null;
  hip_cm: number | null;
  water_liters_today: number | null;
  sleep_hours_last_night: number | null;
  steps_today: number | null;
  workouts_this_week: number;
}

export async function getDashboard(projectId: string) {
  const { data } = await api.get<DashboardSummary>(`/projects/${projectId}/dashboard`);
  return data;
}
