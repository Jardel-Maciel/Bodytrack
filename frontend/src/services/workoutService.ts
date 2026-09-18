import { api } from "./api";
import type { ExerciseSet, Workout, WorkoutSession } from "@/types";

export interface NewWorkoutInput {
  name: string;
  muscle_group?: string | null;
  notes?: string | null;
  exercises: { name: string; order?: number; target_sets?: number | null; target_reps?: string | null }[];
}

export async function create(projectId: string, input: NewWorkoutInput) {
  const { data } = await api.post<Workout>(`/projects/${projectId}/workouts`, input);
  return data;
}

export async function list(projectId: string) {
  const { data } = await api.get<Workout[]>(`/projects/${projectId}/workouts`);
  return data;
}

export async function get(projectId: string, workoutId: string) {
  const { data } = await api.get<Workout>(`/projects/${projectId}/workouts/${workoutId}`);
  return data;
}

export async function logSession(
  projectId: string,
  workoutId: string,
  input: { date: string; notes?: string | null; sets: Omit<ExerciseSet, "id" | "session_id">[] }
) {
  const { data } = await api.post<WorkoutSession>(
    `/projects/${projectId}/workouts/${workoutId}/sessions`,
    input
  );
  return data;
}

export async function listSessions(projectId: string, workoutId: string) {
  const { data } = await api.get<WorkoutSession[]>(
    `/projects/${projectId}/workouts/${workoutId}/sessions`
  );
  return data;
}

export interface ExerciseProgressPoint {
  session_id: string;
  session_date: string;
  best_set_load_kg: number;
  best_set_reps: number;
  total_volume_kg: number;
}

export interface ExerciseProgress {
  workout_exercise_id: string;
  exercise_name: string;
  history: ExerciseProgressPoint[];
  last_session: ExerciseProgressPoint | null;
  previous_session: ExerciseProgressPoint | null;
  load_delta_kg: number | null;
}

export async function getExerciseProgress(projectId: string, workoutId: string, exerciseId: string) {
  const { data } = await api.get<ExerciseProgress>(
    `/projects/${projectId}/workouts/${workoutId}/exercises/${exerciseId}/progress`
  );
  return data;
}
