# [보존] 1차 R3 하위 워커 — arc42·C4·SEI 뷰·문서량 논쟁 (완주분)

I have comprehensive primary-source coverage. Here are the findings.

---

# Axis: Software Architecture Documentation Frameworks — "which layer holds what, and how much"

---

## 1. arc42 — the 12 sections and its explicit "how much" guidance

### 1.1 The 12 sections and their stated intent

Source: [arc42.org/overview](https://arc42.org/overview/)

| # | Section | Stated purpose (verbatim) |
|---|---------|---------------------------|
| 1 | Introduction & Goals | "Fundamental requirements, especially quality goals" |
| 2 | Constraints | "Regulations and external constraints" |
| 3 | Context & Scope | "External systems and interfaces" |
| 4 | Solution Strategy | "Core ideas and solution approaches" |
| 5 | Building Block View | "Structure of source code, modularization, hierarchically refined. **Usually the most extensive section**" |
| 6 | Runtime View | "Important runtime scenarios" |
| 7 | Deployment View | "Hardware, infrastructure and deployment" |
| 8 | Crosscutting Concepts | "Overarching topics… technology choices, recurring patterns, development and deployment processes" |
| 9 | Architectural Decisions | "Important decisions, **unless described elsewhere**" |
| 10 | Quality Requirements | "Quality tree and quality scenarios" |
| 11 | Risks & Technical Debt | "Known problems and risks" |
| 12 | Glossary | "Important and specific terms ('ubiquitous language')" |

Detail on the sections you flagged:

**§1 Introduction and Goals** ([docs.arc42.org/section-1](https://docs.arc42.org/section-1/)) — captures "relevant requirements and the driving forces that software architects and development team must consider." It carries a **hard numeric cap**: quality goals are "**The top three (max five) quality goals** for the architecture whose fulfillment is of highest importance to the major stakeholders." They must be concrete, not buzzwords. Also holds the stakeholder table (role, name, expectations).

**§4 Solution Strategy** ([section-4](https://docs.arc42.org/section-4/)) — "a **short summary** and explanation of the fundamental decisions and solution strategies that shape the system's architecture." Covers technology decisions, top-level decomposition, patterns, how quality goals are met, organizational decisions. Tips: 4-1 "Explain the solution strategy **as compact as possible (e.g. as list of keywords)**"; 4-2 "Describe the solution approaches **as a table**" linking quality goals → scenarios → solutions; 4-4 "In the solution strategy, **refer to** concepts, views or code."

**§5 Building Block View** ([section-5](https://docs.arc42.org/section-5/)) — static decomposition, hierarchically refined L1/L2/L3. Motivation: "maintain an overview of your source code by making its structure understandable **through abstraction**." Depth guidance is explicitly anti-completeness: "**prefer relevance over completeness**… specify important, surprising, risky, complex or volatile building blocks. **Leave out normal, simple, boring or standardized parts.**" Tip 5-3: always describe Level-1 ("Level-1 is your friend") because it is stable and cheap to maintain; deeper levels require selective justification.

**§8 Crosscutting Concepts** ([section-8](https://docs.arc42.org/section-8/)) — practices/patterns/regulations spanning multiple building blocks: logging, authn/authz, domain model, data model. Purpose: "form the basis for **conceptual integrity** (consistency, homogeneity) of the architecture," and they exist to **prevent redundant documentation** by addressing crosscutting concerns in one place instead of repeating them per building block. Explicit warning: "Pick only the most-needed topics… **DO NOT ATTEMPT to cover all of the topics.**"

**§9 Architecture Decisions** ([section-9](https://docs.arc42.org/section-9/)) — "Important, expensive, large scale or risky architecture decisions **including rationales**." Motivation: "Stakeholders of your system should be able to comprehend and retrace your decisions." Diagnosis it names: teams "know about the decision, as it is visible e.g. in source code, but **miss the motivation behind that decision**."

**§10 Quality Requirements** ([section-10](https://docs.arc42.org/section-10/)) — see §1.4 below.

**§11 Risks & Technical Debt** ([section-11](https://docs.arc42.org/section-11/)) — "a list of identified technical risks or technical debts, **ordered by priority**," plus suggested mitigations. Audience is explicitly management (PM/PO) for risk analysis and measure planning. Six tips are all *detection* techniques (interview stakeholders, analyze external interfaces, processes, data structures, source code) — i.e. §11 is a findings register, not a narrative.

### 1.2 arc42's explicit anti-over-documentation guidance — this is the money section

**FAQ E-3, "How can arc42 help us in reducing documentation effort?"** ([faq.arc42.org/questions/E-3](https://faq.arc42.org/questions/E-3/)) — four strategies:

1. "**Less is often more.** Keep documentation short and focussed. **Don't try to explain the whole world.**"
2. "**Focus on important, interesting, special or risky topics, instead of striving for completeness.**"
3. Document crosscutting **concepts** rather than detailing many individual building blocks.
4. "**Use abstractions**, especially in the building block view and runtime view."

**FAQ E-7, "Most important tips for documentation in agile projects"** ([E-7](https://faq.arc42.org/questions/E-7/)):

1. Appoint a "**Docu-Gardener**" — "even in a Scrum-team, appoint a person responsible for documentation" to maintain quality and **remove outdated material**.
2. "**Document economically** ('Less is often more')."
3. "Clarify appropriateness and needs through **early feedback**."
4. ★ "**Focus on explanation and rationale, not only facts**" — because **"source code contains facts,"** so documentation should supply reasoning and context. *This is arc42's version of "don't document what the code says."*
5. "Rate requirements higher than principles."

**FAQ E-5, "What to write down vs. communicate orally"** ([E-5](https://faq.arc42.org/questions/E-5/)) — deliberately gives no content rule; it gives a **stakeholder simulation test**: "Imagine you're a future stakeholder who then needs to work on the system (implement, architect, deploy, test, operate, monitor or other). Then ask yourself **what information you need to have**…" Process: identify stakeholder groups → ask each what they need → prioritize and fold into Definition-of-Done.

**FAQ E-6, "Can we defer documentation?"** ([E-6](https://faq.arc42.org/questions/E-6/)) — "In theory, yes. In practice such a deferral means that this documentation will (quite likely) **never ever be created**." Recommendation: "document economically (short, brief, compact and with as-low-as-possible effort), **but do this continuously**."

**Per-section brevity tips** ([docs.arc42.org/keywords](https://docs.arc42.org/keywords/)) — arc42 publishes a keyword index of tips; the brevity cluster:

| Tip | Text |
|---|---|
| 3-5 | "Restrict the context to an overview, avoid too many details!" |
| 4-1 | "Explain the solution strategy as compact as possible (e.g. as list of keywords)!" |
| 5-21 | "Describe or specify internal interfaces with **minimal effort**!" |
| 5-28 | "**Explain concepts instead of building blocks!**" |
| 6-2 | "Document **only a few** runtime scenarios!" |
| 6-3 | "Document 'schematic' (instead of detailed) scenarios!" |
| 8-9 | "**Document decisions instead of concepts!**" |
| 9-1 | "Document **only architecturally relevant** decisions!" |
| 12-5 | "Keep the glossary compact! **Avoid trivia.**" |

Also, the template itself is opt-in per section: "Everything is optional — there is no need to fill in every section of the template."

### 1.3 arc42 §9 ↔ ADRs — the relationship, and the routing rule

Source: [docs.arc42.org/section-9](https://docs.arc42.org/section-9/), [tip 9-1](https://docs.arc42.org/tips/9-1/), [tip 8-9](https://docs.arc42.org/tips/8-9/)

- **ADRs are the recommended format for §9 content.** arc42 endorses Michael Nygard's structure: Title, Context, Decision, Status (proposed/accepted/deprecated/superseded), Consequences (positive *and* negative).
- **§9 is explicitly a "unless described elsewhere" section.** The overview literally qualifies it that way, and the section page says: "**Avoid redundant texts. Refer to section 4**, where you captured the most important decisions of your architecture already." So §4 holds the *few* shaping decisions inline; §9 holds the rest as records; decisions local to one building block are documented **inside that building block**, not in §9.
- **Tip 9-1 — the relevance filter.** Architecturally relevant = decisions that "affect the **structure, non-functional characteristics, dependencies, interfaces, or construction techniques**." Document a decision when it is: critical/important; influences important quality attributes; **unconventional / off the beaten track**; risky with expensive consequences; long-lasting; affects many or very important stakeholders; took substantial time/effort to decide; or is **astonishing or surprising**. Explicitly *not* every minor development choice.
- **Tip 8-9 — the concept/decision routing algorithm.** arc42 states concepts are "special cases of architecture and/or design decisions," and gives a literal branch:

  > `if (extensive-explanation-required) then concept else decision`

  and adds that a decision in §9 can simply **reference source code or unit tests**, which is often sufficient without a prose concept. This is a directly reusable routing rule.
- **Tip 5-28** — for systems whose structure is governed by a pattern (microservices, pipes-and-filters), explain the **concept** rather than enumerating building blocks — but keep the Level-1 view (tip 5-3).

### 1.4 arc42's quality tree / quality scenarios (relevant to the test-strategy doc)

Source: [docs.arc42.org/section-10](https://docs.arc42.org/section-10/), [tip 10-3](https://docs.arc42.org/tips/10-3/)

- **§10.1 Quality tree** — quality requirements summarized as a hierarchy: generic "quality" at the root, refined into categories (ISO 25010:2023 or the Q42 model), leaves pointing at concrete scenarios. Also called a **"Quality Attribute Utility Tree."** Tip 10-3: "Mind-maps provide the ability to hierarchically structure (like a tree), but are sometimes **more reader-friendly**" — arc42 explicitly trades a table for a mind-map on readability grounds.
- **§10.2 Quality scenarios** — the mechanism that makes quality "specific and **measurable**." Two kinds:
  - **Usage scenarios** — "the system's runtime reaction to a certain stimulus" (e.g. "The system reacts to a user's request within one second").
  - **Change scenarios** — "the desired effect of a modification or extension of the system," measured in effort or duration.
  - Minimal form: context + stimulus source + measurable acceptance criteria. Extended form adds scenario ID, artifact, response, response measure.
- Tips recommend: keep quality goals concise; use the tree **as a checklist**; cover usage, change **and fault/error** scenarios; and reuse scenarios for architecture analysis / ATAM evaluation.
- **§1.2 holds only the top 3–5;** §10 holds the full set including "nice-to-have" qualities. The layering is: §1 = the short prioritized list, §10 = the tree + measurable scenarios.

---

## 2. C4 model (Simon Brown) — levels, which to keep, diagram rules

### 2.1 The four levels and the abstraction-first principle

Source: [c4model.com](https://c4model.com/), [c4model.com/abstractions](https://c4model.com/abstractions)

C4 is "an **'abstraction-first' approach** to diagramming software architecture, based upon abstractions that reflect how software architects and developers think about and build software." The hierarchy: **people** use **software systems**; software systems are made of **containers** (separately deployable/runnable applications and data stores); containers contain **components**; components are made of **code** elements.

It is explicitly **notation independent** and **tooling independent**: "The C4 model is notation independent, and doesn't prescribe any particular notation" ([notation page](https://c4model.com/diagrams/notation)). The stated benefit is a shared vocabulary: "The small set of abstractions and diagram types makes the C4 model easy to learn and use."

### 2.2 Which levels are worth maintaining — the explicit guidance

Source: [c4model.com/diagrams](https://c4model.com/diagrams), [c4model.com/diagrams/code](https://c4model.com/diagrams/code)

- **The overarching rule:** "**you don't need to use all 4 levels of diagram; only those that add value.**" System Context + Container diagrams suffice for most teams; Component and Code are available when extra detail is warranted.
- **Level 4 (Code) is explicitly discouraged as maintained documentation.** From the Code diagram page:
  - "This is **very much an optional level of detail** and is often available **on-demand from tooling such as IDEs**."
  - "Ideally this diagram would be **automatically generated** using tooling (e.g. an IDE or UML modelling tool)."
  - Answering whether to create them: "**No, particularly for long-lived documentation**, because most IDEs can generate this level of detail on demand."
- Rationale for the multi-level structure: the levels "allow you to **tell different stories to different audiences**" — i.e. levels are audience segmentation, not completeness tiers.
- **Splitting over consolidating** ([FAQ](https://c4model.com/faq)): "don't be afraid to **split that single complex diagram into a larger number of simpler diagrams**, each with a specific focus around a business area, functional area, functional grouping, bounded context, use case, user interaction, feature set, etc."

### 2.3 Diagram rules — every diagram needs a title, key, and self-describing elements

Source: [c4model.com/diagrams/notation](https://c4model.com/diagrams/notation), [c4model.com/diagrams/checklist](https://c4model.com/diagrams/checklist)

Verbatim rules:
- "**Every diagram should have a title** describing the diagram type and scope" (e.g. "System Context diagram for My Software System").
- "**Every diagram should have a key/legend** explaining the notation being used" (shapes, colours, border styles, line types, arrow heads).
- "Any notation used should be **as self-describing as possible**, but **all** diagrams should have a key/legend to make the notation explicit. **This applies to diagrams created with notations such as UML, ArchiMate and SysML too**, as not everybody will know the notation being used."
- "The **type** of every element should be explicitly specified (e.g. Person, Software System, Container or Component)."
- "Every element should have a **short description**, to provide an **'at a glance' view of key responsibilities**."
- "Every container and component should have a **technology** explicitly specified."
- "Every line should represent a **unidirectional** relationship"; "Every line should be **labelled**, the label being consistent with the direction and intent"; container-to-container relationships get "a technology/protocol explicitly labelled."
- "Acronyms and abbreviations… should be understandable by all audiences, or explained."

The **review checklist** is framed as reader-comprehension questions, not author-compliance questions — "Do *you understand* what every element does?", "Do *you understand* the meaning of all colours used?" That framing itself is a transferable review technique.

### 2.4 "The code doesn't tell the whole story" — why architecture docs still matter

Primary source: Simon Brown, *Software Architecture for Developers*, [conference extract PDF](https://static.codingthearchitecture.com/sddconf2014-software-architecture-for-developers-extract.pdf) (ch. 16 "The code doesn't tell the whole story", ch. 17 "Software documentation as a guidebook"). Also [dev.to/simonbrown — A minimal approach to software architecture documentation](https://dev.to/simonbrown/a-minimal-approach-to-software-architecture-documentation-4k6k).

**The core argument** (verbatim from ch. 17):

> "**'Working software over comprehensive documentation'** is what the Manifesto for Agile Software Development says and it's incredible to see **how many software teams have interpreted those five words as 'don't write any documentation'**. The underlying principle here is that real working software is much more valuable to end-users than a stack of comprehensive documentation but **many teams use this line in the agile manifesto as an excuse to not write any documentation at all**. Unfortunately the code doesn't tell the whole story and **not having a source of supplementary information about a complex software system can slow a team down as they struggle to navigate the codebase**."

**What the code cannot tell you** (his list — note his worked example is literally an internet banking system):
- How the system fits into the existing system landscape
- Why the technologies in use were chosen
- The overall structure of the system
- Where components are deployed at runtime and how they communicate
- What approach to logging/configuration/error handling was adopted and **whether it is consistent across the codebase**
- Whether any common patterns and principles are in use
- **How and where to add new functionality**
- How security has been implemented across the stack
- How scalability is achieved / how interfaces with other systems work

And the killer line on why "just read the code" fails: "Reading the code will get you so far but you'll probably need to ask questions to the rest of the team at some point. And **if you don't ask the right questions, you won't get the right answers — you don't know what you don't know.**"

He also cites Grady Booch via the dev.to piece: "**The code is the truth, but not the whole truth.**"

**His upper bound on detail** (ch. 17, "Keep it short, keep it simple"):

> "**Do resist the temptation to go into too much technical detail** though because **the technical people that will understand that level of detail will know how to find it in the codebase anyway.** As with everything, there's a happy mid-point somewhere."

**His minimal set** (dev.to): (1) System Context diagram, (2) Container diagram, (3) Deployment diagram(s), (4) lightweight narrative docs in Markdown/AsciiDoc — a software guidebook **or arc42**, (5) **ADRs**. Framed as "a starting point."

**The software guidebook headings** (13): Context, Functional Overview, Quality Attributes, Constraints, Principles, Software Architecture, External Interfaces, Code, Data, Infrastructure Architecture, Deployment, Operation and Support, **Decision Log**.

**Product vs project documentation** — a distinction highly relevant to a 50-doc banking corpus:

> "the style of documentation that I'm referring to here is related to the **product** being built rather than the **project** that is creating/changing the product… organisations [have] software systems approaching twenty years old and, although they have varying amounts of project-level documentation, **there's often nothing that tells the story of how the product works and how it's evolved**… New joiners in such environments are often expected to simply read the code and fill in the blanks by tracking down documentation produced by various project teams."
>
> "I recommend that software teams create a **single software guidebook for every software system**… Once a single software guidebook is in place, **every project/change-stream/timebox to change that system is exactly that — a small delta.**"

**The map/zoom metaphor** — his justification for levels: satellite imagery at max zoom shows the most detail but you can't tell where you are; "**this abstraction allows us to see some of the major structural elements… along with some of the place names, which were previously getting obscured by the detail.**" Detail actively obscures orientation. He also diagnoses the failure mode being fixed: "when software teams think about documentation, they usually think of **huge Microsoft Word documents based upon a software architecture document template from the 1990's**… **Few people enjoy reading this type of document, let alone writing it!**"

**C4 ↔ arc42 mapping** (from the [C4 FAQ](https://c4model.com/faq)) — they are explicitly compatible:
- Context and Scope (arc42 §3) → System Context diagram
- Building Block View level 1 (§5) → Container diagram
- Building Block View level 2 → Component diagram
- Building Block View level 3 → Code diagram

And C4's scope limit: business processes, workflows, state machines, domain models and data models are **out of scope** for C4 — "feel free to supplement the C4 diagrams with UML diagrams, BPML diagrams, ArchiMate diagrams, entity relationship diagrams, etc."

---

## 3. The "documentation should be short" debate — both sides, sourced

### 3.1 The Agile Manifesto and how it is misread

- The Manifesto's own text is a **preference, not a negation**: it values working software over comprehensive documentation "**while there is value in the items on the right**." ([agilemanifesto.org](https://agilemanifesto.org/))
- The [12 principles](https://agilemanifesto.org/principles.html) never mention documentation. The two relevant ones: "The most efficient and effective method of conveying information to and within a development team is **face-to-face conversation**," and "**Simplicity — the art of maximizing the amount of work not done — is essential.**"
- arc42 states the correction flatly ([FAQ category E](https://faq.arc42.org/category_e/)): "The Agile Manifesto says: 'Working software over comprehensive documentation'. It does **not** say 'no documentation'."
- Simon Brown's version is quoted in §2.4 above.

### 3.2 Side A — "less, and later" (Scott Ambler / Agile Modeling)

Sources: [Lean/Agile Documentation: Strategies for Agile Teams](https://agilemodeling.com/essays/agiledocumentation.htm), [Core Practices for Lean/Agile Documentation](https://agilemodeling.com/essays/agiledocumentationbestpractices.htm), [Just Barely Good Enough (JBGE)](https://agilemodeling.com/essays/barelygoodenough.htm)

**The JBGE model — with an actual economic argument, not just a slogan:**

> "if an artifact is JBGE then **by definition it is at the most effective point that it could possibly be at**."
>
> "The point of maximal value is where **the incremental cost of adding more to the artifact exceeds the incremental value being added**." Beyond it, "any effort to the right of this point **removes net value** from the artifact because the cost expended is rising faster than the benefit gained."
>
> "once an artifact fulfills its intended purpose then **any more investment in it is simply busy work**."

**Ambler's strongest claims** (from the documentation essay):
- "Documentation should be concise: **overviews/roadmaps are generally preferred over detailed documentation**."
- "**Comprehensive documentation does not ensure success, in fact, it increases your chance of failure.**"
- "Developers **rarely trust the documentation**, particularly detailed documentation, because it's usually out of sync with the code."
- Agilists "see documentation as a strategy which **increases overall risk**."
- The decision test: "Ask whether you **NEED** the documentation, not whether you **want** it."
- Value criteria: agile documents maximize stakeholder ROI; stakeholders know the **TCO** of the document; documents are "lean and sufficient"; **fulfill a purpose**; describe "good things to know"; **have a specific customer**.

**The core practices** (from the best-practices essay) — the ones that map directly onto a doc-set rewrite:

*What to document:*
- **Document With a Purpose** — "You should only create a document if it **fulfills a clear, important, and immediate goal**." Explicitly warns against template-driven documentation ("avoid template-based approaches" — each system's needs differ).
- **Focus on the Needs of Actual Customers** — identify real readers, negotiate "the **minimal sufficient subset** they need."
- **The Customer Determines Sufficiency** — the reader, not the author, is the quality gate.
- **Require People to Justify Documentation Requests** — challenge requesters on what they'll use it for; often documents are "**security blankets**" masking trust issues.
- **Recognize That You Need Some Documentation** — "Documentation is as much a part of the system as the source code." (Ambler is not a no-docs advocate.)

*How to structure:*
- **Write the Fewest Documents With Least Overlap** — interconnected small single-topic pieces rather than duplication.
- **Single Source Information** — "Strive to capture information in **one place and one place only**."
- **Put Information in the Most Appropriate Place** — where the reader will naturally look (code comment vs diagram vs external doc).
- **Keep Documentation Just Simple Enough, But Not Too Simple** — "**The best documentation is the simplest that gets the job done**"; overviews over exhaustive detail; sketches over elaborate diagrams.

*When to write:*
- **Document Late / Document Stable Concepts, Not Speculative Ideas** — "By waiting to document information **once it has stabilized** you reduce both the cost and the risk associated with documentation."
- **Document Continuously** — capture throughout, defer the polish.
- **Update Only When It Hurts** — update only when staleness measurably impedes productivity.
- **Start With Models You Actually Keep Current** — "If you've chosen to keep your [diagram] up to date… that is a good sign that these are valuable." Abandoned artifacts are evidence of low value. *(This is an empirical test you can run on the existing 50 docs.)*
- **Iterate** — "Write a little bit, show it to someone, get feedback, act on that feedback, and then iterate."
- **Prefer Executable Specifications Over Static Documents** — "The majority of the information captured in traditional specification documents… can be captured as **executable specifications in the form of tests**."
- **Generate System Documentation** where tooling can reverse-engineer it.
- **Treat Documentation Like a Requirement** — "estimated, prioritized, and put on your work item stack along with all other work items."
- **Find Better Ways to Communicate** — "Documentation is only one of several options available to you and… **often isn't the best option**."

### 3.3 Side B — under-documenting costs more

- **Simon Brown** (above): missing supplementary information "**can slow a team down as they struggle to navigate the codebase**"; handover/offshoring cases where complex systems shipped "without a single piece of supporting documentation"; the "you don't know what you don't know" problem that defeats "just ask the team."
- **arc42 FAQ E-6**: deferral in practice means the documentation "will (quite likely) **never ever be created**," and stakeholders end up reading source.
- **arc42 FAQ E-7 / E-5**: the future-stakeholder test — implement, architect, deploy, **test**, operate, monitor — presumes those roles have information needs the code cannot serve.
- **SEI Principle 5, Record rationale**: "the reasoning behind a decision may be **forgotten in as little as a few weeks**" ([CMU/SEI-2004-TN-037](https://www.sei.cmu.edu/documents/2057/2004_004_001_14351.pdf), p.3). This is the strongest sourced argument for ADR-style rationale capture: the decay window is weeks, not years.
- **Empirical, on reliance**: in a study of OSS adoption (10 interviews + 42 survey respondents), "**All ten participants confirmed that they rely on OSS documentation**"; **91.18%** indicated dependence on documentation for adoption decisions; median importance 5/5 (interviews) and 4/5 (survey), with **74%** rating it 4 or 5 ([arXiv:2403.03819](https://arxiv.org/html/2403.03819v1)).

### 3.4 Counter-evidence — long docs go unread, and staleness

- **SEI's own critique of the monolithic SAD** ([CMU/SEI-2004-TN-037](https://www.sei.cmu.edu/documents/2057/2004_004_001_14351.pdf), p.19) — this is the sharpest sourced statement of the failure mode being diagnosed:

  > "A traditional document, **in the effort to reduce bulk and still address the needs of a general audience, inevitably contains much information that is unneeded by some users and lacks information required by others. The more sophisticated user skims the document, perhaps missing key elements, and other users become frustrated and search for different reference materials.**"
  >
  > "Documentation created for a general audience **suffers from its sheer size**. Notebooks full of paper are cumbersome, and large digital files are difficult to navigate and search."
  >
  > On repetition: "Repetition is **the root of inconsistency**. Keeping track of all repeats is difficult, if not impossible; thus, repeated information becomes inconsistent over time, and **attempts to avoid these inconsistencies are costly**."

  SEI's remedy is *not* "write less" — it is **per-stakeholder generated views over a single repository**, with access-controlled, role-tailored renderings of one source. That is a materially different fix than shortening.
- **SEI Principle 6**: "Documentation that is incomplete or out of date **does not reflect truth, does not obey its own rules for form and internal consistency, and is not used.**" (p.3 / [InformIT excerpt](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5)) — this is the closest authoritative source to the "stale documentation is worse than none" claim; note it says *not used*, not *worse than none*.
- **Ambler**: "Developers rarely trust the documentation, particularly detailed documentation, because it's usually out of sync with the code."
- **Empirical, on staleness**: same OSS study — ~60% cited **version–documentation inconsistency**, ~55% **missing information**, ~50% **reading challenges**, ~45% **difficulty finding relevant information** ([arXiv:2403.03819](https://arxiv.org/html/2403.03819v1)).
- **Caveat on the "78% of developers struggle with outdated docs" figure**: this circulated in secondary search results and I could not trace it to a primary study. Treat as unsourced — do not cite.

**Where the two sides actually agree** (this is the useful synthesis): both camps reject *comprehensive* documentation, and both locate value in **rationale, orientation, and cross-cutting invariants** — the things code and tests cannot express. The disagreement is only about *default posture* (write-late-and-minimal vs. maintain-a-standing-guidebook), not about content selection.

---

## 4. Views/viewpoints tradition and the stakeholder-driven selection rule

### 4.1 ISO/IEC/IEEE 42010

Sources: [iso-architecture.org/42010/cm](http://www.iso-architecture.org/42010/cm/), [Getting started](http://www.iso-architecture.org/ieee-1471/getting-started.html), [arc42 quality model summary](https://quality.arc42.org/standards/iso-42010)

- A **viewpoint** is "the set of conventions for the creation, interpretation and use of an architecture view **to frame one or more concerns**" of stakeholders. A **view** is a viewpoint applied to a system.
- The conformance chain is the load-bearing part: identify **stakeholders** → identify their **concerns** → **each concern must be framed by at least one viewpoint** → views conform to viewpoints. Stakeholder concerns must be explicitly addressed in the architecture description.
- Practical consequence: **a view with no stakeholder concern behind it has no standing.** The standard makes concern-coverage the completeness criterion — not structural coverage.
- The 2022 2nd edition adds **Stakeholder Perspectives** as a way to group concerns and thereby organize viewpoints.
- ANSI/IEEE 1471-2000 required at minimum that **users, acquirers, developers, and maintainers** be considered (quoted in [CMU/SEI-2004-TN-037](https://www.sei.cmu.edu/documents/2057/2004_004_001_14351.pdf), p.A-6).

### 4.2 Kruchten's 4+1

Source: [4+1 View Model of Architecture (IEEE Software, 1995)](https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf)

Each view is defined **by its audience**, which is the point:

| View | Concern | Audience |
|---|---|---|
| Logical | functional requirements; problem-domain abstractions | analysts, designers |
| Process | concurrency, synchronization, performance | system integrators |
| Development | static organization of software in the dev environment | developers, managers |
| Physical | mapping of software to hardware/nodes | system engineers, deployers |
| Scenarios (+1) | ties the four together; validates them | all stakeholders |

Kruchten explicitly permits dropping views: **not all views are necessary for every project** — simpler systems may not require all five, and the model should be tailored to complexity and stakeholder needs. The "+1" scenarios view is the **validation** mechanism: it is what proves the other four are consistent and sufficient.

### 4.3 SEI "Views and Beyond" — the explicit rule you asked for

Sources: [CMU/SEI-2004-TN-037](https://www.sei.cmu.edu/documents/2057/2004_004_001_14351.pdf); [Views and Beyond: The SEI Approach](https://www.sei.cmu.edu/documents/2546/2018_010_001_513864.pdf); [DSA: Views and Beyond, 2nd ed.](https://sei.cmu.edu/library/documenting-software-architectures-views-and-beyond-second-edition/)

**The selection rule, verbatim** (TN-037 §1.3, p.3–4):

> "Before documentation begins, the architect creates a **table of stakeholders versus views** in which each stakeholder's needs are recorded. **Each view comes with a cost, and each view comes with a benefit. Available resources must be weighed against stakeholders' needs.** The architect must balance these opposing concerns carefully."

And in the SAD template (p.A-5/A-6), the stakeholder matrix is not decoration — it is the **justification artifact**:

> "This information is represented as a matrix, where the rows list stakeholder roles, the columns list concerns, and a cell in the matrix contains an **indication of how serious the concern is** to a stakeholder in that role. **This information is used to motivate the choice of viewpoints chosen in Section 1.5.**"

> "ANSI/IEEE 1471-2000 provides guidance for choosing the best set of views to document, **by bringing stakeholder interests to bear**… Together, the chosen set of views show the entire architecture and all of its relevant properties."

V+B is deliberately **not a fixed view set**: "The V&B approach is free from the confines of a fixed set of views, and the architect is free to choose exactly those views which are appropriate for the system." The procedure is stakeholder-based, "using stakeholders (or stakeholder proxies) to determine the uses to which the documentation will be put." (Chapter 9 of *Documenting Software Architectures* is titled "**Choosing the Views**.")

**The Seven Rules for Sound Documentation** — the single most transferable artifact on this axis. Verbatim, with SEI's own explanations (TN-037 §1.2, pp.2–3; expanded in the [InformIT book excerpt](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5)):

1. **Write from the reader's point of view.** "A document is read only if it meets the needs of, and is usable by, its intended audience. Material written in streams of consciousness or using arcane terminology is unlikely to meet the reader's needs and thus is **unlikely to be read or consulted often**." The book adds: documentation should be easy to *use*, not merely easy to *write*.
2. **Avoid unnecessary repetition.** "Each kind of information should be recorded in **exactly one place**." "Repetition is the root of inconsistency… attempts to avoid these inconsistencies are costly." **Important qualifier:** "if avoiding repetition creates excessive navigation burden for readers, **selective repetition across locations is acceptable**, especially in online documents using hyperlinks." — i.e. SEI explicitly permits redundancy when de-duplication has made the doc unreadable. *This directly licenses reducing cross-reference density.*
3. **Avoid ambiguity.** "It is **far better to be explicit and wrong than to be vague**." Sub-rule **3a: Explain your notation** — every diagram needs a key; for informal notations define all symbology including colors, shapes, and positional significance; arrows in particular must be disambiguated (calls? data flow? instantiation? messaging?).
4. **Use a standard organization.** "Usually a document is not read more than once, if that. Yet, if it is successful, **readers will refer to it numerous times**." So: **organize for reference, not cover-to-cover reading**; provide TOC, index, glossary, acronym list; and **never leave a section blank** — mark it "NA" or "TBD" with an explanation.
5. **Record rationale.** "The reasoning behind the decisions is just as important as the decisions themselves… the reasoning behind a decision may be **forgotten in as little as a few weeks**." Capture rejected alternatives and why. Priority targets: decisions critical to quality requirements, decisions that required stakeholder meetings, decisions backed by experiments/prototypes.
6. **Keep documentation current but not too current.** "Documentation that is incomplete or out of date does not reflect truth, does not obey its own rules for form and internal consistency, and **is not used**." But: don't publish decisions still under reconsideration — "Including information that might not be final does not help them." Define a **documentation release plan**; version-control docs like code; where updates aren't feasible, **mark the outdated sections** so readers retain confidence in the rest.
7. **Review documentation for fitness of purpose.** "**Only the intended users of a document will be able to tell you whether it contains the right information presented in the right way.**" Have target-audience representatives review before release.

**SEI's three view categories** (useful as a top-level partition): **module views** (units of implementation — responsibility, allowed-uses, actual-uses, inheritance), **component-and-connector views** (runtime components and their interaction), and **allocation views** (mapping to environment). Plus "information that applies to more than one view" — SEI's equivalent of arc42 §8 crosscutting concepts.

---

## 5. Synthesis — a layering principle, and the sourced rule for what NOT to write

### 5.1 The layering principle: each document type is defined by (audience × question × decay rate)

Every framework surveyed converges on the same move: **partition by reader-question, not by subject matter**, and let each layer's *stability* determine its size. Synthesizing arc42's routing rules (tips 8-9, 9-1, 5-28, 4-4), C4's levels, and SEI's viewtypes:

| Layer | Reader's question | Framework precedent | Content rule | How much |
|---|---|---|---|---|
| **Orientation / map** | "Where am I? What is this system and what does it touch?" | C4 Context + Container; arc42 §1, §3, §4 | Names, responsibilities one line each, external interfaces, top 3–5 quality goals, solution strategy as **keywords/table** | Smallest layer. arc42 caps quality goals at **max five** (§1); tip 4-1 says strategy "as compact as possible" |
| **Business rule registry** | "What is always true, everywhere?" | arc42 §8 Crosscutting Concepts; SEI "information that applies to more than one view" | Invariants that span multiple use cases. Exists **specifically to stop repetition** across contracts | arc42 §8: "Pick only the most-needed topics… **DO NOT ATTEMPT to cover all of the topics**" |
| **Use-case contract** | "What happens in *this* flow?" | arc42 §6 Runtime View; C4 dynamic diagram; Kruchten scenarios | One flow, schematic. **References** registry entries rather than restating them | Tip 6-2 "**only a few**"; tip 6-3 "**schematic** (instead of detailed)" |
| **ADR** | "Why is it this way, and what did we reject?" | arc42 §9; C4 minimal set item 5; SEI Rule 5 | Context, Decision, Status, Consequences (+ and −), **rejected alternatives** | Tip 9-1's 8-point relevance filter (below). "unless described elsewhere" |
| **Quality/test strategy** | "How do we know it's true?" | arc42 §10 quality tree + scenarios; Kruchten "+1" | Quality tree (mind-map) → **measurable scenarios** (usage / change / **fault-error**), each with stimulus + measurable response | Tree used "**as a checklist**"; §1.2 holds only the top 3–5, §10 holds the full tree |
| **Runbook** | "It's 3am and it's broken — what do I do?" | Simon Brown's guidebook §12 "Operation and Support"; arc42 §7 | Procedural, self-contained. This is the **one place SEI's Rule 2 is deliberately relaxed** — see below | Sized by the operator's task, not by system size |
| **Risk / debt register** | "What do we know is wrong?" | arc42 §11 | Prioritized list + mitigation. Audience is management | Ordered by priority; it's a register, not a narrative |

Two structural insights worth adopting explicitly:

**(a) Simon Brown's product-vs-project split.** For a long-lived banking system, maintain **one standing product guidebook** ("a single place where somebody can find information about how the product works and how it's evolved"), and treat every change stream as "**a small delta**" against it. Registries and crosscutting concepts are product-level; ADRs are the delta log. This prevents the 20-year accretion failure he describes.

**(b) SEI's actual remedy for "too long for a general audience" is not shortening — it's per-stakeholder views over one source.** SEI diagnosed exactly the symptom described (readers skim and miss key elements; others can't find what they need) and fixed it with role-tailored renderings of a single repository, not by deleting content. Where content genuinely serves distinct roles, **route it, don't cut it**.

### 5.2 The sourced rule for what NOT to write

Assemble it as a five-gate filter. Each gate is a direct quotation, so each is defensible:

**Gate 1 — No identified stakeholder, no document.**
> "the architect creates a **table of stakeholders versus views** in which each stakeholder's needs are recorded. **Each view comes with a cost, and each view comes with a benefit.** Available resources must be weighed against stakeholders' needs." — [SEI CMU/SEI-2004-TN-037, §1.3](https://www.sei.cmu.edu/documents/2057/2004_004_001_14351.pdf)

Reinforced by ISO 42010's conformance chain (every concern framed by ≥1 viewpoint — and by implication, no viewpoint without a concern), Kruchten (views are per-audience and droppable), and Ambler ("Agile documents **have a specific customer**"). **Operationalize:** build the stakeholder × concern matrix for the ~50 docs first; documents that populate no cell are candidates for deletion, not rewriting.

**Gate 2 — If the code or tests already say it, don't say it again; say *why* instead.**
> "**Focus on explanation and rationale, not only facts**" — because "**source code contains facts**." — [arc42 FAQ E-7](https://faq.arc42.org/questions/E-7/)

> `if (extensive-explanation-required) then concept else decision` — and a decision can simply **reference source code or unit tests**. — [arc42 tip 8-9](https://docs.arc42.org/tips/8-9/)

> "**Do resist the temptation to go into too much technical detail** because **the technical people that will understand that level of detail will know how to find it in the codebase anyway.**" — [Simon Brown, *SA4D*](https://static.codingthearchitecture.com/sddconf2014-software-architecture-for-developers-extract.pdf)

> "**No, particularly for long-lived documentation**, because most IDEs can generate this level of detail on demand." — [c4model.com, on Code diagrams](https://c4model.com/diagrams/code)

> "The majority of the information captured in traditional specification documents… can be captured as **executable specifications in the form of tests**." — [Agile Modeling](https://agilemodeling.com/essays/agiledocumentationbestpractices.htm)

**Operationalize:** for dense verification tables — if a machine can check it, the machine is the artifact; the document keeps only the *rationale* and a pointer. This is the direct precedent for de-densifying machine-oriented tables.

**Gate 3 — Relevance beats completeness; document the surprising, not the routine.**
> "**Focus on important, interesting, special or risky topics, instead of striving for completeness.**" — [arc42 FAQ E-3](https://faq.arc42.org/questions/E-3/)

> "**prefer relevance over completeness**… specify important, surprising, risky, complex or volatile building blocks. **Leave out normal, simple, boring or standardized parts.**" — [arc42 §5](https://docs.arc42.org/section-5/)

> Document a decision if it is critical, quality-affecting, **unconventional / off the beaten track**, risky/expensive, long-lasting, affects many or important stakeholders, took substantial effort to decide, or is **astonishing or surprising**. — [arc42 tip 9-1](https://docs.arc42.org/tips/9-1/)

> "you don't need to use all 4 levels of diagram; **only those that add value**." — [c4model.com/diagrams](https://c4model.com/diagrams)

**Operationalize:** tip 9-1's eight predicates are a ready-made intake checklist for the ADR set. A banking rule that is standard practice needs a registry line; a banking rule that is *surprising* needs a paragraph of rationale.

**Gate 4 — Excessive cross-referencing is an explicitly sanctioned exception to single-sourcing.**

Single-sourcing is the default: "Each kind of information should be recorded in **exactly one place**" (SEI Rule 2); "**Strive to capture information in one place and one place only**" (Ambler). *But* SEI itself carves out the exception:

> "if avoiding repetition creates **excessive navigation burden for readers**, **selective repetition across locations is acceptable**." — [SEI Rule 2](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5)

This is the single most directly applicable finding for the stated diagnosis. The correct formulation is a **two-sided** rule, not "always link":
- **Normative content** (a business rule's definition) → exactly one place; everything else links. Repetition here "is the root of inconsistency."
- **Orienting content** (what the rule means, enough to read the current page) → repeat inline. Forcing a reader to chase a reference to understand the sentence in front of them is the failure SEI names.
- **Runbooks are the strongest case for repetition** — an operator at 3am must not follow cross-references. Combine SEI Rule 1 (reader's point of view) with the Rule 2 exception: runbooks should be self-contained even at the cost of duplication.

**Gate 5 — Stop when the next sentence costs more than it returns; and prefer late over speculative.**
> "The point of maximal value is where **the incremental cost of adding more to the artifact exceeds the incremental value being added**"; beyond it, effort "**removes net value**." — [Agile Modeling, JBGE](https://agilemodeling.com/essays/barelygoodenough.htm)

> "By waiting to document information **once it has stabilized** you reduce both the cost and the risk." — [Agile Modeling](https://agilemodeling.com/essays/agiledocumentationbestpractices.htm)

> "Including information that **might not be final** does not help them." — [SEI Rule 6](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5)

With the essential counterweight, so this isn't read as license to defer indefinitely:
> "In theory, yes. In practice such a deferral means that this documentation will (quite likely) **never ever be created**." — [arc42 FAQ E-6](https://faq.arc42.org/questions/E-6/)

### 5.3 Two acceptance tests to build into the methodology

Both are sourced, cheap, and directly counter the "optimized for machine verification" diagnosis:

**The reader-comprehension review** (not an author-compliance review). C4's [diagram checklist](https://c4model.com/diagrams/checklist) is phrased entirely as "**Do you understand…**" — every element's type, purpose, technology; every arrow's intent and direction; every colour, shape, icon, line style. SEI Rule 7 generalizes it: "**Only the intended users of a document will be able to tell you whether it contains the right information presented in the right way**" — have target-audience representatives review before release. Combined with SEI Rule 1 ("easy to *use*, not just easy to write") this gives a defensible review protocol: a representative of each identified stakeholder role reads their document cold and reports what they could not answer.

**The maintenance test as a value proxy.** "If you've chosen to keep your [artifact] up to date… **that is a good sign that these are valuable**" — [Agile Modeling](https://agilemodeling.com/essays/agiledocumentationbestpractices.htm). Run this retrospectively over the ~50 docs: which have actually been updated? Unmaintained documents are evidence of absent demand, and are Gate-1 deletion candidates rather than rewrite candidates. Pair with SEI Rule 6's practical fallback — where a document can't be updated now, **mark the stale sections** so readers retain confidence in the rest.

**Also worth adopting from SEI Rule 4:** "Organize documentation **for reference rather than cover-to-cover reading**," and "**never leave sections blank**; mark them 'NA' or 'TBD' with explanations." A rewrite that shortens documents but leaves the reader unable to *navigate* to an answer has not fixed the problem.

---

### Note on source quality
All claims above are from primary sources (arc42.org, faq.arc42.org, docs.arc42.org, c4model.com, agilemodeling.com, agilemanifesto.org, sei.cmu.edu, iso-architecture.org, Kruchten's original IEEE Software paper, and Simon Brown's own book extract / his own dev.to post). No blog or HN opinion is load-bearing in this report, so no [실무 의견] tags were required. Two caveats flagged inline: the "78% of developers struggle with outdated documentation" figure could **not** be traced to a primary study — do not cite it; and the SEI "Choosing the Views" three-step method (build stakeholder/view table → combine views → prioritize and stage) is referenced in secondary literature as Chapter 9 of *Documenting Software Architectures*, but I could only verify the **stakeholder/view table + cost-benefit** step against a primary SEI document (TN-037 §1.3) — the "combine" and "prioritize and stage" steps should be verified against the book before being quoted as SEI's wording.
