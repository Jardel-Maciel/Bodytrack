import { useState } from "react";

import { useAuth } from "@/contexts/AuthContext";

export default function ProfileEditForm() {
  const { user, updateProfile } = useAuth();
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(user?.name ?? "");
  const [height, setHeight] = useState(user?.height_cm != null ? String(user.height_cm) : "");
  const [birthDate, setBirthDate] = useState(user?.birth_date ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startEditing = () => {
    setName(user?.name ?? "");
    setHeight(user?.height_cm != null ? String(user.height_cm) : "");
    setBirthDate(user?.birth_date ?? "");
    setError(null);
    setEditing(true);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      await updateProfile({
        name: name.trim() || undefined,
        height_cm: height ? Number(height) : null,
        birth_date: birthDate || null,
      });
      setEditing(false);
    } catch {
      setError("Não foi possível salvar. Confira os dados e tente de novo.");
    } finally {
      setSaving(false);
    }
  };

  if (!editing) {
    return (
      <div className="card space-y-1">
        <div className="flex items-start justify-between">
          <div>
            <p className="font-medium">{user?.name}</p>
            <p className="text-sm text-foreground-muted">{user?.email}</p>
          </div>
          <button
            type="button"
            onClick={startEditing}
            className="rounded-lg border border-border px-3 py-1 text-xs text-foreground-muted hover:border-accent"
          >
            Editar
          </button>
        </div>
        <div className="flex gap-4 pt-1 text-xs text-foreground-muted">
          <span>Altura: {user?.height_cm != null ? `${user.height_cm} cm` : "não informada"}</span>
          <span>Nascimento: {user?.birth_date ?? "não informado"}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="card space-y-3">
      <p className="stat-label">Editar perfil</p>
      <label className="block text-xs text-foreground-muted">
        Nome
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-1 w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm text-foreground outline-none focus:border-accent"
        />
      </label>
      <label className="block text-xs text-foreground-muted">
        Altura (cm)
        <input
          type="number"
          step="0.1"
          min={0}
          value={height}
          onChange={(e) => setHeight(e.target.value)}
          placeholder="ex.: 178"
          className="mt-1 w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm text-foreground outline-none focus:border-accent"
        />
      </label>
      <label className="block text-xs text-foreground-muted">
        Data de nascimento
        <input
          type="date"
          value={birthDate}
          onChange={(e) => setBirthDate(e.target.value)}
          className="mt-1 w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm text-foreground outline-none focus:border-accent"
        />
      </label>
      {error && <p className="text-xs text-danger">{error}</p>}
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setEditing(false)}
          disabled={saving}
          className="flex-1 rounded-xl border border-border py-2 text-sm text-foreground-muted hover:border-accent disabled:opacity-60"
        >
          Cancelar
        </button>
        <button
          type="button"
          onClick={handleSave}
          disabled={saving || !name.trim()}
          className="flex-1 rounded-xl bg-accent py-2 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60"
        >
          {saving ? "Salvando…" : "Salvar"}
        </button>
      </div>
    </div>
  );
}
