#!/usr/bin/env bash
# Installa gli strumenti del laboratorio in una sessione cloud nuova.
# Uso: bash re-lab/setup.sh
set -uo pipefail

LAB_DIR="$(cd "$(dirname "$0")" && pwd)"
TOOLS_DIR="${TOOLS_DIR:-$HOME/tools}"
REPO="davidepaag/davidepaag"
GHIDRA_TAG="${GHIDRA_TAG:-ghidra}"
WHISPER_MODEL="${WHISPER_MODEL:-base}"
mkdir -p "$TOOLS_DIR"

ok()   { printf '  \033[32m✔\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m✘\033[0m %s\n' "$1"; }

echo "== REA (npm)"
if (cd "$LAB_DIR" && npm install --no-fund --no-audit --silent); then
  ok "rea $(cd "$LAB_DIR" && npx rea --version 2>/dev/null | head -1)"
else
  warn "npm install non riuscito"
fi

echo "== whisper.cpp (sottotitoli automatici)"
WHISPER_DIR="$TOOLS_DIR/whisper.cpp"
if [ ! -x "$WHISPER_DIR/build/bin/whisper-cli" ]; then
  [ -d "$WHISPER_DIR" ] || GIT_LFS_SKIP_SMUDGE=1 git clone -q --depth 1 https://github.com/ggml-org/whisper.cpp "$WHISPER_DIR"
  cmake -S "$WHISPER_DIR" -B "$WHISPER_DIR/build" -DCMAKE_BUILD_TYPE=Release -DWHISPER_BUILD_TESTS=OFF >/dev/null \
    && cmake --build "$WHISPER_DIR/build" -j"$(nproc)" --target whisper-cli >/dev/null
fi
[ -x "$WHISPER_DIR/build/bin/whisper-cli" ] && ok "whisper-cli compilato" || warn "compilazione whisper.cpp non riuscita"

MODEL="$WHISPER_DIR/models/ggml-$WHISPER_MODEL.bin"
if [ ! -s "$MODEL" ]; then
  curl -fsSL -o "$MODEL.part" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-$WHISPER_MODEL.bin" \
    && mv "$MODEL.part" "$MODEL" || rm -f "$MODEL.part"
fi
[ -s "$MODEL" ] && ok "modello whisper $WHISPER_MODEL" \
  || warn "modello whisper non scaricato (serve accesso a us.aws.cdn.hf.co)"

echo "== FFmpeg"
command -v ffmpeg >/dev/null && ok "$(ffmpeg -version | head -1 | cut -d' ' -f1-3)" || warn "ffmpeg mancante"

echo "== Ghidra (motore nativo per REA)"
GHIDRA_HOME="$(ls -d "$TOOLS_DIR"/ghidra_*_PUBLIC 2>/dev/null | tail -1)"
if [ -z "$GHIDRA_HOME" ]; then
  # Lo zip ufficiale va caricato come allegato della release "$GHIDRA_TAG" del repository.
  ZIP_NAME="$(curl -fsSL "https://github.com/$REPO/releases/expanded_assets/$GHIDRA_TAG" 2>/dev/null \
    | grep -oE 'ghidra_[0-9.]+_PUBLIC_[0-9]+\.zip' | head -1)"
  if [ -n "$ZIP_NAME" ]; then
    curl -fsSL -o "$TOOLS_DIR/$ZIP_NAME" "https://github.com/$REPO/releases/download/$GHIDRA_TAG/$ZIP_NAME"
    echo "     sha256: $(sha256sum "$TOOLS_DIR/$ZIP_NAME" | cut -d' ' -f1)"
    echo "     confrontalo con quello pubblicato su github.com/NationalSecurityAgency/ghidra/releases"
    (cd "$TOOLS_DIR" && unzip -q "$ZIP_NAME" && rm -f "$ZIP_NAME")
    GHIDRA_HOME="$(ls -d "$TOOLS_DIR"/ghidra_*_PUBLIC 2>/dev/null | tail -1)"
  fi
fi
if [ -n "$GHIDRA_HOME" ]; then
  ok "Ghidra in $GHIDRA_HOME"
  echo "     prima di usare REA: export GHIDRA_INSTALL_DIR=\"$GHIDRA_HOME\""
else
  warn "Ghidra non trovato: carica lo zip ufficiale nella release '$GHIDRA_TAG' di $REPO"
fi
