import { useEffect, useState } from "react";

import * as trainerService from "@/services/trainerService";

interface Props {
  linkId: string;
  photoId: string;
  alt: string;
  className?: string;
}

/** Foto do aluno vista pelo personal: baixada com o token (blob) e liberada da memória ao sair da tela. */
export default function TrainerPhoto({ linkId, photoId, alt, className = "h-full w-full object-cover" }: Props) {
  const [url, setUrl] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let objectUrl: string | null = null;
    let cancelled = false;
    setUrl(null);
    setFailed(false);
    trainerService
      .getPhotoObjectUrl(linkId, photoId)
      .then((u) => {
        if (cancelled) return URL.revokeObjectURL(u);
        objectUrl = u;
        setUrl(u);
      })
      .catch(() => !cancelled && setFailed(true));
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [linkId, photoId]);

  if (failed) return <span className="p-2 text-center text-xs text-foreground-muted">Foto indisponível</span>;
  if (!url) return <span className="text-xs text-foreground-muted">Carregando…</span>;
  return <img src={url} alt={alt} className={className} />;
}
