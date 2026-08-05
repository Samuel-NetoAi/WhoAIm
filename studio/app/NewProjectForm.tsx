"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

export const NewProjectForm = () => {
  const router = useRouter();
  const [creatureName, setCreatureName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ creatureName }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Falha ao criar projeto");
      router.push(`/projects/${data.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro desconhecido");
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="row">
      <input
        value={creatureName}
        onChange={(event) => setCreatureName(event.target.value)}
        placeholder="Nome da criatura (ex: Cthullhu)"
        required
        style={{ flex: 1, minWidth: 220 }}
      />
      <button type="submit" className="primary" disabled={busy}>
        {busy ? "Criando..." : "Criar projeto"}
      </button>
      {error && <span className="status error">{error}</span>}
    </form>
  );
};
