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
  /** ID no catálogo de demonstração (null = sem imagem para este exercício). */
  catalog_id: string | null;
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
  /** Preenchido quando o treino foi montado por um personal. */
  created_by_trainer_id?: string | null;
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

export interface ExerciseCatalogItem {
  id: string;
  name: string;
  aliases: string[];
  primary_muscles: string[];
  secondary_muscles: string[];
  equipment: string;
  image_count: number;
  /** Vídeo em loop (mp4). null = ainda não existe, usa as imagens. */
  video_url: string | null;
}

// ---------------- área do personal ----------------

export interface InviteRead {
  link_id: string;
  invite_code: string;
  invite_expires_at: string;
  student_label: string | null;
}

export interface StudentSummary {
  link_id: string;
  status: "pending" | "active";
  display_name: string;
  invite_code: string | null;
  invite_expires_at: string | null;
  share_photos: boolean;
  share_progress: boolean;
  project_name: string | null;
  last_session_date: string | null;
  photos_count: number | null;
}

export interface MyTrainerLink {
  link_id: string;
  trainer_name: string;
  status: string;
  share_photos: boolean;
  share_progress: boolean;
  accepted_at: string | null;
}

export interface TrainerWorkout {
  id: string;
  name: string;
  muscle_group: string | null;
  notes: string | null;
  created_by_trainer_id: string | null;
  /** true = foi este personal que montou (só esses ele pode editar/excluir). */
  editable: boolean;
  exercises: (WorkoutExercise & { notes?: string | null })[];
}

export interface TrainerExerciseInput {
  id?: string;
  name: string;
  target_sets?: number | null;
  target_reps?: string | null;
  rest_seconds?: number | null;
  notes?: string | null;
}

export interface TrainerWorkoutInput {
  name: string;
  muscle_group?: string | null;
  notes?: string | null;
  exercises: TrainerExerciseInput[];
}

export interface StudentProgress {
  project_name: string | null;
  initial_weight_kg: number | null;
  weights: { date: string; weight_kg: number }[];
  latest_measurement_date: string | null;
  latest_waist_cm: number | null;
  sessions_last_30_days: number;
  recent_sessions: {
    session_id: string;
    date: string;
    workout_name: string;
    sets_count: number;
    total_volume_kg: number;
  }[];
}

// ---------------- avisos e chat ----------------

export interface AppNotice {
  id: string;
  kind: string;
  title: string;
  body: string | null;
  link_path: string | null;
  at: string;
  read: boolean;
}

export interface NoticeList {
  items: AppNotice[];
  unread_count: number;
}

export interface ChatMessage {
  id: string;
  sender_id: string;
  body: string;
  created_at: string;
  mine: boolean;
}

export interface ChatUnread {
  total: number;
  by_link: Record<string, number>;
}

// ---------------- gamificação ----------------

export interface TodayGoal {
  done: boolean;
  points: number;
}

export interface GamificationSummary {
  total_points: number;
  level: number;
  level_title: string;
  points_in_level: number;
  level_size: number;
  points_to_next: number;
  points_today: number;
  today: {
    date: string;
    login: TodayGoal;
    water: TodayGoal & { liters: number | null; goal_liters: number | null };
    workout: TodayGoal;
  };
  last_7_days: { day: string; points: number }[];
  recent: { kind: "login" | "water" | "workout"; day: string; points: number }[];
  rules: Record<string, number>;
}
