"""Ponte por voz para o Alpha Studio (Next.js/Remotion na porta 3001).

Cada função retorna uma STRING em português — é o que o modelo de voz lê
em voz alta para o Samuel. Erros também voltam como frases, nunca exceções.
"""

from __future__ import annotations

import json
import subprocess
import time
import webbrowser
from pathlib import Path

import requests

STUDIO_URL = "http://localhost:3001"
STUDIO_DIR = r"C:\Ai-Project\Alpha\studio"

# Últimos jobs disparados por voz, por tipo, para "como está o render?"
_last_jobs: dict[str, dict] = {}


def _studio_alive() -> bool:
    try:
        requests.get(f"{STUDIO_URL}/api/projects", timeout=3)
        return True
    except requests.RequestException:
        return False


def _start_studio() -> bool:
    subprocess.Popen(
        ["npm", "--prefix", STUDIO_DIR, "run", "dev", "--", "-p", "3001"],
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    for _ in range(30):
        time.sleep(2)
        if _studio_alive():
            return True
    return False


def _ensure_studio() -> str | None:
    """Retorna None se o Studio está de pé; senão uma frase de erro."""
    if _studio_alive():
        return None
    if _start_studio():
        return None
    return (
        "Não consegui iniciar o Alpha Studio. "
        "Verifique a pasta C:\\Ai-Project\\Alpha\\studio."
    )


def _get_projects() -> list[dict]:
    r = requests.get(f"{STUDIO_URL}/api/projects", timeout=10)
    r.raise_for_status()
    return r.json().get("projects", [])


def _find_project(name: str) -> dict | None:
    """Match por nome falado ('medusa', 'baba yaga'), tolerante a acentos."""
    needle = name.strip().lower().replace(" ", "")
    for p in _get_projects():
        haystack = (p["creatureName"] + p["projectDirName"]).lower().replace(" ", "").replace("/", "")
        if needle and needle in haystack:
            return p
    return None


def studio_control(args: dict) -> str:
    action = (args.get("action") or "").strip()
    project_name = args.get("project") or ""

    err = _ensure_studio()
    if err:
        return err

    try:
        if action == "list_projects":
            projects = _get_projects()
            if not projects:
                return "Nenhum projeto encontrado nas pastas Criaturas ou Animes."
            parts = []
            for p in projects:
                status = "com plano de edição" if p["hasEditPlan"] else "sem plano ainda"
                parts.append(
                    f"{p['creatureName']}: {p['clipCount']} clipes, {status}"
                )
            return f"{len(projects)} projeto(s): " + "; ".join(parts)

        # Todas as ações abaixo precisam de um projeto.
        project = _find_project(project_name)
        if not project:
            return (
                f"Não achei um projeto chamado {project_name}. "
                "Peça a lista de projetos para ver os nomes."
            )
        pid = project["id"]
        label = project["creatureName"]

        if action == "analyze":
            r = requests.post(
                f"{STUDIO_URL}/api/projects/{pid}/analyze", timeout=300
            )
            data = r.json()
            if not r.ok:
                return f"A análise de {label} falhou: {data.get('error', 'erro desconhecido')}"
            n = len(data["editPlan"]["clips"])
            dur = round(data["editPlan"]["narration"]["durationInSeconds"])
            smart = data.get("alignment") == "smart"
            modo = (
                "cortes encaixados nas pausas da narração"
                if smart
                else "divisão igual de tempo"
            )
            return f"Análise de {label} pronta: {n} cenas em {dur} segundos de narração, {modo}."

        if action in ("render_full", "render_short"):
            target = "short" if action == "render_short" else "full"
            body: dict = {"target": target}
            if target == "short" and args.get("target_seconds"):
                body["targetSeconds"] = float(args["target_seconds"])
            r = requests.post(
                f"{STUDIO_URL}/api/projects/{pid}/render",
                json=body,
                timeout=30,
            )
            data = r.json()
            if not r.ok:
                return f"Falha ao iniciar o render: {data.get('error', 'erro desconhecido')}"
            _last_jobs[target] = {"jobId": data["jobId"], "pid": pid, "label": label}
            tipo = "Short" if target == "short" else "vídeo completo"
            return (
                f"Render do {tipo} de {label} iniciado. "
                "Pergunte o status quando quiser."
            )

        if action == "status":
            if not _last_jobs:
                return "Nenhum render foi iniciado por voz nesta sessão."
            frases = []
            for target, job in list(_last_jobs.items()):
                r = requests.get(
                    f"{STUDIO_URL}/api/projects/{job['pid']}/render/{job['jobId']}",
                    timeout=10,
                )
                if not r.ok:
                    frases.append(f"{target}: status indisponível")
                    continue
                j = r.json()["job"]
                tipo = {"full": "vídeo completo", "short": "Short", "post": "pós-processamento"}.get(
                    j["target"], j["target"]
                )
                if j["status"] == "rendering":
                    frases.append(f"{tipo} de {job['label']}: {round(j['progress'] * 100)} por cento")
                elif j["status"] == "done":
                    nome = Path(j.get("outputPath", "")).name
                    frases.append(f"{tipo} de {job['label']}: pronto, arquivo {nome}")
                    _last_jobs.pop(target, None)
                else:
                    frases.append(f"{tipo} de {job['label']}: erro — {j.get('error', '?')[:80]}")
                    _last_jobs.pop(target, None)
            return ". ".join(frases) + "."

        if action == "open":
            webbrowser.open(f"{STUDIO_URL}/projects/{pid}")
            return f"Abri o projeto {label} no navegador."

        return f"Ação desconhecida: {action}."

    except requests.RequestException as e:
        return f"Erro de comunicação com o Studio: {str(e)[:100]}"
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        return f"Resposta inesperada do Studio: {str(e)[:100]}"
