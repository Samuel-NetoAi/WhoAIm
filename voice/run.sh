#!/usr/bin/env bash
# Lançador do ALPHA no Linux (a máquina secundária).
#
# Diferenças em relação ao run.bat: usa o venv local e exige que
# AI_PROJECT_ROOT aponte para a pasta dos projetos — no Windows o padrão
# C:\Ai-Project serve, aqui não existe.
#
# Sem microfone, a janela abre em MODO DIGITADO e o campo de comando funciona
# igual. Digite 'diagnostico' para ver o que esta máquina tem e o que falta.
set -euo pipefail
cd "$(dirname "$0")"

if [[ -z "${AI_PROJECT_ROOT:-}" ]]; then
  echo "AI_PROJECT_ROOT não está definida."
  echo "Ex.: export AI_PROJECT_ROOT=\"\$HOME/Ai-Project\""
  echo "(é a pasta que contém Criaturas/, Animes/ e Trilhas/)"
  exit 1
fi

PYTHON="./.venv/bin/python"
[[ -x "$PYTHON" ]] || PYTHON="python3"

exec "$PYTHON" main.py
