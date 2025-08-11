# Quickstart

## SDK (author)

```python
from mcp_ingest import describe, autoinstall

# Generate manifest + index without running the server
paths = describe(
  name="watsonx-mcp",
  url="http://127.0.0.1:6288/sse",
  tools=["chat"],
  resources=[{"uri":"file://server.py","name":"source"}],
  description="Watsonx SSE server",
  version="0.1.0",
)
print(paths)
# Optional (local dev): register into MatrixHub
# autoinstall(matrixhub_url="http://127.0.0.1:7300")
```

## CLI (operator)

```bash
# Detect → describe (offline)
mcp-ingest pack ./examples/watsonx --out dist/

# Register later (idempotent)
mcp-ingest register \
  --matrixhub http://127.0.0.1:7300 \
  --manifest dist/manifest.json
```

## Harvest a whole repo (many servers)

```bash
mcp-ingest harvest-repo https://github.com/modelcontextprotocol/servers/archive/refs/heads/main.zip \
  --out dist/servers
```

**Result:** one `manifest.json` per subserver + a repo-level `index.json`.

## Harvest README-linked servers too

Use the new integrated command to extract GitHub candidates from a repo’s README, harvest each, and (optionally) register them:

```bash
mcp-ingest harvest-source \
  https://github.com/modelcontextprotocol/servers \
  --out dist/servers \
  --yes \
  --max-parallel 4 \
  --register \
  --matrixhub http://127.0.0.1:7300
```

This first reads the README, finds all GitHub repo (and `/tree/<ref>/<subdir>`) links, then processes each candidate. See the full tutorial in **Tutorials → Harvest README-linked servers**.


