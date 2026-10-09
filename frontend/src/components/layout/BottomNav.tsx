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

/** Barra de navegação inferior — visível apenas em telas pequenas (mobile-first). */
export default function BottomNav() {
  const { user } = useAuth();
  const items = user?.role === "trainer" ? [...baseItems.slice(0, -1), trainerItem, baseItems[baseItems.length - 1]] : baseItems;
  return (
    <nav className="fixed inset-x-0 bottom-0 z-20 border-t border-border bg-background-surface/95 backdrop-blur md:hidden">
      <ul className="flex items-stretch justify-around">
        {items.map((item) => (
          <li key={item.to} className="flex-1">
            <NavLink
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                clsx(
                  "flex flex-col items-center gap-1 py-2.5 text-xs font-medium",
                  isActive ? "text-accent" : "text-foreground-muted"
                )
              }
            >
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
