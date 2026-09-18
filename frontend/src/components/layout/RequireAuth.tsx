import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "@/contexts/AuthContext";

export default function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
