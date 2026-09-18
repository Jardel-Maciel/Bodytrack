import { useEffect, useState } from "react";

import * as photoService from "@/services/photoService";
import type { ProgressPhoto } from "@/types";

const ANGLE_LABEL: Record<string, string> = { front: "Frente", side: "Lado", back: "Costas" };

export default function PhotoThumbnail({ projectId, photo }: { projectId: string; photo: ProgressPhoto }) {
  const [url, setUrl] = useState<string | null>(null);

  useEffect(() => {
    let objectUrl: string | null = null;
    let cancelled = false;
    photoService.getPhotoObjectUrl(projectId, photo.id).then((u) => {
      if (cancelled) {
        URL.revokeObjectURL(u);
        return;
      }
      objectUrl = u;
      setUrl(u);
    });
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [projectId, photo.id]);

  return (
    <div className="overflow-hidden rounded-xl border border-border bg-background-elevated">
      <div className="flex aspect-[3/4] items-center justify-center bg-black/20">
        {url ? (
          <img src={url} alt={ANGLE_LABEL[photo.angle]} className="h-full w-full object-cover" />
        ) : (
          <span className="text-xs text-foreground-muted">Carregando…</span>
        )}
      </div>
      <div className="px-2 py-1.5 text-center text-xs text-foreground-muted">
        {ANGLE_LABEL[photo.angle] ?? photo.angle}
        {photo.week_number != null ? ` · Semana ${photo.week_number}` : ""}
      </div>
    </div>
  );
}
