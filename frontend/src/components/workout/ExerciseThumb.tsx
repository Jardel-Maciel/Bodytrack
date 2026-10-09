import { useState } from "react";

import { useExerciseCatalog } from "@/hooks/useExerciseCatalog";
import type { WorkoutExercise } from "@/types";

import ExerciseDemoModal from "./ExerciseDemoModal";
import ExerciseImage from "./ExerciseImage";

interface Props {
  exercise: Pick<WorkoutExercise, "name" | "catalog_id">;
  className?: string;
}

/**
 * Miniatura (animada) do exercício; ao tocar, abre o modal grande com
 * músculos trabalhados. Não renderiza nada se o exercício não tem
 * correspondência no catálogo — a tela fica exatamente como era antes.
 */
export default function ExerciseThumb({ exercise, className = "h-12 w-12" }: Props) {
  const [open, setOpen] = useState(false);
  const { byId } = useExerciseCatalog();

  if (!exercise.catalog_id) return null;
  const item = byId.get(exercise.catalog_id);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label={`Ver demonstração de ${exercise.name}`}
        className={`${className} shrink-0 overflow-hidden rounded-lg border border-border bg-black hover:border-accent`}
      >
        <ExerciseImage
          catalogId={exercise.catalog_id}
          alt=""
          imageCount={item?.image_count ?? 2}
          className="h-full w-full object-cover"
        />
      </button>
      {open && item && (
        <ExerciseDemoModal exerciseName={exercise.name} item={item} onClose={() => setOpen(false)} />
      )}
    </>
  );
}
