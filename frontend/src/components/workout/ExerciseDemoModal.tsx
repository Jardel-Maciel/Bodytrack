import { useEffect } from "react";

import { imageUrl } from "@/services/exerciseCatalogService";
import type { ExerciseCatalogItem } from "@/types";

import ExerciseImage from "./ExerciseImage";

interface Props {
  exerciseName: string;
  item: ExerciseCatalogItem;
  onClose: () => void;
}

export default function ExerciseDemoModal({ exerciseName, item, onClose }: Props) {
  // Fecha com ESC e trava a rolagem da página enquanto o modal está aberto.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = previousOverflow;
    };
  }, [onClose]);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Demonstração: ${exerciseName}`}
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 p-0 sm:items-center sm:p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md overflow-hidden rounded-t-2xl border border-border bg-background-elevated sm:rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {item.video_url ? (
          // Vídeo próprio: loop mudo (autoplay só funciona no celular se for muted + playsInline).
          <video
            src={item.video_url}
            poster={imageUrl(item.id, 0)}
            autoPlay
            loop
            muted
            playsInline
            controls
            preload="metadata"
            aria-label={`Vídeo de ${exerciseName}`}
            className="aspect-[4/3] w-full bg-black object-cover"
          />
        ) : (
          <ExerciseImage
            catalogId={item.id}
            alt={`Demonstração de ${exerciseName}`}
            imageCount={item.image_count}
            className="aspect-[4/3] w-full bg-black object-cover"
          />
        )}
        <div className="space-y-3 p-4">
          <div>
            <p className="font-semibold">{exerciseName}</p>
            <p className="text-xs text-foreground-muted">{item.equipment}</p>
          </div>

          <dl className="space-y-1 text-sm">
            <div className="flex gap-2">
              <dt className="w-24 shrink-0 text-foreground-muted">Principal</dt>
              <dd>{item.primary_muscles.join(", ") || "—"}</dd>
            </div>
            {item.secondary_muscles.length > 0 && (
              <div className="flex gap-2">
                <dt className="w-24 shrink-0 text-foreground-muted">Secundários</dt>
                <dd>{item.secondary_muscles.join(", ")}</dd>
              </div>
            )}
          </dl>

          <a
            href={`https://www.youtube.com/results?search_query=${encodeURIComponent(`como fazer ${exerciseName} execução correta`)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full rounded-xl bg-accent py-2 text-center text-sm font-semibold text-white hover:bg-accent-hover"
          >
            ▶ Ver vídeos no YouTube
          </a>

          <button
            type="button"
            onClick={onClose}
            className="w-full rounded-xl border border-border py-2 text-sm text-foreground-muted hover:border-accent"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
