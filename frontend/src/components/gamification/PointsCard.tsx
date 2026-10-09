import { Link } from "react-router-dom";

import { useGamification } from "@/hooks/useGamification";

const WEEKDAYS = ["D", "S", "T", "Q", "Q", "S", "S"];

/** Nível, barra de progresso, metas de hoje e os últimos 7 dias. */
export default function PointsCard() {
  const { data } = useGamification();
  if (!data) return null;

  const { today } = data;
  const pct = Math.min(100, Math.round((data.points_in_level / data.level_size) * 100));
  const maxDay = Math.max(30, ...data.last_7_days.map((d) => d.points));

  const goals = [
    { done: today.login.done, label: "Acesso do dia", points: today.login.points, to: null as string | null },
    {
      done: today.water.done,
      label:
        today.water.goal_liters != null
          ? `Meta de água (${(today.water.liters ?? 0).toFixed(1)}/${today.water.goal_liters} L)`
          : "Meta de água",
      points: today.water.points,
      to: "/hoje",
    },
    { done: today.workout.done, label: "Treino do dia", points: today.workout.points, to: "/treino" },
  ];

  return (
    <section className="card space-y-4" aria-label="Pontos e metas de hoje">
      <div className="flex items-center justify-between">
        <div>
          <p className="stat-label">Nível {data.level} · {data.level_title}</p>
          <p className="text-2xl font-bold">
            {data.total_points} <span className="text-sm font-normal text-foreground-muted">pontos</span>
          </p>
        </div>
        {data.points_today > 0 && (
          <span className="rounded-full bg-success/15 px-3 py-1 text-xs font-semibold text-success">
            +{data.points_today} hoje
          </span>
        )}
      </div>

      <div>
        <div
          className="h-2 overflow-hidden rounded-full bg-border"
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Progresso para o próximo nível"
        >
          <div className="h-full rounded-full bg-accent transition-all" style={{ width: `${pct}%` }} />
        </div>
        <p className="mt-1 text-xs text-foreground-muted">
          Faltam {data.points_to_next} pontos para o nível {data.level + 1}
        </p>
      </div>

      <ul className="space-y-1.5">
        {goals.map((g) => {
          const row = (
            <>
              <span className={g.done ? "text-success" : "text-foreground-muted"} aria-hidden>
                {g.done ? "✅" : "⬜"}
              </span>
              <span className={`flex-1 ${g.done ? "" : "text-foreground-muted"}`}>{g.label}</span>
              <span className={`text-xs font-semibold ${g.done ? "text-success" : "text-foreground-muted"}`}>
                {g.done ? "+" : ""}
                {g.points} pts
              </span>
            </>
          );
          return (
            <li key={g.label}>
              {g.to && !g.done ? (
                <Link to={g.to} className="flex items-center gap-2 rounded-lg text-sm hover:bg-border/40">
                  {row}
                </Link>
              ) : (
                <div className="flex items-center gap-2 text-sm">{row}</div>
              )}
            </li>
          );
        })}
      </ul>

      <div className="flex items-end justify-between gap-1.5" aria-label="Pontos nos últimos 7 dias">
        {data.last_7_days.map((d) => {
          const weekday = WEEKDAYS[new Date(`${d.day}T12:00:00`).getDay()];
          return (
            <div key={d.day} className="flex flex-1 flex-col items-center gap-1" title={`${d.day}: ${d.points} pts`}>
              <div className="flex h-12 w-full items-end">
                <div
                  className={`w-full rounded-t ${d.day === today.date ? "bg-accent" : "bg-accent/50"}`}
                  style={{ height: `${Math.max(d.points ? 8 : 3, (d.points / maxDay) * 100)}%`, opacity: d.points ? 1 : 0.25 }}
                />
              </div>
              <span className="text-[10px] text-foreground-muted">{weekday}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
