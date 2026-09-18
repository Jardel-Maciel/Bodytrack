import { useQuery, useQueryClient } from "@tanstack/react-query";

import MetricChart from "@/components/charts/MetricChart";
import MeasurementForm from "@/components/measurements/MeasurementForm";
import PhotoThumbnail from "@/components/photos/PhotoThumbnail";
import PhotoUploadForm from "@/components/photos/PhotoUploadForm";
import { useProject } from "@/contexts/ProjectContext";
import * as measurementService from "@/services/measurementService";
import * as photoService from "@/services/photoService";
import { fmtCm } from "@/utils/format";

const FIELD_LABELS: Record<string, string> = {
  waist_cm: "Cintura",
  abdomen_cm: "Abdômen",
  hip_cm: "Quadril",
  chest_cm: "Peito",
  arm_right_cm: "Braço direito",
  arm_left_cm: "Braço esquerdo",
  thigh_right_cm: "Coxa direita",
  thigh_left_cm: "Coxa esquerda",
};

export default function EvolutionPage() {
  const { project, loading: projectLoading } = useProject();
  const queryClient = useQueryClient();

  const { data: progress } = useQuery({
    queryKey: ["measurement-progress", project?.id],
    queryFn: () => measurementService.progress(project!.id),
    enabled: Boolean(project),
  });

  const { data: photos } = useQuery({
    queryKey: ["photos", project?.id],
    queryFn: () => photoService.list(project!.id),
    enabled: Boolean(project),
  });

  if (projectLoading) return <p className="text-sm text-foreground-muted">Carregando…</p>;
  if (!project) return <p className="text-sm text-foreground-muted">Crie um projeto na tela Início primeiro.</p>;

  const highlighted = progress?.filter((f) => FIELD_LABELS[f.field] && f.variation != null) ?? [];

  return (
    <div className="space-y-5">
      <h1 className="text-lg font-semibold">Minha evolução</h1>

      {highlighted.length > 0 && (
        <section className="grid grid-cols-2 gap-3">
          {highlighted.map((f) => (
            <div key={f.field} className="card">
              <p className="stat-label">{FIELD_LABELS[f.field]}</p>
              <p className="stat-value">{fmtCm(f.current_value)}</p>
              <p className="mt-1 text-xs text-foreground-muted">
                {fmtCm(f.initial_value)} → {fmtCm(f.current_value)} ({f.variation! > 0 ? "+" : ""}
                {f.variation} cm)
              </p>
            </div>
          ))}
        </section>
      )}

      <MeasurementForm
        projectId={project.id}
        onSaved={() => {
          queryClient.invalidateQueries({ queryKey: ["measurement-progress", project.id] });
          queryClient.invalidateQueries({ queryKey: ["series", project.id] });
        }}
      />

      <MetricChart projectId={project.id} metric="waist_cm" title="Evolução da cintura" unit=" cm" />
      <MetricChart projectId={project.id} metric="abdomen_cm" title="Evolução do abdômen" unit=" cm" />
      <MetricChart projectId={project.id} metric="hip_cm" title="Evolução do quadril" unit=" cm" />
      <MetricChart
        projectId={project.id}
        metric="training_frequency"
        title="Frequência de treino (por semana)"
        kind="bar"
        defaultPeriod="project"
      />
      <MetricChart projectId={project.id} metric="sleep_hours" title="Sono" unit="h" />
      <MetricChart projectId={project.id} metric="water_liters" title="Consumo de água" unit=" L" />

      <PhotoUploadForm
        onUpload={async (input) => {
          await photoService.upload(project.id, input);
          queryClient.invalidateQueries({ queryKey: ["photos", project.id] });
        }}
      />

      {photos && photos.length > 0 && (
        <section>
          <p className="stat-label mb-2">Fotos de progresso</p>
          <div className="grid grid-cols-3 gap-2">
            {photos.map((photo) => (
              <PhotoThumbnail key={photo.id} projectId={project.id} photo={photo} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
