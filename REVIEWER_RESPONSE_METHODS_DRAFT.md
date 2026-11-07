# Draft response to reviewers

**Historical draft notice:** This draft predates the 7 November 2026 revision in which the initial Google Scholar search date, 10 March 2026, was supplied. Statements below that the date could not be recovered reflect the information available when this draft was written; original execution logs remain unavailable. The current response letter and `search/HISTORICAL_SEARCH_DATE.md` reflect the later information.

**Author note — draft for review, not yet ready to submit.** Insert the final manuscript page/line numbers and a working public repository or archive URL after release. Check that every file cited below is included in that release and that its contents are accessible to reviewers. The metadata-only public export omits abstracts and raw model responses, so it does not by itself allow complete offline replay of model-based screening. Complete the citation verification and final proofreading noted below, and confirm the highlighted manuscript and clean copy before submission.

## Reviewer 1, comment 1: citations and bibliography

**Response.** Thank you. We have begun a citation-level audit that maps manuscript citation keys to the available inventories and records source-checked title and version relationships. The representative-evidence table cites the studies associated with its reported results. We will complete a final check of citation-to-claim support, publication metadata and bibliography formatting before resubmission; the current mapping is not a certification of every technical claim.

**Changes made.** The citation mapping and priority source checks are recorded under `reproduct/audit/`; the revised comparison table and bibliography are in the manuscript. [Insert final page/line numbers after completing the verification.]

## Reviewer 1, comment 2: retrospective selection limitations

**Response.** We have retained a clear account of the historical search and selection limitations in the Survey Methodology section. We distinguish the historical scored records, the later merged candidates and the separate exploratory search audit, and avoid treating these quantities as stages of a verified flow.

**Changes made.** Section III describes the available records, limitations and counting units. [Insert final page/line numbers.]

## Reviewer 1, comment 3: proofreading and presentation

**Response.** We have revised the presentation of the search method, evidence table and related-work comparisons. A final proofreading pass of the complete manuscript, including figures, captions, tables, cross-references and language, remains to be completed before resubmission.

**Changes made.** Revised Section III, introduction and representative-study comparison. [Insert final page/line numbers after proofreading.]

## Reviewer 2, comment 1: search procedures, eligibility criteria and study-selection statistics

**Response.** Thank you for asking us to strengthen the methodology. We revised Section III to describe the intended inclusion and exclusion criteria, the available record counts and the limits of the surviving selection history. The original search dates, database-specific execution logs and record-level screening decisions could not be recovered. We therefore describe the article as a retrospective survey and do not present its historical collection as a fully reproducible systematic search.

To make the available evidence inspectable, we provide the surviving historical inventory, a record-level crosswalk and the later merged candidate inventory. The historical archive has 485 rows, of which 220 carry the original 1–3 relevance scores (45, 116 and 59 respectively). The other 265 rows include zero, missing and other values and cannot be treated as verified exclusions. Although the score distribution matches the earlier manuscript, we cannot establish from these counts alone that the archived rows are identical to the previously submitted supplementary file. The later 225-row candidate inventory is a different selection with revised scores; neither inventory establishes the number of unique eligible studies.

We also document a separate exploratory search on 5 November 2026 using Crossref and arXiv, with database-specific query logs, timestamps, limits and exact-identifier linkage. Provider responses are retained in the research archive. The top-100 Crossref and arXiv snapshot contains 10,467 retrieved hit rows and 6,408 provisional identifier groups; the Crossref queries and two arXiv queries were truncated. The two truncated arXiv topics were subsequently rerun with pagination and are documented as a separate time-stamped search. The search caps, differences in source coverage and unresolved versions limit recall and preclude an exhaustive-coverage claim.

For transparency, the supplementary materials identify the automated title/abstract triage, model, protocol, decision fields and conservative flags. Individual prompts and responses are retained in the research archive; a metadata-only public release omits those materials and third-party abstracts, so it cannot by itself support complete offline replay. Two calls for records with available abstracts were made to the same model in separate sessions; they were **not** independent human screening. The resulting labels are preliminary, and no final study-selection count is inferred from them. Missing abstracts, conflicting labels and uncertain versions remain identified for further review.

**Changes made.** Section III now describes the intended eligibility scope, historical uncertainty, separate search update, linkage rules and limits. The supplementary files contain the query logs, record mappings, candidate inventories and screening audit. [Insert final page/line numbers and public archive URL.]

## Reviewer 2, comment 2: novelty relative to existing surveys

**Response.** We have added a comparison with representative surveys of LLMs in software engineering, vulnerability detection, automated program repair and cybersecurity. The comparison makes explicit this article's organizing perspective: OS components and privileged interfaces, the security workflows associated with each component, the artifacts used for validation, and the distinction between direct OS-security evidence, transferable techniques and studies that protect LLM execution. We present this as the focus of our synthesis rather than a claim that prior reviews never cover OS-related examples.

**Changes made.** The introduction contains a related-survey discussion and comparison table. [Insert final page/line numbers.]

## Reviewer 2, comment 3: comparative tables

**Response.** We have added a representative evidence table covering KernelGPT, SyzAgent, BugLens, KNighter, MigGPT, PathSentinel, LLM-CAL and an OpenAI kernel-security pipeline. It records each study's target and task, the model's role and validation, evaluation setting or baseline, reported result and limitation. These examples cover different tasks and do not form a uniform benchmark; the table and accompanying text avoid ranking incompatible metrics as directly comparable.

**Changes made.** The representative-evidence table and cross-study synthesis appear in the OS-security discussion. [Insert final page/line numbers.]

## Reviewer 2, comment 4: critical synthesis

