# QA Confidence — prompt template

Copy/adapt when asking the agent to map a case or decide skip vs manual.

```
/QA_ConfidenceWorkflow

Module: <Products | Beacons | Fee Management | …>
Manual case: <MC-… or paste steps>
Question: Can we skip this manually? / Seed a scenario mapping / Raise confidence after green run

Constraints:
- Follow qa-confidence/prompts/agent_guardrails.md
- Prefer cheapest CMS layer from trust_policy.yaml
- Update scenarios/ and cases/ YAML; regenerate report
- Do not claim trusted while caveats remain
```

After a green StepReporter run:

```
/QA_ConfidenceWorkflow

Attach run: reports/KS-CMS-<MODULE>-001….html
Update confidence for module <…> — keep slightly pessimistic; clear caveats only when evidence supports it.
```
