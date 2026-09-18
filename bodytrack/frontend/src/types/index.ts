/**
 * Tipos TypeScript espelhando os modelos do backend (app/models/*.py).
 * Mantidos manualmente por enquanto; se o projeto crescer, considerar
 * gerar estes tipos automaticamente a partir do schema OpenAPI
 * (`openapi-typescript`) para eliminar duplicação.
 */

export interface Project {
  id: string;
  name: string;
  goal_description: string | null;
  start_date: string; // ISO date
  end_date: string;
  initial_weight_kg: number | null;
  status: "active" | "paused" | "finished" | "archived";
}

export interface DailyCheckin {
  id: string;
  project_id: string;
  date: string;
  weight_kg: number | null;
  water_liters: number | null;
  sleep_start: string | null;
  sleep_end: string | null;
  sleep_hours: number | null;
  sleep_quality: number | null;
  steps: number | null;
  trained_today: boolean;
  energy_level: number | null;
  mood_level: number | null;
  followed_diet: boolean | null;
  hit_protein_goal: boolean | null;
  avoided_ultraprocessed: boolean | null;
  portion_control: boolean | null;
  notes: string | null;
}

export interface BodyMeasurement {
  id: string;
  project_id: string;
  date: string;
  weight_kg: number | null;
  neck_cm: number | null;
  shoulders_cm: number | null;
  chest_cm: number | null;
  arm_right_cm: number | null;
  arm_left_cm: number | null;
  waist_cm: number | null;
  abdomen_cm: number | null;
  hip_cm: number | null;
  thigh_right_cm: number | null;
  thigh_left_cm: number | null;
  calf_right_cm: number | null;
  calf_left_cm: number | null;
}

export type PhotoAngle = "front" | "side" | "back";

export interface ProgressPhoto {
  id: string;
  project_id: string;
  date: string;
  week_number: number | null;
  angle: PhotoAngle;
  is_private: boolean;
}

export interface WorkoutExercise {
  id: string;
  name: string;
  order: number;
  target_sets: number | null;
  target_reps: string | null;
  rest_seconds: number | null;
}

export interface Workout {
  id: string;
  project_id: string;
  name: string;
  muscle_group: string | null;
  is_active: boolean;
  exercises: WorkoutExercise[];
}

export interface ExerciseSet {
  id: string;
  session_id: string;
  workout_exercise_id: string;
  set_number: number;
  reps: number;
  load_kg: number;
}

export interface WorkoutSession {
  id: string;
  workout_id: string;
  date: string;
  notes: string | null;
  sets: ExerciseSet[];
  total_volume_kg: number;
}

export type GoalType =
  | "weight"
  | "waist"
  | "training_frequency"
  | "water"
  | "sleep"
  | "steps"
  | "strength";

export interface Goal {
  id: string;
  project_id: string;
  type: GoalType;
  target_value: number;
  target_exercise_name: string | null;
  achieved: boolean;
}
