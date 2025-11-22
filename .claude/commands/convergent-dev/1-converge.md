# Convergence: From Ideas to Feature Scope

Transform ideas into focused, shippable scope through structured convergence.

**What this does:**
- Launches the `convergence-architect` agent
- Guides you through 4 phases: DIVERGE → CAPTURE → CONVERGE → DEFER
- Adapts based on your specific situation (MVP, next feature, or backlog organization)
- Creates `FEATURE_SCOPE.md` and updates `MASTER_BACKLOG.md`

**Three convergence scenarios:**

**Scenario 1: MVP Convergence** (Starting Fresh)
- "I'm starting a new project and need to define the MVP scope"
- Explore all possibilities, converge to minimal viable product
- Output: Clear MVP scope + comprehensive backlog of deferred features

**Scenario 2: Next Feature** (Ongoing Project)
- "I have an ongoing project and need to find what to build next"
- Reviews existing backlog, explores new ideas, identifies what adds most value
- Output: Next feature scope + updated backlog + "why this next"

**Scenario 3: Organize Backlog** (Idea Management)
- "I have many ideas that need to be structured into manageable features"
- Break down ideas into feature-scoped backlog items
- Output: Well-structured backlog (may not pick "next" yet)

**The agent will ask you to select your scenario first**, then adapt the process accordingly.

**Process (all scenarios):**
1. **DIVERGE**: Explore all possibilities freely
2. **CAPTURE**: Organize ideas into structures
3. **CONVERGE**: Identify scope or structure (depends on scenario)
4. **DEFER**: Preserve all non-scope ideas in backlog

**Typical duration:** 30-60 minutes depending on scenario and complexity

**Outputs:**
- `ai_working/[project-name]/convergence/YYYY-MM-DD-feature-name/FEATURE_SCOPE.md` (Scenarios 1 & 2)
- `ai_working/[project-name]/convergence/YYYY-MM-DD-feature-name/DEFERRED_FEATURES.md`
- `ai_working/[project-name]/convergence/MASTER_BACKLOG.md` (updated or created)

**After this:**
- **Scenarios 1 & 2**: Use `/convergent-dev:2-plan-sprints` to break scope into executable sprints
- **Scenario 3**: Review backlog, then decide if ready to converge to next feature

**Full methodology:** See `ai_context/convergent-dev/CONVERGENCE_PROCESS.md`

---

**Ready to start?**

I'll launch the convergence-architect agent who will first ask you to select your scenario, then guide you through the convergence process.
