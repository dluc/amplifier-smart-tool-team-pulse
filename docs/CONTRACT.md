# Unison Leadership Experience Contract — v1 (DRAFT)

**Who builds against this:** people using Unison to understand and lead work; library/CLI callers and standalone/MCP App integrators; maintainers supporting the same product behavior. Silent changes to evidence, authority, result identity or recovery affect them.

## Purpose

Unison connects the leadership view in [VISION.md](VISION.md) to promises that can be checked. This draft covers shared product behavior, not a release checklist or a claim of delivery. A later build agreement names the clauses it delivers; omitted destination capabilities remain explicit gaps, not silently fulfilled promises.

The current code is a working end-to-end teammate-oriented example, not this contract's scope. Internal teammates on the existing Team Pulse server remain the selected initial sharing audience; that choice does not settle the next build. This document revision authorizes no implementation, packaging, generation, cleanup or publication.

## What it looks like

An area lead sees a shared-capability dependency, inspects its evidence and routes a question to the appropriate owner. A whole-team reader sees the cross-area consequence of the same work. Both return to the recorded response and its evidence—not a manufactured success or a fresh generation disguised as the previous result.

## Core — proposed product promises

1. **Portfolio considers the team landscape before personal attention.** AI identifies work from authorized Team Pulse evidence without requiring manual assembly or initial draft approval. Work connects to intended outcomes, capabilities, beneficiaries, stated team direction and dependencies; coverage and unclear alignment remain visible.

2. **For you explains why attention matters.** For you and Portfolio present the same retained result and revision; each attention item leads to its corresponding Portfolio work. Awareness differs from useful participation. No qualifying attention found within the evidenced scope is different from insufficient context to judge. An unchanged suggestion does not repeatedly demand a response.

3. **Claims retain their evidence and limits.** Sources, observation times, coverage, corrections and contrary evidence are inspectable. Plans, reported progress, verified delivery, use and benefit remain distinct. Outcome confidence names its basis and comparison; freshness, activity or spend alone cannot establish value or causality. Historical results stay identified as historical; unavailable original evidence stays unavailable. Changed source text is not substituted for the original support.

4. **Perspective changes context, not access or authority.** Effort, area and whole-team views use the same work and preserve relevant cross-area relationships. Current focus is clear and correctable. Protected reads require verified identity and applicable access checks; access denial clears protected UI content. Responsibility, ownership or permission is not inferred from a person's title or relevance.

5. **Judgment and follow-through stay connected to the work.** Options, consequences, accountable owner, intended recipient and effects are explicit. Unknown ownership or authority is stated rather than invented. A recommendation is not a decision. Questions, decisions, delegation, deferral and deliberate non-action retain their disposition, response and returned evidence. An unresolved outcome stays unresolved; routine work does not require the reader's approval.

6. **Reading, generating and acting are different operations.** Opening, navigation, retained reads and request inspection do not call AI, change saved content or submit shared answers. Explicit generation uses an identified, separately authorized route with declared source scope, tool access, limits and effects; it does not borrow the host's model or silently switch routes. Shared writes require non-model approval of the exact target and payload. Model output is data, never execution authority.

7. **Saved results and operations keep stable identities.** Only complete, validated output becomes a successful new result; prior revisions survive failed, malformed or interrupted updates. Identical request identity and arguments return the original receipt; changed arguments are refused. Recovery inspects the original durable request before retry or replacement, preserving unresolved status and usage. A new request ID does not bypass that check. Restart, migration, directory changes or renamed grants do not reset authority or silently repeat work.

8. **Entry points keep the same meaning.** Library behavior underlies thin CLI and application adapters. Each advertised operation declares inputs, results, prerequisites, effects, failures and recovery; discovery matches installed behavior. Standalone web and compatible MCP App presentations preserve exact result identities and effect semantics, not necessarily identical layouts. Quiet Junction, keyboard use, themes, narrow screens and reduced motion do not hide evidence or blocked states.

9. **Configuration and retained work remain understandable and private.** People can identify effective connection, verified identity, AI route, limits, data/configuration locations and when changes apply. Data, configuration, credentials and operation history are distinct; diagnostics do not reveal secrets. Supported backup, restore and upgrade preserve results, receipts, usage and unknowns. Removing code does not silently remove retained work.

10. **Supported releases make bounded, verified claims.** A release identifies its source, version, packaged assets, notices, supported environments and actual opening. It installs outside the developer checkout without private databases, grants or host settings. A transport receipt, schema test or mounted UI is not proof of the promised user journey; unsupported conditions fail clearly rather than bypass safeguards.

## What v1 deliberately does NOT freeze

