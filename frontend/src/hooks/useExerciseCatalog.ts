import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import * as exerciseCatalogService from "@/services/exerciseCatalogService";
import type { ExerciseCatalogItem } from "@/types";

/**
 * Carrega o catálogo UMA vez e o mantém em cache (o conteúdo só muda quando
 * o app é atualizado, por isso staleTime infinito). `byId` permite achar o
 * exercício a partir do `catalog_id` que vem junto de cada exercício do treino.
 */
export function useExerciseCatalog() {
  const query = useQuery({
    queryKey: ["exercise-catalog"],
    queryFn: exerciseCatalogService.list,
    staleTime: Infinity,
    gcTime: Infinity,
  });

  const byId = useMemo(() => {
    const map = new Map<string, ExerciseCatalogItem>();
    query.data?.forEach((item) => map.set(item.id, item));
    return map;
  }, [query.data]);

  return { catalog: query.data ?? [], byId, isLoading: query.isLoading };
}
