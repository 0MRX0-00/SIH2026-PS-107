# Graph-First Architecture Exploration & Token Conservation Rule

## Invariant: Graph-First Investigation (Token Saver)
When exploring, answering questions, or planning changes to a codebase:

1. **Do NOT scan or read all folders and files blindly**:
   - Never run unbounded recursive scans or read dozens of files into context to understand structure or trace callers/dependencies.
   - Exhaustive file dumping wastes token context.

2. **Always check for and use the Graphify Knowledge Graph**:
   - Check if `graphify-out/graph.json` exists in the repository.
   - If `graphify-out/graph.json` exists, treat codebase questions as a **Graphify query first**:
     - Explain symbols and inspect connections: `python -m graphify explain "<symbol>"`
     - Query architecture or flows: `python -m graphify query "<question>"`
     - Trace shortest paths between components: `python -m graphify path "<nodeA>" "<nodeB>"`
   - If `graphify-out/graph.json` does not exist yet and the codebase has multiple files, initialize it via `python -m graphify update .` instead of manually reading all folders.

3. **Targeted Reading Only**:
   - Once Graphify pinpoints the exact file and line numbers for the relevant symbols, only open and read those specific targeted files.

4. **Keep the Graph Fresh**:
   - When code is refactored or new files are added, run `python -m graphify update .` to keep AST nodes, edges, and community hubs updated in milliseconds without LLM cost.

