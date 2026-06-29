# Workflow & Agent Routing Policies

## Multi-LLM Routing Matrix
This project enforces an asymmetric engineering team topology utilizing Antigravity 2.0 orchestration rules:

1. **The Conductor (Claude Opus 4.6):** * Retains absolute ownership over `spec.md`, track definitions, and design patterns.
   * Handles high-level structural changes.
   * Conducts ultimate verification loops.

2. **The Builder (Gemini 3.5 Flash):**
   * Default worker for token-heavy coding files, boilerplate generation, and rapid S-expression parsing functions.
   * Operates via parallel subagents to generate Python matrix loops.

3. **The Validator (Gemini 3.1 Pro):**
   * Acts as an isolated code gatekeeper.
   * Validates git diffs and implementation scripts directly against `spec.md` requirements before committing changes.

## Development Execution Gate
* Never proceed to automated implementation if Gemini 3.5 Flash encounters architectural ambiguity; code errors must trigger a fallback back to Claude Opus 4.6.
