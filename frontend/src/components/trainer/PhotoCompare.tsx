import { useEffect, useMemo, useState } from "react";

import type { PhotoAngle, ProgressPhoto } from "@/types";

import TrainerPhoto from "./TrainerPhoto";

const ANGLES: { value: PhotoAngle; label: string }[] = [
  { value: "front", label: "Frente" },
  { value: "side", label: "Lado" },
  { value: "back", label: "Costas" },
];

const formatDate = (iso: string) => iso.split("-").reverse().join("/");

const photoLabel = (p: ProgressPhoto) =>
  `${formatDate(p.date)}${p.week_number != null ? ` · Sem. ${p.week_number}` : ""}`;

interface Props {
  linkId: string;
  photos: ProgressPhoto[];
}

/**
 * Comparação "antes e depois" para o personal.
 * Por padrão compara a PRIMEIRA com a ÚLTIMA foto do ângulo escolhido (o que mais
 * interessa para ajustar o treino); dá para trocar qualquer uma das duas.
 * Dois modos: lado a lado, ou "cortina" (arrastar para revelar uma sobre a outra).
 */
export default function PhotoCompare({ linkId, photos }: Props) {
  const [angle, setAngle] = useState<PhotoAngle>("front");
  const [mode, setMode] = useState<"side" | "slider">("side");
  const [beforeId, setBeforeId] = useState<string>("");
  const [afterId, setAfterId] = useState<string>("");
  const [reveal, setReveal] = useState(50);

  const ofAngle = useMemo(
    () => photos.filter((p) => p.angle === angle).sort((a, b) => a.date.localeCompare(b.date)),
    [photos, angle]
  );

  // Ao trocar de ângulo (ou chegarem fotos novas), volta para primeira x última.
  useEffect(() => {
    setBeforeId(ofAngle[0]?.id ?? "");
    setAfterId(ofAngle.length > 1 ? ofAngle[ofAngle.length - 1].id : "");
  }, [ofAngle]);

  const before = ofAngle.find((p) => p.id === beforeId);
  const after = ofAngle.find((p) => p.id === afterId);

  const selectClass =
    "w-full rounded-lg border border-border bg-background-elevated px-2 py-1.5 text-xs outline-none focus:border-accent";

  return (
    <div className="card space-y-3">
      <p className="stat-label">Comparar fotos</p>

      <div className="flex gap-2">
        {ANGLES.map((a) => (
          <button
            key={a.value}
            type="button"
            onClick={() => setAngle(a.value)}
            className={`flex-1 rounded-lg border py-1.5 text-xs font-medium ${
              angle === a.value ? "border-accent bg-accent-muted text-white" : "border-border text-foreground-muted"
            }`}
          >
            {a.label}
          </button>
        ))}
      </div>

      {ofAngle.length < 2 ? (
        <p className="text-sm text-foreground-muted">
          {ofAngle.length === 0
            ? "O aluno ainda não enviou fotos deste ângulo."
            : "Só há uma foto deste ângulo — são necessárias duas para comparar."}
        </p>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-2">
            <label className="space-y-1 text-xs text-foreground-muted">
              Antes
              <select value={beforeId} onChange={(e) => setBeforeId(e.target.value)} className={selectClass}>
                {ofAngle.map((p) => (
                  <option key={p.id} value={p.id}>
                    {photoLabel(p)}
                  </option>
                ))}
              </select>
            </label>
            <label className="space-y-1 text-xs text-foreground-muted">
              Depois
              <select value={afterId} onChange={(e) => setAfterId(e.target.value)} className={selectClass}>
                {ofAngle.map((p) => (
                  <option key={p.id} value={p.id}>
                    {photoLabel(p)}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="flex gap-2 text-xs">
            {(
              [
                ["side", "Lado a lado"],
                ["slider", "Cortina"],
              ] as const
            ).map(([value, label]) => (
              <button
                key={value}
                type="button"
                onClick={() => setMode(value)}
                className={`rounded-full border px-3 py-1 ${
                  mode === value ? "border-accent text-accent" : "border-border text-foreground-muted"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {before && after && mode === "side" && (
            <div className="grid grid-cols-2 gap-2">
              {[
                { p: before, tag: "Antes" },
                { p: after, tag: "Depois" },
              ].map(({ p, tag }) => (
                <figure key={tag} className="overflow-hidden rounded-xl border border-border">
                  <div className="flex aspect-[3/4] items-center justify-center bg-black/20">
                    <TrainerPhoto linkId={linkId} photoId={p.id} alt={`${tag}: ${photoLabel(p)}`} />
                  </div>
                  <figcaption className="px-2 py-1 text-center text-xs text-foreground-muted">
                    {tag} · {photoLabel(p)}
                  </figcaption>
                </figure>
              ))}
            </div>
          )}

          {before && after && mode === "slider" && (
            <div className="space-y-2">
              <div className="relative mx-auto aspect-[3/4] max-w-xs overflow-hidden rounded-xl border border-border bg-black/20">
                <div className="absolute inset-0 flex items-center justify-center">
                  <TrainerPhoto linkId={linkId} photoId={after.id} alt={`Depois: ${photoLabel(after)}`} />
                </div>
                <div
                  className="absolute inset-0 flex items-center justify-center"
                  style={{ clipPath: `inset(0 ${100 - reveal}% 0 0)` }}
                >
                  <TrainerPhoto linkId={linkId} photoId={before.id} alt={`Antes: ${photoLabel(before)}`} />
                </div>
                <div
                  className="pointer-events-none absolute inset-y-0 w-0.5 bg-white/80"
                  style={{ left: `${reveal}%` }}
                />
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={reveal}
                onChange={(e) => setReveal(Number(e.target.value))}
                aria-label="Revelar foto de antes"
                className="w-full"
              />
              <p className="text-center text-xs text-foreground-muted">
                Esquerda: {photoLabel(before)} (antes) · Direita: {photoLabel(after)} (depois)
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
