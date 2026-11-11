# Manual relevance review

Procedure confirmed by the author on **11 November 2026**, and reported in Section III, "Screening and relevance assessment," of the current manuscript.

## Procedure

1. At the manual review stage, three reviewers read each study under consideration.
2. Each reviewer voted on whether the study was relevant to the survey scope.
3. A study was selected on relevance grounds if at least two of the three reviewers voted in favor.
4. A 2--1 disagreement was resolved by the majority vote; unanimity or a separate adjudicator was not required by the reported rule.

The scope in Section III covers research from 2020--2026 that substantively uses an LLM for security analysis, testing, repair or verification, explicitly targets an OS component or privileged interface, and provides methodological and evaluation evidence. Foundational work, transferable methods, and systems protecting LLM execution are considered as background or related work. The majority rule reports the manual relevance decision, not a study-quality score.

## Provenance and retained evidence

The author clarified the three-person voting procedure during the manuscript revision and confirmed that the individual study-level voting records were not retained. This document records that retrospective author statement; its date is the date of clarification, not an inferred date of the original votes.

The archive therefore has no per-study ballots, reviewer-specific decisions, linked vote counts or complete adjudicated study list from which to recompute the manual selection. Reviewer independence, blinding and an agreement statistic were not reported. The exact set of records considered at the manual stage cannot be reconstructed from the retained files. No claim is made that all 6,408 discovery-audit records, all 225 updated candidates, or every later addition received a separately documented three-person vote.

## Relationship to the automated files

`protocol.txt`, the model prompts, raw responses, `screening_results.csv`, the second- and third-pass files, and review queues describe the frozen automated discovery audit. The preliminary model was `deepseek/deepseek-flash`; the separate assessment of available abstracts used the same model. Model calls and the Codex sample audit are distinct from the three human reviewers.

Fields such as `independent review pending` record the status in that automated snapshot. They are preserved as historical model-assessment fields, not relabeled as human decisions. Because no individual voting log was retained, the author-confirmed procedure cannot retrospectively populate those fields with verified manual outcomes.

The 59 historical in-depth candidates and the 23 updated direct candidates are relevance-score subsets of different inventories. The majority-vote procedure does not convert either subset into a verified final count of unique eligible studies. See [the manuscript alignment](../MANUSCRIPT_ALIGNMENT.md) and [inventory documentation](../inventory/README.md).
