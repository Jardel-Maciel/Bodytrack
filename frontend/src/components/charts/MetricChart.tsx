import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import clsx from "clsx";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import * as seriesService from "@/services/seriesService";

const PERIODS = [
  { value: "7d", label: "7d" },
  { value: "30d", label: "30d" },
  { value: "90d", label: "90d" },
  { value: "project", label: "Projeto" },
];

interface Props {
  projectId: string;
  metric: string;
  title: string;
  unit?: string;
  kind?: "line" | "bar";
  defaultPeriod?: string;
}

/**
 * Um gráfico genérico reutilizado pelos ~9 gráficos pedidos no
 * briefing (peso, cintura, abdômen, quadril, sono, água...): a série
 * de dados muda (prop `metric`), o componente visual não. Série única
 * por gráfico, então não precisa de legenda — o título já identifica o
 * que está sendo mostrado (ver skill de dataviz: "single series needs
 * no legend box").
 */
export default function MetricChart({ projectId, metric, title, unit, kind = "line", defaultPeriod = "30d" }: Props) {
  const [period, setPeriod] = useState(defaultPeriod);

  const { data, isLoading } = useQuery({
    queryKey: ["series", projectId, metric, period],
    queryFn: () => seriesService.getSeries(projectId, metric, period),
  });

  return (
    <div className="card">
      <div className="mb-3 flex items-center justify-between">
        <p className="stat-label">{title}</p>
        <div className="flex gap-1">
          {PERIODS.map((p) => (
            <button
              key={p.value}
              type="button"
              onClick={() => setPeriod(p.value)}
              className={clsx(
                "rounded-lg px-2 py-1 text-xs font-medium transition-colors",
                period === p.value
                  ? "bg-accent text-white"
                  : "text-foreground-muted hover:bg-background-elevated"
              )}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="flex h-40 items-center justify-center text-sm text-foreground-muted">
          Carregando…
        </div>
      ) : !data || data.points.length === 0 ? (
        <div className="flex h-40 items-center justify-center text-sm text-foreground-muted">
          Sem dados neste período ainda.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={180}>
          {kind === "bar" ? (
            <BarChart data={data.points}>
              <CartesianGrid strokeDasharray="3 3" stroke="#242C3D" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#9AA4B2" }} tickFormatter={(d) => d.slice(5)} />
              <YAxis tick={{ fontSize: 11, fill: "#9AA4B2" }} allowDecimals={false} width={28} />
              <Tooltip
                contentStyle={{ background: "#1B2233", border: "1px solid #242C3D", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#F5F7FA" }}
                formatter={(value: number) => [`${value}${unit ?? ""}`, title]}
              />
              <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} maxBarSize={28} />
            </BarChart>
          ) : (
            <LineChart data={data.points}>
              <CartesianGrid strokeDasharray="3 3" stroke="#242C3D" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#9AA4B2" }} tickFormatter={(d) => d.slice(5)} />
              <YAxis tick={{ fontSize: 11, fill: "#9AA4B2" }} domain={["auto", "auto"]} width={36} />
              <Tooltip
                contentStyle={{ background: "#1B2233", border: "1px solid #242C3D", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#F5F7FA" }}
                formatter={(value: number) => [`${value}${unit ?? ""}`, title]}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ r: 3, fill: "#3B82F6", strokeWidth: 0 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      )}
    </div>
  );
}
