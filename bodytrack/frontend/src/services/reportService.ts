import { api } from "./api";

export interface WeeklyReport {
  id: string;
  project_id: string;
  week_number: number;
  start_date: string;
  end_date: string;
  summary: Record<string, number | string | null>;
}

export async function generate(projectId: string, weekNumber: number) {
  const { data } = await api.post<WeeklyReport>(`/projects/${projectId}/reports/generate`, {
    week_number: weekNumber,
  });
  return data;
}

export async function list(projectId: string) {
  const { data } = await api.get<WeeklyReport[]>(`/projects/${projectId}/reports`);
  return data;
}

export function pdfUrl(projectId: string, reportId: string) {
  return `${api.defaults.baseURL}/projects/${projectId}/reports/${reportId}/pdf`;
}

export async function downloadExport(projectId: string, format: "csv" | "json") {
  const { data, headers } = await api.get(`/projects/${projectId}/reports/export`, {
    params: { format },
    responseType: "blob",
  });
  const url = URL.createObjectURL(data as Blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `bodytrack_export.${format}`;
  a.click();
  URL.revokeObjectURL(url);
  return headers;
}

export async function listAchievements(projectId: string) {
  const { data } = await api.get(`/projects/${projectId}/achievements`);
  return data as { code: string; label: string; unlocked_at: string }[];
}
