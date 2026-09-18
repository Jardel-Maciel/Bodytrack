import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import BottomNav from "./BottomNav";
import { useOfflineSync } from "@/hooks/useOfflineSync";

/**
 * Casca visual comum a todas as telas autenticadas: sidebar no
 * desktop, barra inferior no mobile, conteúdo com padding que reserva
 * espaço para a bottom nav (evitando que o último elemento da tela
 * fique encoberto por ela).
 *
 * `useOfflineSync` vive aqui (não em TodayPage) porque a fila offline
 * pode ter itens pendentes de uma sessão anterior — o usuário pode
 * abrir o app já em qualquer tela, não só em "Hoje", e ainda assim
 * precisa ver que há check-ins aguardando envio.
 */
export default function AppLayout() {
  const pending = useOfflineSync();

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1">
        <main className="mx-auto max-w-3xl px-4 pb-24 pt-6 md:pb-10">
          {pending > 0 && (
            <div className="mb-4 rounded-xl border border-warning/40 bg-warning/10 px-4 py-2.5 text-center text-xs font-medium text-warning">
              {pending === 1
                ? "1 check-in aguardando conexão para sincronizar."
                : `${pending} check-ins aguardando conexão para sincronizar.`}
            </div>
          )}
          <Outlet />
        </main>
      </div>
      <BottomNav />
    </div>
  );
}
