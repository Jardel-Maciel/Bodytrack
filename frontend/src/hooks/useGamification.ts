import { useQuery } from "@tanstack/react-query";

import { useAuth } from "@/contexts/AuthContext";
import * as gamificationService from "@/services/gamificationService";

export const GAMIFICATION_KEY = ["gamification"];

/**
 * Pontos e metas do dia. Atualiza a cada 60s e ao voltar para a aba — isso também
 * cobre check-ins feitos offline que sincronizam depois. Quem salva um check-in
 * ou treino invalida esta chave para a pontuação aparecer na hora.
 */
export function useGamification() {
  const { user } = useAuth();
  return useQuery({
    queryKey: GAMIFICATION_KEY,
    queryFn: gamificationService.getSummary,
    enabled: Boolean(user),
    refetchInterval: 60_000,
  });
}
