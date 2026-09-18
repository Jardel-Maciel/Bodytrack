import { useQuery } from "@tanstack/react-query";

import CreateProjectForm from "@/components/onboarding/CreateProjectForm";
import MetricChart from "@/components/charts/MetricChart";
import StatCard from "@/components/ui/StatCard";
import { useProject } from "@/contexts/ProjectContext";
import * as dashboardService from "@/services/dashboardService";
import { fmtCm, fmtKg, fmtSigned } from "@/utils/format";

export default function HomePage() {
  const { project, loading: projectLoading } = useProject();

  const { data, isLoading } = useQuery({
    queryKey: ["dashboard", project?.id],
    queryFn: () => dashboardService.getDashboard(project!.id),
    enabled: Boolean(project),
  });

  if (projectLoading) {
    return <p className="text-sm text-foreground-muted">Carregando…</p>;
  }

  if (!project) {
    return <CreateProjectForm />;
  }

  if (isLoading || !data) {
    return <p className="text-sm text-foreground-muted">Carregando painel…</p>;
  }

  return (
    <div className="space-y-6">
      <header>
        <p className="stat-label">
          Semana {data.week_of_project} de {data.total_weeks}
        </p>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-background-elevated">
          <div
            className="h-full rounded-full bg-accent transition-all"
            style={{ width: `${Math.min(data.percent_complete, 100)}%` }}
          />
        </div>
        <p className="mt-2 text-sm text-foreground-muted">
          {data.percent_complete}% do projeto concluído · {data.days_remaining} dias restantes
        </p>
        <p className="text-sm text-foreground-muted">
          {data.streak_days} {data.streak_days === 1 ? "dia consecutivo" : "dias consecutivos"} registrados
        </p>
      </header>

      <section className="grid grid-cols-2 gap-3">
        <StatCard label="Peso atual" value={fmtKg(data.current_weight_kg)} />
        <StatCard label="Variação" value={fmtSigned(data.weight_variation_kg, "kg")} />
        <StatCard label="Cintura" value={fmtCm(data.waist_cm)} />
        <StatCard label="Consistência (7d)" value={`${data.consistency_pct_last_7_days}%`} />
      </section>

      <section className="grid grid-cols-2 gap-3">
        <StatCard label="Treinos esta semana" value={String(data.workouts_this_week)} />
        <StatCard label="IMC" value={data.bmi != null ? String(data.bmi) : "—"} hint="apenas referência" />
      </section>

      <MetricChart projectId={project.id} metric="weight_kg" title="Evolução do peso" unit=" kg" />
    </div>
  );
}
