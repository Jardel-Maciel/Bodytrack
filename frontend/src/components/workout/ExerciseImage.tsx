import { useEffect, useState } from "react";

import { imageUrl } from "@/services/exerciseCatalogService";

interface Props {
  catalogId: string;
  alt: string;
  imageCount?: number;
  className?: string;
  /** Alterna entre posição inicial e final (parece uma animação do movimento). */
  animate?: boolean;
}

/**
 * Mostra a demonstração do exercício. O dataset traz 2 fotos (início e fim
 * do movimento); alternando entre elas a cada ~900ms dá a noção do movimento
 * sem precisar de GIF/vídeo (muito mais leve). Se a imagem não carregar
 * (offline sem cache, arquivo ausente), o componente some em vez de mostrar
 * um ícone quebrado.
 */
export default function ExerciseImage({ catalogId, alt, imageCount = 2, className, animate = true }: Props) {
  const [frame, setFrame] = useState(0);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    if (!animate || imageCount < 2) return;
    // Respeita quem pediu menos movimento no sistema (acessibilidade).
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return;
    const timer = window.setInterval(() => setFrame((f) => (f + 1) % imageCount), 900);
    return () => window.clearInterval(timer);
  }, [animate, imageCount]);

  if (failed) return null;

  return (
    <img
      src={imageUrl(catalogId, frame)}
      alt={alt}
      loading="lazy"
      decoding="async"
      onError={() => setFailed(true)}
      className={className}
    />
  );
}
