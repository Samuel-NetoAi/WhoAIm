"use client";

import { useEffect, useState } from "react";

// Persists fases 0–2 (pesquisa, roteiro, prompts) as markdown files inside
// the project's notes/ folder, so the whole production lives in one place.
const NOTE_TABS = [
  { key: "dossie", label: "Dossiê (Fase 0 — pesquisa)" },
  { key: "roteiro", label: "Roteiro (Fase 1 — cenas)" },
  { key: "prompts", label: "Prompts (Fase 2 — SeeDance/storyboards)" },
] as const;

type NoteKey = (typeof NOTE_TABS)[number]["key"];

export function NotesPanel({ projectId }: { projectId: string }) {
  const [active, setActive] = useState<NoteKey>("dossie");
  const [content, setContent] = useState("");
  const [loadedFor, setLoadedFor] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;
    const key = `${projectId}:${active}`;
    if (loadedFor === key) return;
    fetch(`/api/projects/${projectId}/notes/${active}`)
      .then((res) => res.json())
      .then((data) => {
        setContent(data.content ?? "");
        setLoadedFor(key);
        setMessage(null);
      })
      .catch(() => setMessage("Erro ao carregar nota"));
  }, [projectId, active, loadedFor]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`/api/projects/${projectId}/notes/${active}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      });
      setMessage(res.ok ? "Salvo." : "Erro ao salvar");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div
        className="row"
        role="tablist"
        style={{ gap: "0.3rem", marginBottom: "0.7rem" }}
      >
        {NOTE_TABS.map((tab) => (
          <button
            key={tab.key}
            role="tab"
            className="tab"
            aria-selected={active === tab.key}
            onClick={() => setActive(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Cole aqui o resultado da skill correspondente (pesquisa-seres / whoiam), ou peça por voz ao Jarvis para preencher automaticamente."
        style={{ width: "100%", minHeight: 240 }}
      />
      <div className="row" style={{ marginTop: "0.6rem" }}>
        <button className="primary" onClick={handleSave} disabled={saving}>
          {saving ? "Salvando..." : "Salvar nota"}
        </button>
        {message && <span className="status">{message}</span>}
      </div>
    </div>
  );
}
