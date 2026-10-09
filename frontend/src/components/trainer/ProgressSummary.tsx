import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { StudentProgress } from "@/types";

const formatDate = (iso: string) => iso.split("-").reverse().slice(0, 2).join("/");

/** Resumo para o personal ajustar o treino: frequência, cargas recentes e peso. */
export default function ProgressSummary({ progress }: { progress: StudentProgress }) {
  const { weights, recent_sessions: sessions } = progress;
  const first = weights[0]?.weight_kg ?? progress.initial_weight_kg;
  const last = weights[weights.length - 1]?.weight_kg;
  const delta = first != null && last != null ? last - first : null;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-2">
        <div className="card text-center">
          <p className="text-xl font-semibold">{progress.sessions_last_30_days}</p>
          <p className="text-[11px] text-foreground-muted">treinos em 30 dias</p>
        </div>
        <div className="card text-center">
          <p className="text-xl font-semibold">{last != null ? `${last.toFixed(1)} kg` : "—"}</p>
          <p className="text-[11px] text-foreground-muted">peso atual</p>
        </div>
        <div className="card text-center">
          <p className="text-xl font-semibold">
            {delta != null ? `${delta > 0 ? "+" : ""}${delta.toFixed(1)} kg` : "—"}
          </p>
          <p className="text-[11px] text-foreground-muted">variação</p>
        </div>
      </div>

      {progress.latest_waist_cm != null && (
        <p className="text-sm text-foreground-muted">
          Última cintura: <span className="text-foreground">{progress.latest_waist_cm} cm</span>
          {progress.latest_measurement_date ? ` (${formatDate(progress.latest_measurement_date)})` : ""}
        </p>
      )}

      {weights.length >= 2 && (
        <div className="card">
          <p className="stat-label mb-2">Peso</p>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={weights.map((w) => ({ ...w, label: formatDate(w.date) }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
                <XAxis dataKey="label" tick={{ fontSize: 10 }} />
                <YAxis domain={["dataMin - 1", "dataMax + 1"]} tick={{ fontSize: 10 }} width={32} />
                <Tooltip />
                <Line type="monotone" dataKey="weight_kg" name="kg" stroke="#6366f1" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div className="card space-y-2">
        <p className="stat-label">Últimas sessões</p>
        {sessions.length === 0 && <p className="text-sm text-foreground-muted">O aluno ainda não registrou sessões.</p>}
        {sessions.map((s) => (
          <div key={s.session_id} className="flex items-center justify-between text-sm">
            <span>
              {s.workout_name}
              <span className="ml-2 text-xs text-foreground-muted">{s.date.split("-").reverse().join("/")}</span>
            </span>
            <span className="text-xs text-foreground-muted">
              {s.sets_count} séries · {Math.round(s.total_volume_kg)} kg
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
