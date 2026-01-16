# Kubecost–CloudTuner Documentation Index

Use this guide to navigate the working notes that support the Kubecost ⇄ CloudTuner integration. Everything now lives under `docs/kubecost/` with subfolders for each rollout phase plus shared references.

## Folder Layout

| Folder | Purpose |
| --- | --- |
| `phase-1/` | Metroculus bootstrap, API validation, and executive summaries for the first rollout. |
| `phase-2/` | All ClickHouse/REST fixes, Phase 2 execution plans, and verification evidence. |
| `phase-3/` | Namespace/pod/node allocation design notes and deployment guides. |
| `phase-4/` | Upcoming UI workstreams and frontend handover material. |
| `architecture/` | Cross-phase diagrams such as K8s schema plus data-extraction reference designs. |
| `analysis/` | Deeper Kubecost metrics investigations and scratch notes. |
| `operations/` | CI/CD, image matrix, installation, and other day‑2 runbooks. |
| `project-health/` | Status dashboards and closure reports that track the overall effort. |
| `handover/` & `strategy/` | Frontend handoffs and ancillary cost-optimization ideas. |

## Quick Links

| Document | Path | Focus | Highlights / When to Use |
| --- | --- | --- | --- |
| **Phase 1 Implementation Summary** | `phase-1/implementation-summary.md` | Original Metroculus integration plan | Architecture diagrams, API flow, and validation steps for the Phase 1 Thanos → Metroculus path. |
| **Phase 1 API Testing Guide** | `phase-1/api-testing-guide.md` | Hands-on validation checklist | Shell commands for verifying Thanos metrics, Metroculus endpoints, and initial REST alignment. |
| **Phase 1 Achievements Summary** | `phase-1/achievements-summary.md` | Quick executive recap | Bullet snapshot of what was delivered during Phase 1 and remaining gaps. |
| **Kubecost Integration Status** | `project-health/integration-status.md` | Project tracking dashboard | Current/next steps, blockers, and deployment namespace details. |
| **Kubecost Integration Complete** | `project-health/integration-complete.md` | Closure report for earlier milestone | Wrap-up of the first iteration before Phase 2 enhancements. |
| **Phase 2 Implementation Summary** | `phase-2/implementation-summary.md` | Deprecated ClickHouse/worker approach | Keeps the original (now discarded) Phase 2 design for reference. |
| **Phase 2 Pricing Fix** | `phase-2/pricing-fix.md` | Current pricing corrections | Details the metric aggregation changes in Metroculus and REST plus gaps targeted for Phase 3. |
| **Pricing Fix Verification** | `phase-2/pricing-fix-verification.md` | Test evidence for the pricing fix | Curl scripts and expected outputs to prove the Phase 2 adjustments. |
| **Simple Spot Solution** | `strategy/simple-spot-solution.md` | Ancillary cost-optimization notes | Supplemental strategy doc; not directly tied to the Kubecost integration flow. |
| **CI/CD Build Strategy** | `operations/cicd-build-strategy.md` | Pipeline/deployment reminders | Use when aligning Helm releases with REST/Metroculus image updates. |
| **Image Versions** | `operations/image-versions.md` | Runtime image matrix | Handy reference when promoting new images during testing. |
| **K8s Schema Design** | `architecture/k8s-schema-design.md` | Data-model diagrams | Use for ClickHouse table context and REST field mapping. |
| **Phase 3 Allocation Deployment** | `phase-3/allocation-deployment-guide.md` | Namespace/pod/node rollout | Step-by-step instructions for enabling granular allocation exports. |
| **Phase 4 UI Planning** | `phase-4/ui-planning.md` | Frontend roadmap | Prep notes for the UI integration workstream. |

## Additional Context Repositories
- **`../../.claude/claude.md`** – Rolling conversation log and architectural context that fed the Phase 2 fixes.<br>
- **`../../.claude/implementation.md`** – Original phased rollout blueprint (kept for historical background).

## Suggested Reading Order
1. Start with **Phase 1 Implementation Summary** → **Phase 1 API Testing Guide** to understand the baseline.
2. Review **Kubecost Integration Status** for a big-picture snapshot.
3. Dive into **Phase 2 Pricing Fix** alongside **Pricing Fix Verification** for the current testing scope.
4. Refer back to **Phase 2 Implementation Summary** only when you need the discarded ClickHouse worker context.

Keep this index updated whenever new context markdowns are added or deprecated so teammates can locate the latest guidance quickly.
