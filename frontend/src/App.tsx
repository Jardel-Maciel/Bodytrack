import { Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "@/components/layout/AppLayout";
import RequireAuth from "@/components/layout/RequireAuth";
import LoginPage from "@/pages/LoginPage";
import HomePage from "@/pages/HomePage";
import TodayPage from "@/pages/TodayPage";
import WorkoutPage from "@/pages/WorkoutPage";
import EvolutionPage from "@/pages/EvolutionPage";
import ProfilePage from "@/pages/ProfilePage";

/**
 * Estrutura de navegação principal, conforme especificado:
 * INÍCIO / HOJE / TREINO / EVOLUÇÃO / PERFIL
 * (barra inferior no celular, sidebar no desktop — ambas renderizadas
 * dentro de AppLayout, que decide o layout conforme o breakpoint).
 */
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route path="/" element={<HomePage />} />
        <Route path="/hoje" element={<TodayPage />} />
        <Route path="/treino" element={<WorkoutPage />} />
        <Route path="/evolucao" element={<EvolutionPage />} />
        <Route path="/perfil" element={<ProfilePage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
