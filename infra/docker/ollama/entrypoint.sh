#!/bin/sh
set -e

ollama serve &
pid=$!

until curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; do
  sleep 2
done

ollama pull nomic-embed-text
ollama pull gemma3:4b

wait "$pid"
