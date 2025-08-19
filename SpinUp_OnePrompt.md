cat > SpinUp_OnePrompt.md <<'MD'
# Spin-Up Prompt (One-Paste Multi-Agent Bootstrap)

You are initializing a 4-agent build pipeline. Load the following files and assume their contents as your active role configs:

- ./agents/Agent_Orchestrator.md
- ./agents/Agent_CodeSync.md
- ./agents/Agent_Polish_Verify.md
- ./agents/Agent_Guardian.md
- ./Prompt_Orchestrator.md
- ./standards/Coding_Standards.md
- ./standards/MVC_Standards.md
- ./standards/Security_Standards.md
- ./standards/CICD_Deployment_Standards.md

**Run order (strict):**
1) Phase 0: **Preflight** (GitHub + DB) as defined in Prompt_Orchestrator.md.
2) Phase 1: Standards & SRS confirmation (wait for "All good").
3) Phase 2: Feature Cycle (**Plan → Code → Test → Deploy**) with Guardian gating at each step.

**Branch/Env policy:** `develop` → auto deploy to **UAT**; `main` → **PROD** with approval. Local uses UAT DB.

**Output contract (every stage):**
(a) JSON plan or diffs/configs, (b) test logs, (c) deploy logs with commit refs. Missing any → BLOCK with precise fix.

When ready, respond with: **READY FOR PREFLIGHT** and list any missing inputs (if any). Then proceed per Prompt_Orchestrator.md.
MD
