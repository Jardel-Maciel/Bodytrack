import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import ProfileEditForm from "@/components/profile/ProfileEditForm";
import { useAuth } from "@/contexts/AuthContext";
import { useProject } from "@/contexts/ProjectContext";
import * as goalService from "@/services/goalService";
import * as reportService from "@/services/reportService";
import type { GoalType } from "@/types";

const GOAL_TYPE_LABELS: Record<GoalType, string> = {
  weight: "Peso",
  waist: "Cintura",
  training_frequency: "Treinos/semana",
  water: "Água (L/dia)",
  sleep: "Sono (h)",
  steps: "Passos/dia",
  strength: "Força (exercício)",
};

export default function ProfilePage() {
  const { logout } = useAuth();
  const { project } = useProject();
  const queryClient = useQueryClient();
  const [exporting, setExporting] = useState(false);

  const { data: goals } = useQuery({
    queryKey: ["goals", project?.id],
    queryFn: () => goalService.list(project!.id),
    enabled: Boolean(project),
  });

  const { data: achievements } = useQuery({
    queryKey: ["achievements", project?.id],
    queryFn: () => reportService.listAchievements(project!.id),
    enabled: Boolean(project),
  });

  const handleExport = async (format: "csv" | "json") => {
    if (!project) return;
    setExporting(true);
    try {
      await reportService.downloadExport(project.id, format);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="space-y-5">
      <h1 className="text-lg font-semibold">Perfil</h1>

      <ProfileEditForm />

      {project && (
        <div className="card">
          <p className="stat-label">Projeto ativo</p>
          <p className="font-medium">{project.name}</p>
          <p className="text-xs text-foreground-muted">
            {project.start_date} → {project.end_date}
          </p>
        </div>
      )}

      {project && (
        <div className="card space-y-2">
          <p className="stat-label">Exportar meus dados</p>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={exporting}
              onClick={() => handleExport("csv")}
              className="flex-1 rounded-xl border border-border py-2 text-sm hover:border-accent disabled:opacity-60"
            >
              CSV
            </button>
            <button
              type="button"
              disabled={exporting}
              onClick={() => handleExport("json")}
              className="flex-1 rounded-xl border border-border py-2 text-sm hover:border-accent disabled:opacity-60"
            >
              JSON
            </button>
          </div>
        </div>
      )}

      {project && goals && (
        <div className="card space-y-2">
          <p className="stat-label">Metas</p>
          {goals.length === 0 && <p className="text-sm text-foreground-muted">Nenhuma meta definida ainda.</p>}
          {goals.map((goal) => (
            <div key={goal.id} className="flex items-center justify-between text-sm">
              <span>
                {GOAL_TYPE_LABELS[goal.type]}: {goal.target_value}
                {goal.target_exercise_name ? ` (${goal.target_exercise_name})` : ""}
              </span>
              <label className="flex items-center gap-1 text-xs text-foreground-muted">
                <input
                  type="checkbox"
                  checked={goal.achieved}
                  onChange={async (e) => {
                    await goalService.update(project.id, goal.id, { achieved: e.target.checked });
                    queryClient.invalidateQueries({ queryKey: ["goals", project.id] });
                  }}
                />
                atingida
              </label>
            </div>
          ))}
        </div>
      )}

      {project && achievements && achievements.length > 0 && (
        <div className="card space-y-1">
          <p className="stat-label">Conquistas</p>
          {achievements.map((a) => (
            <p key={a.code} className="text-sm">
              🏆 {a.label}
            </p>
          ))}
        </div>
      )}

      <button
        type="button"
        onClick={logout}
        className="w-full rounded-xl border border-danger py-2.5 text-sm font-medium text-danger hover:bg-danger/10"
      >
        Sair
      </button>
    </div>
  );
}