- **AI engine and orchestration:** direct library retrieval, Lens, `ask-local`, Copilot or an Amplifier agent are implementation choices. Decide when an agreed leadership probe establishes the needed tools, evidence, limits and failure behavior. The current `ask-local` loop is not assumed to satisfy clause 6.
- **Storage/configuration layout:** data-only directories, shared profiles or explicit instances remain open. Decide when isolation and migration checks demonstrate identity and operation-history continuity under clauses 7 and 9.
- **Presentation and object schema:** names For you / Portfolio remain; exact layouts, generated composition, prompt wording and internal fields are open. Decide when a reviewed task shows a change is necessary without weakening evidence, authority or accessibility.
- **Broader reach:** arbitrary servers, other hosts/platforms, scheduled refresh, offline protected reads, synchronization and billing/telemetry collection are not implied. Consider each only after a concrete need, access boundary and qualification check are agreed.

## Conformance checks — what would distinguish right from wrong

Each check names its Core clause. These are proposed checks, not passing results. Missing capability is **Not yet**; contradictory behavior is **Broken**; unavailable verification is **Can't check**. Required-but-missing behavior does not become acceptable merely because it is disclosed.

1. Include work unrelated to the viewer; reject a personal-only landscape or invented team alignment. Test AI discovery without manual Portfolio assembly.
2. Compare the retained result/revision across For you and Portfolio and each attention item's link target. Distinguish a qualified quiet result from inadequate evidence; retain dispositions on an unchanged suggestion.
3. Compare representative claims with exact consumed material, counterevidence and dates. Reject unsupported confidence or causal claims and substitution of changed source bytes; state when original evidence is unavailable.
4. Widen/narrow focus without losing cross-area context. Test wrong-caller, denied/missing sources and late access denial; no privileged controls or protected residual UI appear without authority.
5. Trace an authorized response through owner, disposition and returned evidence. Keep a deferred or unknown outcome visible; do not label an acknowledgment as completed work.
6. Observe zero AI/shared-write calls during retained reading. In the installed artifact, an attempted model-driven shared write without exact non-model approval is rejected or unreachable; metadata-only hiding is insufficient.
7. Exercise adjacent successful updates, a failed/uncertain cycle, duplicate/concurrent requests and browser/process restart. An attempted new-ID retry without recovery inspection is refused, including after a directory change. Verify original receipts remain findable, old revisions survive and provider calls/usage are not duplicated or reset.
8. Compare exact result references and declared effects across advertised library, CLI, standalone and MCP App paths. Perform real keyboard, narrow-screen, theme and evidence-inspection tasks; fixtures alone do not prove host delivery.
9. Inspect effective configuration without secrets. Test alternate directories, backup/restore, upgrade and removal; protected reads still require access, and operation/usage history is preserved.
10. Install the exact artifact outside the checkout, inspect packaged content/notices, then verify each advertised host's actual opening and retained-result journey. Record supported and unqualified environments separately.

Technical test fixtures belong beside these checks. No existing implementation is declared to pass the complete leadership contract; current fulfillment is recorded separately from the promises.

## Reserved / open questions — not implementation instructions

- Which leadership task and clauses form the next bounded build, and what proves it useful?
- Which Team Pulse sources actually support outcomes, ownership, value and responses; what must remain unknown?
- Does that task need adaptive tool use, or controlled retrieval and synthesis? Which effects remain read-only?
- What coherent contract boundaries emerge when experience, integration and operations need separate audiences or verification targets?

<details>
<summary>Draft record and preserved discovery — not additional promises</summary>

This is a proposed umbrella for shared behavior, not a final claim that all ten clauses belong in one delivery increment. Converge's [contract template](https://raw.githubusercontent.com/microsoft/amplifier-bundle-converge/41679679fd449ecc16b6af58d0ce8ec2cb2d29ad/docs/workspace-template/CONTRACT.md.template) and [boundary guidance](https://raw.githubusercontent.com/microsoft/amplifier-bundle-converge/41679679fd449ecc16b6af58d0ce8ec2cb2d29ad/docs/RIGHT-SIZING.md) inform the shape; no Converge manager workflow or locking is adopted by this edit.

The [full earlier discovery draft](amplifier-canvas://artifact/1441f33c5e7d4f38b24b06e8d5c487e7?session=77c24a6b-90ca-4a92-8c22-2a24f1cf72cc&version=4) retains source quotes, configuration/storage inventory, observed gaps and private-recovery cautions. It is historical evidence, not the next-build plan. The known uncertain request is not resolved or replayed by revising this document.

Exact original file snapshots are also saved in this conversation: vision `1b1de85e6759426a8970f2baa29c94cd` and contract `cb87333615414bcdbb3776aa14b98e3a`. Alex/MJ source interpretations and limits remain in those records; numerical claims and primary-report assertions are not independently verified here.

Drafts remain revisable. Locking, approval to implement and publication are separate decisions; review does not imply any of them. This edit does not adopt Converge governance. If adopted later, its ratified locking bar applies: a written specification, discriminating machine checks, a real implementation passing them, an end-to-end example and the steward's explicit locking decision. A locked document changes only through an approved, evidence-backed exact proposal with what does not change.

</details>

## Draft changelog

- **2026-10-02:** Reframed from historical teammate-preview acceptance and mixed discovery notes into shared leadership promises, clause-linked checks and explicit open choices. Original evidence preserved. Document edits only; no implementation, packaging, ratification or locking.
