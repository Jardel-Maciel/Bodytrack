import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { useAuth } from "./AuthContext";
import * as projectService from "@/services/projectService";
import type { NewProjectInput } from "@/services/projectService";
import type { Project } from "@/types";

interface ProjectContextValue {
  project: Project | null;
  projects: Project[];
  loading: boolean;
  createProject: (input: NewProjectInput) => Promise<Project>;
  refresh: () => Promise<void>;
}

const ProjectContext = createContext<ProjectContextValue | undefined>(undefined);

/**
 * MVP: um usuário tem um projeto "ativo" por vez — o primeiro da
 * lista. Trocar de projeto ativo ou ter vários em paralelo é uma
 * extensão natural (a API já suporta múltiplos projetos por usuário),
 * mas não é necessário para o fluxo principal do app ainda.
 */
export function ProjectProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    if (!isAuthenticated) {
      setProjects([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const data = await projectService.list();
      setProjects(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  const createProject = async (input: NewProjectInput) => {
    const created = await projectService.create(input);
    setProjects((prev) => [created, ...prev]);
    return created;
  };

  const project = projects[0] ?? null;

  return (
    <ProjectContext.Provider value={{ project, projects, loading, createProject, refresh }}>
      {children}
    </ProjectContext.Provider>
  );
}

export function useProject() {
  const ctx = useContext(ProjectContext);
  if (!ctx) throw new Error("useProject deve ser usado dentro de <ProjectProvider>");
  return ctx;
}