**Response.** We have added cross-study analysis of the point at which each approach uses an LLM and the supporting evidence supplied by fuzzing, static analysis, checker synthesis, patch migration and exploit validation. The discussion explains why target reachability, precision, vulnerability counts and patch semantic match measure different outcomes, and identifies dependencies on interfaces, input analyzers, historical patches and kernel versions.

**Changes made.** A cross-study synthesis follows the representative-evidence table, with additional qualification in the component discussions. [Insert final page/line numbers.]

## Reviewer 2, comment 5: direct and adjacent work

**Response.** We have stated the distinction among studies evaluating LLM assistance on an OS-security task, potentially transferable methods evaluated on another target, and adjacent work using OS mechanisms to protect LLM systems. The revised networking and hypervisor/TEE discussions explain how the evaluated target limits the inference to an OS-security setting.

**Changes made.** The distinction is introduced in the OS-security overview and applied in the component discussions. [Insert final page/line numbers.]

## Reviewer 2, comment 6: weakly related references

**Response.** We reviewed the works identified by the reviewer using the reference numbers in the submitted version. We removed the discussion of QiMeng-Attention, SparSamp and RECoRD from the principal component discussions. We condensed the protection-of-LLMs material to a clearly labelled adjacent architectural example, retaining TZ-LLM for that limited purpose. It is not treated as direct evidence that an LLM improves hypervisor or TEE security. We will complete the remaining bibliography and claim-to-reference verification before resubmission.

**Changes made.** The kernel, networking, hypervisor/TEE and system-service discussions were revised; the relevant source checks are recorded under `reproduct/audit/`. [Insert final page/line numbers.]

## Reviewer 2, comment 7: language, figures and tables

**Response.** We have revised the structure and wording around the methodology, comparison tables and scope distinctions. We will complete a manuscript-wide language and presentation check, including the final figures, table layout and cross-references, before submission.

**Changes made.** Introduction, methodology, evidence table and component discussions revised. [Insert final page/line numbers after final proofreading.]

## Reviewer 3, comment 1: reproducibility of the survey methodology

**Response.** We agree that the original documentation did not support a fully reproducible search. We could not reconstruct exact historical search dates, database-specific queries, independent screening arrangements or disagreement-resolution procedures. We have therefore consistently repositioned the work as a retrospective literature survey and limited statements about coverage. The 18 historical formulations are provided in the reproducibility directory, and the manuscript gives an example while distinguishing them from a verified database execution log.

We distinguish this historical collection from the later Crossref/arXiv exploratory search. Its query-level logs, dates, request parameters and exact-identifier linkage are documented; the research archive retains the result snapshots and scripts used to recompute the record mapping. A metadata-only public release omits provider responses and abstracts and therefore cannot fully reproduce this processing offline without separately obtaining the omitted inputs. Source-specific date filters and result caps are disclosed. We also disclose use of automated triage, the absence of a documented independent human screening and adjudication process, and the fact that unique eligible-study counts have not been established. These measures improve traceability of the available material without implying that the missing historical decisions have been recovered.

**Changes made.** Section III identifies the retrospective scope; the search-protocol and screening documentation records the newer activity and its limitations. The original title is retained. [Insert final page/line numbers and public archive URL.]

## Reviewer 3, comment 2: supplementary inventory and record terminology

**Response.** We agree that the inventory should be independently inspectable and its fields and counting units should be clear. We have prepared a historical 220-record scored inventory, a 225-record merged candidate inventory, a 485-row crosswalk and a list of potential duplicate or version pairs. Their fields, preliminary relevance scores, source identifiers and evidence-status information are described in the reproducibility directory. Record identifiers are not bibliography numbers or unique-study identifiers.

The two inventories are not consecutive stages of one verified selection flow. The later inventory retains previously classified related and direct candidates and adds candidates from the exploratory update; its scores are not equivalent to the original scores. Exact-identifier matching can leave preprint and publication versions separate. A record in either file is not automatically an eligible study, and we do not report a unique eligible-study total until version reconciliation and eligibility assessment have been completed.

**Changes made.** Survey Methodology points to the reproducibility directory, where the inventories and matching notes are documented. [Before submitting, publish the files and insert the verified repository URL here and in the manuscript; verify that the released files match the descriptions.]

## Reviewer 3, comment 3: KernelGPT workflow example

**Response.** We agree. The KernelGPT example is presented as an account of the workflow reported in the cited study. It illustrates implementation artifacts, generated specifications, validation feedback and downstream fuzzing; it is not an experiment conducted for this survey and is not empirical validation of the survey taxonomy.

**Changes made.** The device-driver example and its references in the methodology and conclusion retain this qualification. [Insert final page/line numbers.]

## Reviewer 3, comment 4: consistency of coverage claims

**Response.** We agree that the available evidence does not justify an exhaustive-coverage claim. We have retained the original title and revised the abstract, introduction, methodology and conclusion to explain the retrospective scope. We also removed the earlier selection-flow presentation that could imply the unverified 485-to-220 transition was a complete documented screening process. The historical score counts and later candidate counts are reported with their respective meanings, and the unique eligible-study count remains unestablished.

**Changes made.** Revised the abstract, introduction, Section III and conclusion. [Insert final page/line numbers.]

## Reviewer 3, comment 5: references and technical claims

**Response.** Thank you. We have performed targeted source checks for representative studies and recorded bibliographic aliases and issues requiring follow-up. For example, we clarified that the MigGPT paper includes a CVE-backporting evaluation and distinguished PathSentinel's static-analysis detection from the LLM-assisted validation role. The new evidence table links its numerical statements to the corresponding publications and identifies the scope of each evaluation. The targeted checks do not replace a complete final claim-to-reference audit, which remains to be completed before submission.

**Changes made.** The representative comparison, MigGPT discussion and documented source checks were updated. [Insert final page/line numbers after completing the audit.]
