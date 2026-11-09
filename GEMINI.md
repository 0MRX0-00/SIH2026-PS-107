# Project Rules & Guidelines — e-BIS Sahayak

## Graphify-First Codebase Exploration (Token Optimization)
- **Do not scan or read every file and folder recursively**.
- Whenever navigating code, answering questions about architecture, or finding definitions/callers, **use the Graphify knowledge graph first** (`graphify-out/graph.json`):
  - `python -m graphify explain "<Symbol>"`
  - `python -m graphify query "<Question>"`
  - `python -m graphify path "<From>" "<To>"`
- Only read the specific file and line ranges identified by Graphify.
- Run `python -m graphify update .` after code additions or refactors to keep the graph fresh.

