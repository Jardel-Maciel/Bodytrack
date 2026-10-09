import { NavLink } from "react-router-dom";
import clsx from "clsx";

import { useAuth } from "@/contexts/AuthContext";

const baseItems = [
  { to: "/", label: "Início" },
  { to: "/hoje", label: "Hoje" },
  { to: "/treino", label: "Treino" },
  { to: "/evolucao", label: "Evolução" },
  { to: "/perfil", label: "Perfil" },
];

/** Só contas de personal ganham a aba "Alunos" (antes de "Perfil"). */
const trainerItem = { to: "/alunos", label: "Alunos" };

/** Sidebar — visível apenas em telas médias/grandes (desktop/tablet). */
export default function Sidebar() {
  const { user } = useAuth();
  const items = user?.role === "trainer" ? [...baseItems.slice(0, -1), trainerItem, baseItems[baseItems.length - 1]] : baseItems;
  return (
    <aside className="hidden w-56 shrink-0 border-r border-border bg-background-surface md:flex md:flex-col">
      <div className="px-5 py-6">
        <span className="text-lg font-semibold tracking-tight">BodyTrack</span>
      </div>
      <nav className="flex-1 px-3">
        <ul className="space-y-1">
          {items.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  clsx(
                    "block rounded-xl px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-accent-muted text-white"
                      : "text-foreground-muted hover:bg-background-elevated hover:text-foreground"
                  )
                }
              >
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
