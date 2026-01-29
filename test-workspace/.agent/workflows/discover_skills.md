# Workflow: Skill Discovery Protocol

**Goal**: Identify, Evaluate, and Install new capabilities from external sources.

## 1. Search
Run the explorer to find relevant repositories:
```bash
make discover q="topic"  # e.g., "python", "docker", "web"
```

## 2. Evaluate
Before installing, evaluate the source:
- Check the repository URL.
- Look for `.md` files in `skills/` or `tools/` directories.
- Read the raw code/prompt to ensure it matches our safety standards.

## 3. Adapt
Most external skills need adaptation to the Gemini Native Standard:
1.  **Context**: Does it assume specific file paths?
2.  **Format**: Convert to standard Markdown skill format.
3.  **Refine**: Remove specific mentions of other agents (e.g., "You are Claude").

## 4. Install
Use the manager to fetch the raw file, then edit:
```bash
make skill-add source="owner/repo/path/to/skill.md"
# Then edit the file in .agent/skills/
```