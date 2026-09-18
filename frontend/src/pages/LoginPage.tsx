import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const { loginWithPassword, registerAndLogin } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (mode === "login") {
        await loginWithPassword(email, password);
      } else {
        await registerAndLogin({ email, password, name });
      }
      navigate("/", { replace: true });
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(
        detail ??
          (mode === "login" ? "E-mail ou senha incorretos." : "Não foi possível criar a conta.")
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="card w-full max-w-sm">
        <h1 className="mb-1 text-xl font-semibold">BodyTrack</h1>
        <p className="mb-6 text-sm text-foreground-muted">
          {mode === "login"
            ? "Entre para continuar seu diário de transformação."
            : "Crie sua conta para começar a registrar sua evolução."}
        </p>

        <form className="space-y-3" onSubmit={handleSubmit}>
          {mode === "register" && (
            <input
              type="text"
              placeholder="Nome"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
            />
          )}
          <input
            type="email"
            placeholder="E-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
          />
          <input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
          />

          {error && <p className="text-sm text-danger">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-xl bg-accent py-2.5 text-sm font-semibold text-white transition-colors hover:bg-accent-hover disabled:opacity-60"
          >
            {submitting ? "Aguarde…" : mode === "login" ? "Entrar" : "Criar conta"}
          </button>
        </form>

        <button
          type="button"
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError(null);
          }}
          className="mt-4 w-full text-center text-xs text-foreground-muted hover:text-foreground"
        >
          {mode === "login" ? "Não tem conta? Criar uma agora" : "Já tem conta? Entrar"}
        </button>
      </div>
    </div>
  );
}
