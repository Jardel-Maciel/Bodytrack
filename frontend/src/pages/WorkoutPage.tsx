import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import NewWorkoutForm from "@/components/workout/NewWorkoutForm";
import ExerciseThumb from "@/components/workout/ExerciseThumb";
import SessionLogger from "@/components/workout/SessionLogger";
import { useAuth } from "@/contexts/AuthContext";
import { useProject } from "@/contexts/ProjectContext";
import * as workoutService from "@/services/workoutService";

export default function WorkoutPage() {
  const { project, loading: projectLoading } = useProject();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showNewForm, setShowNewForm] = useState(false);
  const [loggingWorkoutId, setLoggingWorkoutId] = useState<string | null>(null);
  const [justLogged, setJustLogged] = useState<string | null>(null);

  const { data: workouts, isLoading } = useQuery({
    queryKey: ["workouts", project?.id],
    queryFn: () => workoutService.list(project!.id),
    enabled: Boolean(project),
  });

  if (projectLoading) return <p className="text-sm text-foreground-muted">Carregando…</p>;
  if (!project) return <p className="text-sm text-foreground-muted">Crie um projeto na tela Início primeiro.</p>;

  const loggingWorkout = workouts?.find((w) => w.id === loggingWorkoutId) ?? null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Treino</h1>
        {!showNewForm && (
          <button
            type="button"
            onClick={() => setShowNewForm(true)}
            className="rounded-xl bg-accent px-3 py-1.5 text-sm font-semibold text-white hover:bg-accent-hover"
          >
            + Novo treino
          </button>
        )}
      </div>

      {showNewForm && (
        <NewWorkoutForm
          onCancel={() => setShowNewForm(false)}
          onCreate={async (input) => {
            await workoutService.create(project.id, input);
            queryClient.invalidateQueries({ queryKey: ["workouts", project.id] });
            setShowNewForm(false);
          }}
        />
      )}

      {loggingWorkout && (
        <SessionLogger
          workout={loggingWorkout}
          onCancel={() => setLoggingWorkoutId(null)}
          onSubmit={async (input) => {
            await workoutService.logSession(project.id, loggingWorkout.id, input);
            queryClient.invalidateQueries({ queryKey: ["dashboard", project.id] });
            queryClient.invalidateQueries({ queryKey: ["gamification"] });
            setLoggingWorkoutId(null);
            setJustLogged(loggingWorkout.name);
          }}
        />
      )}

      {justLogged && (
        <p className="text-sm text-success">Sessão de "{justLogged}" registrada.</p>
      )}

      {isLoading && <p className="text-sm text-foreground-muted">Carregando treinos…</p>}

      {!isLoading && workouts?.length === 0 && !showNewForm && (
        <div className="card text-sm text-foreground-muted">
          Nenhum treino cadastrado ainda. Crie o primeiro com "+ Novo treino".
        </div>
      )}

      <div className="space-y-3">
        {workouts?.map((workout) => (
          <div key={workout.id} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">{workout.name}</p>
                {workout.muscle_group && (
                  <p className="text-xs text-foreground-muted">{workout.muscle_group}</p>
                )}
                {workout.created_by_trainer_id && workout.created_by_trainer_id !== user?.id && (
                  <p className="text-xs text-accent">Montado pelo seu personal</p>
                )}
              </div>
              <button
                type="button"
                onClick={() => setLoggingWorkoutId(workout.id)}
                className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium hover:border-accent"
              >
                Registrar sessão
              </button>
            </div>
            <ul className="mt-3 space-y-2">
              {workout.exercises.map((ex) => (
                <li key={ex.id} className="flex items-center gap-3 text-sm text-foreground-muted">
                  <ExerciseThumb exercise={ex} className="h-10 w-10" />
                  <span>
                    {ex.name}
                    {ex.target_sets && ex.target_reps ? ` — ${ex.target_sets}×${ex.target_reps}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
