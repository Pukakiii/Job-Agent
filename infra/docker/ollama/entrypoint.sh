#!/bin/sh
set -e

ollama serve &
pid=$!

until curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; do
  sleep 2
done

# Pull the models named in OLLAMA_PULL_MODELS (space-separated). Defaults to the
# embedding + chat pair for fully-local use; slim to just an embed model (e.g.
# "nomic-embed-text") for "cloud chat + local embeddings" setups.
for model in ${OLLAMA_PULL_MODELS:-nomic-embed-text gemma3:4b}; do
  echo "Pulling $model ..."
  ollama pull "$model"
done

wait "$pid"
