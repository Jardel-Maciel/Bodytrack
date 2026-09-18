import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { useProject } from "@/contexts/ProjectContext";
import * as checkinService from "@/services/checkinService";
import { todayIso } from "@/utils/format";

const SCALE_5 = [1, 2, 3, 4, 5];

const DIET_FLAGS: { key: "followed_diet" | "hit_protein_goal" | "avoided_ultraprocessed" | "portion_control"; label: string }[] = [
  { key: "followed_diet", label: "Segui a alimentação" },
  { key: "hit_protein_goal", label: "Bati minha meta de proteína" },
  { key: "avoided_ultraprocessed", label: "Evitei ultraprocessados" },
  { key: "portion_control", label: "Mantive controle das porções" },
];

export default function TodayPage() {
  const { project, loading: projectLoading } = useProject();
  const queryClient = useQueryClient();

  const [loaded, setLoaded] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<number | null>(null);
  const [offlineQueued, setOfflineQueued] = useState(false);

  const [weight, setWeight] = useState("");
  const [water, setWater] = useState(0);
  const [sleepHours, setSleepHours] = useState("");
  const [sleepQuality, setSleepQuality] = useState<number | null>(null);
  const [steps, setSteps] = useState("");
  const [trained, setTrained] = useState(false);
  const [energy, setEnergy] = useState<number | null>(null);
  const [mood, setMood] = useState<number | null>(null);
  const [diet, setDiet] = useState<Record<string, boolean>>({});
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (!project) return;
    checkinService.getByDate(project.id, todayIso()).then((existing) => {
      if (existing) {
        setWeight(existing.weight_kg?.toString() ?? "");
        setWater(existing.water_liters ?? 0);
        setSleepHours(existing.sleep_hours?.toString() ?? "");
        setSleepQuality(existing.sleep_quality ?? null);
        setSteps(existing.steps?.toString() ?? "");
        setTrained(existing.trained_today);
        setEnergy(existing.energy_level ?? null);
        setMood(existing.mood_level ?? null);
        setDiet({
          followed_diet: existing.followed_diet ?? false,
          hit_protein_goal: existing.hit_protein_goal ?? false,
          avoided_ultraprocessed: existing.avoided_ultraprocessed ?? false,
          portion_control: existing.portion_control ?? false,
        });
        setNotes(existing.notes ?? "");
      }
      setLoaded(true);
    });
  }, [project]);

  if (projectLoading || (project && !loaded)) {
    return <p className="text-sm text-foreground-muted">Carregando…</p>;
  }
  if (!project) {
    return <p className="text-sm text-foreground-muted">Crie um projeto na tela Início antes de registrar o check-in.</p>;
  }

  const handleSave = async () => {
    setSaving(true);
    try {
      const result = await checkinService.upsert(project.id, {
        date: todayIso(),
        weight_kg: weight ? Number(weight) : null,
        water_liters: water || null,
        sleep_hours: sleepHours ? Number(sleepHours) : null,
        sleep_quality: sleepQuality,
        sleep_start: null,
        sleep_end: null,
        steps: steps ? Number(steps) : null,
        trained_today: trained,
        energy_level: energy,
        mood_level: mood,
        followed_diet: diet.followed_diet ?? null,
        hit_protein_goal: diet.hit_protein_goal ?? null,
        avoided_ultraprocessed: diet.avoided_ultraprocessed ?? null,
        portion_control: diet.portion_control ?? null,
        notes: notes || null,
      });
      setOfflineQueued(result.queued);
      setSavedAt(Date.now());
      if (!result.queued) {
        queryClient.invalidateQueries({ queryKey: ["dashboard", project.id] });
        queryClient.invalidateQueries({ queryKey: ["series", project.id] });
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-5 pb-6">
      <h1 className="text-lg font-semibold">Check-in de hoje</h1>

      <div className="card space-y-3">
        <p className="stat-label">Peso</p>
        <input
          type="number"
          step="0.1"
          value={weight}
          onChange={(e) => setWeight(e.target.value)}
          placeholder="kg"
          className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
        />
      </div>

      <div className="card space-y-3">
        <div className="flex items-center justify-between">
          <p className="stat-label">Água</p>
          <p className="text-sm text-foreground-muted">{water.toFixed(2)} L</p>
        </div>
        <div className="flex gap-2">
          {[0.25, 0.5, 1].map((amount) => (
            <button
              key={amount}
              type="button"
              onClick={() => setWater((w) => Math.round((w + amount) * 100) / 100)}
              className="flex-1 rounded-xl border border-border bg-background-elevated py-2 text-sm font-medium hover:border-accent"
            >
              +{amount * 1000 >= 1000 ? `${amount} L` : `${amount * 1000} ml`}
            </button>
          ))}
          <button
            type="button"
            onClick={() => setWater(0)}
            className="rounded-xl border border-border px-3 py-2 text-sm text-foreground-muted hover:border-accent"
          >
            zerar
          </button>
        </div>
      </div>

      <div className="card space-y-3">
        <p className="stat-label">Sono</p>
        <div className="grid grid-cols-2 gap-3">
          <input
            type="number"
            step="0.5"
            value={sleepHours}
            onChange={(e) => setSleepHours(e.target.value)}
            placeholder="horas dormidas"
            className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
          />
          <ScalePicker value={sleepQuality} onChange={setSleepQuality} label="qualidade" />
        </div>
      </div>

      <div className="card space-y-3">
        <p className="stat-label">Treino e passos</p>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={trained} onChange={(e) => setTrained(e.target.checked)} />
          Treinei hoje
        </label>
        <input
          type="number"
          value={steps}
          onChange={(e) => setSteps(e.target.value)}
          placeholder="passos"
          className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
        />
      </div>

      <div className="card space-y-3">
        <ScalePicker value={energy} onChange={setEnergy} label="Energia" />
        <ScalePicker value={mood} onChange={setMood} label="Humor" />
      </div>

      <div className="card space-y-2">
        <p className="stat-label">Alimentação</p>
        {DIET_FLAGS.map(({ key, label }) => (
          <label key={key} className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={Boolean(diet[key])}
              onChange={(e) => setDiet((prev) => ({ ...prev, [key]: e.target.checked }))}
            />
            {label}
          </label>
        ))}
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Observações (opcional)"
          rows={3}
          className="mt-2 w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
        />
      </div>

      <button
        type="button"
        onClick={handleSave}
        disabled={saving}
        className="w-full rounded-xl bg-accent py-3 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60"
      >
        {saving ? "Salvando…" : "Salvar check-in"}
      </button>
      {savedAt && !offlineQueued && <p className="text-center text-xs text-success">Check-in salvo.</p>}
      {savedAt && offlineQueued && (
        <p className="text-center text-xs text-warning">
          Sem conexão agora — o check-in foi guardado no aparelho e será enviado automaticamente quando a internet voltar.
        </p>
      )}
    </div>
  );
}

function ScalePicker({
  value,
  onChange,
  label,
}: {
  value: number | null;
  onChange: (v: number) => void;
  label: string;
}) {
  return (
    <div>
      <p className="mb-1 text-xs text-foreground-muted">{label}</p>
      <div className="flex gap-1">
        {SCALE_5.map((n) => (
          <button
            key={n}
            type="button"
            onClick={() => onChange(n)}
            className={`h-8 flex-1 rounded-lg text-sm font-medium ${
              value === n ? "bg-accent text-white" : "bg-background-elevated text-foreground-muted"
            }`}
          >
            {n}
          </button>
        ))}
      </div>
    </div>
  );
}
