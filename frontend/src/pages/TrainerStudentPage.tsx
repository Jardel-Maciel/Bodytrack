import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import ChatPanel from "@/components/chat/ChatPanel";
import PhotoCompare from "@/components/trainer/PhotoCompare";
import ProgressSummary from "@/components/trainer/ProgressSummary";
import TrainerPhoto from "@/components/trainer/TrainerPhoto";
import TrainerWorkoutEditor from "@/components/trainer/TrainerWorkoutEditor";
import ExerciseThumb from "@/components/workout/ExerciseThumb";
import { useAuth } from "@/contexts/AuthContext";
import { useUnread } from "@/hooks/useUnread";
import * as trainerService from "@/services/trainerService";
import type { TrainerWorkout, TrainerWorkoutInput } from "@/types";

type Tab = "workouts" | "photos" | "progress" | "chat";
const TABS: { id: Tab; label: string }[] = [
  { id: "workouts", label: "Treinos" },
  { id: "photos", label: "Fotos" },
  { id: "progress", label: "Evolução" },
  { id: "chat", label: "Chat" },
];

export default function TrainerStudentPage() {
  const { linkId = "" } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<Tab>("workouts");
  const [editing, setEditing] = useState<TrainerWorkout | "new" | null>(null);
  const [editorError, setEditorError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const isTrainer = user?.role === "trainer";
  const { chatByLink } = useUnread();
  const unreadChat = chatByLink[linkId] ?? 0;

  const { data: students } = useQuery({
    queryKey: ["trainer-students"],
    queryFn: trainerService.listStudents,
    enabled: isTrainer,
  });
  const student = students?.find((s) => s.link_id === linkId);

  const workoutsKey = ["trainer-workouts", linkId];
  const { data: workouts, isLoading: loadingWorkouts } = useQuery({
    queryKey: workoutsKey,
    queryFn: () => trainerService.listWorkouts(linkId),
    enabled: isTrainer && Boolean(student),
  });

  const { data: photos } = useQuery({
    queryKey: ["trainer-photos", linkId],
    queryFn: () => trainerService.listPhotos(linkId),
    enabled: isTrainer && Boolean(student?.share_photos) && tab === "photos",
  });

  const { data: progress } = useQuery({
    queryKey: ["trainer-progress", linkId],
    queryFn: () => trainerService.getProgress(linkId),
    enabled: isTrainer && Boolean(student?.share_progress) && tab === "progress",
  });

  const save = useMutation({
    mutationFn: (input: TrainerWorkoutInput) =>
      editing && editing !== "new"
        ? trainerService.updateWorkout(linkId, editing.id, input)
        : trainerService.createWorkout(linkId, input),
    onSuccess: () => {
      setEditing(null);
      setEditorError(null);
      setNotice("Treino salvo. O aluno já vê a versão atualizada.");
      queryClient.invalidateQueries({ queryKey: workoutsKey });
    },
    onError: (err) => setEditorError(trainerService.errorMessage(err, "Não foi possível salvar o treino.")),
  });

  const remove = useMutation({
    mutationFn: (workoutId: string) => trainerService.deleteWorkout(linkId, workoutId),
    onSuccess: (result) => {
      setNotice(
        result === "archived"
          ? "O aluno já tem histórico neste treino, então ele foi arquivado (sai da lista, mas o histórico fica)."
          : "Treino excluído."
      );
      queryClient.invalidateQueries({ queryKey: workoutsKey });
    },
    onError: (err) => setNotice(trainerService.errorMessage(err, "Não foi possível excluir o treino.")),
  });

  const endLink = useMutation({
    mutationFn: () => trainerService.removeStudent(linkId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["trainer-students"] });
      navigate("/alunos", { replace: true });
    },
  });

  if (!isTrainer) return <div className="card text-sm text-foreground-muted">Área exclusiva para personal.</div>;
  if (students && !student) {
    return (
      <div className="space-y-3">
        <Link to="/alunos" className="text-sm text-accent">‹ Alunos</Link>
        <div className="card text-sm text-foreground-muted">Aluno não encontrado ou vínculo encerrado.</div>
      </div>
    );
  }
  if (!student) return <p className="text-sm text-foreground-muted">Carregando…</p>;

  return (
    <div className="space-y-4">
      <Link to="/alunos" className="text-sm text-accent">‹ Alunos</Link>
      <div>
        <h1 className="text-lg font-semibold">{student.display_name}</h1>
        <p className="text-xs text-foreground-muted">{student.project_name ?? "Sem projeto ativo"}</p>
      </div>

      <div className="flex gap-1 rounded-xl border border-border p-1" role="tablist">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
            className={`flex-1 rounded-lg py-1.5 text-sm font-medium ${
              tab === t.id ? "bg-accent-muted text-white" : "text-foreground-muted"
            }`}
          >
            {t.label}
            {t.id === "chat" && unreadChat > 0 && tab !== "chat" && (
              <span className="ml-1 rounded-full bg-danger px-1.5 text-[10px] font-bold text-white">{unreadChat}</span>
            )}
          </button>
        ))}
      </div>

      {notice && <p className="rounded-xl border border-border px-3 py-2 text-xs text-foreground-muted">{notice}</p>}

      {tab === "workouts" && (
        <div className="space-y-3">
          {editing ? (
            <TrainerWorkoutEditor
              key={editing === "new" ? "new" : editing.id}
              initial={editing === "new" ? undefined : editing}
              saving={save.isPending}
              error={editorError}
              onSave={(input) => save.mutate(input)}
              onCancel={() => {
                setEditing(null);
                setEditorError(null);
              }}
            />
          ) : (
            <button
              type="button"
              onClick={() => {
                setNotice(null);
                setEditing("new");
              }}
              className="w-full rounded-xl bg-accent py-2.5 text-sm font-semibold text-white hover:bg-accent-hover"
            >
              + Novo treino para {student.display_name.split(" ")[0]}
            </button>
          )}

          {loadingWorkouts && <p className="text-sm text-foreground-muted">Carregando treinos…</p>}
          {!loadingWorkouts && workouts?.length === 0 && !editing && (
            <div className="card text-sm text-foreground-muted">Nenhum treino montado ainda para este aluno.</div>
          )}

          {workouts?.map((w) => (
            <div key={w.id} className="card space-y-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-medium">{w.name}</p>
                  <p className="text-xs text-foreground-muted">
                    {[w.muscle_group, w.editable ? "montado por você" : "criado pelo aluno"].filter(Boolean).join(" · ")}
                  </p>
                </div>
                {w.editable && !editing && (
                  <div className="flex shrink-0 gap-3 text-xs">
                    <button
                      type="button"
                      onClick={() => {
                        setNotice(null);
                        setEditing(w);
                      }}
                      className="text-accent"
                    >
                      editar
                    </button>
                    <button
                      type="button"
                      onClick={() => window.confirm(`Excluir "${w.name}"?`) && remove.mutate(w.id)}
                      className="text-danger"
                    >
                      excluir
                    </button>
                  </div>
                )}
              </div>
              {w.notes && <p className="text-xs text-foreground-muted">{w.notes}</p>}
              <ul className="space-y-2">
                {w.exercises.map((ex) => (
                  <li key={ex.id} className="flex items-center gap-3 text-sm text-foreground-muted">
                    <ExerciseThumb exercise={ex} className="h-10 w-10" />
                    <span>
                      {ex.name}
                      {ex.target_sets && ex.target_reps ? ` — ${ex.target_sets}×${ex.target_reps}` : ""}
                      {ex.rest_seconds ? ` · ${ex.rest_seconds}s` : ""}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}

      {tab === "chat" && <ChatPanel linkId={linkId} otherName={student.display_name.split(" ")[0]} />}

      {tab === "photos" &&
        (!student.share_photos ? (
          <div className="card text-sm text-foreground-muted">
            O aluno não compartilhou as fotos com você. Ele pode liberar em <b>Perfil › Meu personal</b>.
          </div>
        ) : !photos ? (
          <p className="text-sm text-foreground-muted">Carregando fotos…</p>
        ) : (
          <div className="space-y-4">
            <PhotoCompare linkId={linkId} photos={photos} />
            <div className="card space-y-2">
              <p className="stat-label">Todas as fotos ({photos.length})</p>
              <div className="grid grid-cols-3 gap-2">
                {[...photos].reverse().map((p) => (
                  <figure key={p.id} className="overflow-hidden rounded-lg border border-border">
                    <div className="flex aspect-[3/4] items-center justify-center bg-black/20">
                      <TrainerPhoto linkId={linkId} photoId={p.id} alt={`Foto ${p.angle} de ${p.date}`} />
                    </div>
                    <figcaption className="px-1 py-1 text-center text-[10px] text-foreground-muted">
                      {p.date.split("-").reverse().slice(0, 2).join("/")} · {{ front: "Frente", side: "Lado", back: "Costas" }[p.angle]}
                    </figcaption>
                  </figure>
                ))}
              </div>
            </div>
          </div>
        ))}

      {tab === "progress" &&
        (!student.share_progress ? (
          <div className="card text-sm text-foreground-muted">
            O aluno não compartilhou a evolução (peso, medidas e sessões) com você. Ele pode liberar em{" "}
            <b>Perfil › Meu personal</b>.
          </div>
        ) : !progress ? (
          <p className="text-sm text-foreground-muted">Carregando evolução…</p>
        ) : (
          <ProgressSummary progress={progress} />
        ))}

      <button
        type="button"
        onClick={() =>
          window.confirm(`Encerrar o acompanhamento de ${student.display_name}? Os treinos que você montou continuam com o aluno.`) &&
          endLink.mutate()
        }
        className="w-full rounded-xl border border-danger py-2 text-sm text-danger hover:bg-danger/10"
      >
        Encerrar acompanhamento
      </button>
    </div>
  );
}
