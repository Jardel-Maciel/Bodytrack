import { api } from "./api";
import type { ExerciseCatalogItem } from "@/types";

export async function list() {
  const { data } = await api.get<ExerciseCatalogItem[]>("/exercise-catalog");
  return data;
}

/** URL de uma imagem de demonstração (arquivos estáticos em /public/exercises). */
export function imageUrl(catalogId: string, index: number) {
  return `/exercises/${catalogId}/${index}.webp`;
}
