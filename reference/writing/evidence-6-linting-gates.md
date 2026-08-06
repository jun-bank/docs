# [보존] 1차 R3 하위 워커 — docs-as-code·린트 게이팅·가독성 공식 비판 (완주분)

I have enough primary-source material. Here are the findings.

---

# Axis: docs-as-code practice + documentation linting

## 1. Vale — mechanics, enforceable rules, readability metrics

### 1.1 What Vale is and how gating actually works

Vale is a markup-aware prose linter (Go). Config lives in `.vale.ini`; "styles" are directories of YAML rule files. Rules do not require programming — each rule declares an `extends:` extension point plus parameters ([docs.vale.sh/topics/styles](https://docs.vale.sh/topics/styles)).

**The gating mechanic is the alert level, and this is the single most important fact for your purpose** ([docs.vale.sh/keys/minalertlevel](https://docs.vale.sh/keys/minalertlevel)):

| Level | Exit code | CI effect |
|---|---|---|
| `suggestion` (default) | 0 | never fails a build |
| `warning` | 0 | never fails a build |
| `error` | non-zero | **fails the build** |

So "enforced gate" in Vale = *assign a rule `level: error`*. Everything else is advisory-by-construction. Per-rule override in `.vale.ini` (`Vale.Spelling = warning`), global floor via `MinAlertLevel`, CLI override via `--minAlertLevel=warning`. This lets you run one config strictly in CI and loosely in the editor.

Escape hatch (as documented by GitLab): `<!-- vale off -->` / `<!-- vale on -->`, or per-rule `<!-- vale gitlab_base.RuleName = NO -->` ([docs.gitlab.com/development/documentation/testing/vale/](https://docs.gitlab.com/development/documentation/testing/vale/)).

### 1.2 The extension points — confirmed list (11)

Confirmed from Vale's own docs corpus ([docs.vale.sh/llms-full.txt](https://docs.vale.sh/llms-full.txt), corroborated by [docs.vale.sh/topics/styles](https://docs.vale.sh/topics/styles)). Note: your brief listed these 11 and that matches the primary source; one third-party page claims "twelve" — the docs say 11.

| Extension point | What it checks |
|---|---|
| `existence` | presence of a regex pattern |
| `substitution` | replace pattern X with preferred string Y (supports auto-fix) |
| `occurrence` | pattern must occur N times within a scope (min/max) |
| `repetition` | pattern must not repeat |
| `consistency` | either of a pair may be used, but only one, consistently |
| `conditional` | pattern A required if pattern B present |
| `capitalization` | enforce a capitalization scheme in a scope |
| `metric` | **arbitrary formula over document statistics + threshold** |
| `spelling` | Hunspell dictionaries + custom vocabularies |
| `sequence` | ordered pattern matching, with **part-of-speech tagging** |
| `script` | arbitrary Tengo script over the content |

`conditional`, `consistency`, `occurrence`, and `script` are the four that matter most for a spec/registry corpus — they can express *structural* invariants, not just word choice.

### 1.3 Packaged styles — actual rule names

Pulled directly from the errata-ai style repos.

**Google (36 rules)** — [github.com/errata-ai/Google](https://github.com/errata-ai/Google/tree/master/Google):
`AMPM, Acronyms, Anthropomorphism, Colons, Contractions, DateFormat, Ellipses, EmDash, ExcessiveClaims, Exclamation, FirstPerson, Gender, GenderBias, HeadingPunctuation, Headings, Jargon, Latin, LyHyphens, OptionalPlurals, Ordinal, OxfordComma, Parens, Passive, Periods, Quotes, Ranges, Semicolons, Slang, Spacing, Spelling, Timeless, Units, We, Will, WordList, WordListCase`

**Microsoft (47 rules)** — [github.com/errata-ai/Microsoft](https://github.com/errata-ai/Microsoft/tree/master/Microsoft):
`AMPM, Accessibility, Acronyms, Adverbs, Auto, Avoid, BiasFree, Contractions, Dashes, DateFormat, DateNumbers, DateOrder, Ellipses, ExclamationPoints, FirstPerson, Foreign, Gender, GenderBias, GeneralURL, HeadingAcronyms, HeadingColons, HeadingPunctuation, Headings, Hyphens, Jargon, Militaristic, Negative, Ordinal, OxfordComma, Passive, Percentages, Plurals, QuestionMarks, Quotes, RangeTime, Semicolon, SentenceLength, Spacing, Suspended, Terms, UIVerbs, URLFormat, Units, Uppercase, Vocab, We, Wordiness`

**write-good (8)** — `Cliches, E-Prime, Illusions, Passive, So, ThereIs, TooWordy, Weasel`
**proselint (34)** — `Airlinese, AnimalLabels, Annotations, Apologizing, Archaisms, But, Cliches, CorporateSpeak, Currency, Cursing, DateCase, DateMidnight, DateRedundancy, DateSpacing, DenizenLabels, Diacritical, GenderBias, GroupTerms, Hedging, Hyperbole, Jargon, LGBTOffensive, LGBTTerms, Malapropisms, Needless, Nonwords, Oxymorons, P-Value, RASSyndrome, Skunked, Spelling, Typography, Uncomparables, Very`
**alex (11)** — `Ablist, Condescending, Gendered, LGBTQ, OCD, Press, ProfanityLikely, ProfanityMaybe, ProfanityUnlikely, Race, Suicide`
**Joblint (17)** — `Acronyms, Benefits, Bro, Competitive, Derogatory, DevEnv, DumbTitles, Gendered, Hair, LegacyTech, Meritocracy, Profanity, Reassure, Sexualised, Starter, TechTerms, Visionary` (job postings — irrelevant to you, listed for completeness)

### 1.4 Four rules quoted verbatim — so you can see the enforcement grain

`Microsoft.SentenceLength` ([source](https://raw.githubusercontent.com/errata-ai/Microsoft/master/Microsoft/SentenceLength.yml)):
```yaml
extends: occurrence
message: "Try to keep sentences short (< 30 words)."
scope: sentence
level: suggestion
max: 30
token: \b(\w+)\b
```

`Google.Headings` ([source](https://raw.githubusercontent.com/errata-ai/Google/master/Google/Headings.yml)) — note it ships an explicit exceptions list, i.e. **every capitalization rule needs a domain vocabulary or it drowns you in false positives**:
```yaml
extends: capitalization
message: "'%s' should use sentence-style capitalization."
level: warning
scope: heading
match: $sentence
exceptions: [Azure, CLI, Cosmos, Docker, Emmet, gRPC, I, Kubernetes, Linux,
             macOS, Marketplace, MongoDB, REPL, Studio, TypeScript, URLs,
             Visual, VS, Windows, JSON]
```

`Google.Passive` ([source](https://raw.githubusercontent.com/errata-ai/Google/master/Google/Passive.yml)) — regex + a long hand-written irregular-participle list. Ships at `suggestion`:
```yaml
extends: existence
message: "In general, use active voice instead of passive voice ('%s')."
level: suggestion
raw:
  - \b(am|are|were|being|is|been|was|be)\b\s*
tokens: ['[\w]+ed', awoken, beat, become, been, begun, bent, ...]
```

`Microsoft.Wordiness` ([source](https://raw.githubusercontent.com/errata-ai/Microsoft/master/Microsoft/Wordiness.yml)) — a `substitution` map with **auto-fix** (`action: name: replace`):
```yaml
extends: substitution
level: suggestion
action:
  name: replace
swap:
  "(?:in order to|as a means to)": to
  "(?:utilize|make use of)": use
  "(?:previous|prior) to": before
  "a (?:large)? number of": many
  ...
```

### 1.5 The `metric` extension point — Vale's readability capability

Vale can compute *any* formula over document-level counters ([docs.vale.sh/checks/metric](https://docs.vale.sh/checks/metric)).

**Available variables (16):**
- Text composition: `words`, `sentences`, `syllables`, `characters`, `paragraphs`
- Word complexity: `complex_words` (polysyllabic minus common suffixes), `polysyllabic_words` (3+ syllables), `long_words` (7+ chars)
- Structure: `blockquote`, `list`, `pre`, `heading.h1` … `heading.h6`
- Math: `math.sqrt(x)`, `math.abs(x)`

**All calculations are document-scope** — metric rules are inherently whole-file summary checks, not line-level. Condition syntax is `'> 8.0'` (docs warn: always use float syntax).

The official readability package is **[errata-ai/readability](https://github.com/errata-ai/readability)**, shipping 7 rules: `AutomatedReadability.yml, ColemanLiau.yml, FleschKincaid.yml, FleschReadingEase.yml, GunningFog.yml, LIX.yml, SMOG.yml`.

Two verbatim:
```yaml
# FleschKincaid.yml
extends: metric
message: "Try to keep the Flesch–Kincaid grade level (%s) below 8."
formula: |
  (0.39 * (words / sentences)) + (11.8 * (syllables / words)) - 15.59
condition: "> 8"
```
```yaml
# GunningFog.yml
extends: metric
message: "Try to keep the Gunning-Fog index (%s) below 10."
formula: |
  0.4 * ((words / sentences) + 100 * (complex_words / words))
condition: "> 10"
```

**How teams set thresholds:** by editing `condition:` directly. The shipped defaults are FK < 8 and Gunning Fog < 10.

Two important observations:
- Neither shipped rule declares a `level:`, so they inherit Vale's default (`suggestion`) — **the readability rules do not fail CI as shipped**; you would have to deliberately promote them to `error` in `.vale.ini`. *(Config detail — worth a smoke test before relying on it. `[구현 검증]`)*
- The `list`, `pre`, and `heading.h*` variables **exist but are unused by the shipped formulas**. That is precisely the gap Redish identifies (§4): Vale can count your tables/lists/code blocks but Flesch-Kincaid throws that information away.

---

## 2. Other doc linters worth naming

| Tool | Type | Concrete rules | Notes |
|---|---|---|---|
| **markdownlint** ([Rules.md](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)) | structural | `MD001` heading increment · `MD003` heading style · `MD013` line length · `MD022` blanks around headings · `MD024` duplicate headings · `MD025` multiple H1 · `MD026` trailing punctuation in heading · `MD029` ordered-list prefix · `MD032` lists surrounded by blank lines · `MD041` first line is H1 · **`MD043` required heading structure** · `MD055` table pipe style · `MD056` table column count · `MD058` blanks around tables · `MD060` table column style | ~140 rules. `MD043` is the highest-value one for you — it enforces a *document template*. |
| **textlint** ([repo](https://github.com/textlint/textlint), [rule collection](https://github.com/textlint/textlint/wiki/collection-of-textlint-rule)) | pluggable prose | no bundled rules; all via npm. `textlint-rule-sentence-length`, `textlint-rule-no-start-duplicated-conjunction`, `textlint-rule-write-good`, `textlint-rule-alex`, spellcheckers | Wraps write-good/alex as plugins. Netlify uses it. |
| **write-good** ([checks](https://github.com/btford/write-good#checks)) | prose heuristics | `passive`, `illusion` (repeated word), `so` (sentence-initial), `thereIs`, `weasel`, `adverb`, `tooWordy`, `cliches`, `eprime` (off by default) | Self-described "naive linter". |
| **alex** | inclusive language | gendered / ableist / racial / polarising phrasing | Available as a Vale style and a textlint rule. |
| **proselint** | prose | 34 checks (see §1.3) | Mostly literary-register; low yield on specs. |
| **LanguageTool** | grammar/spelling engine | self-hostable grammar server, thousands of pattern rules | Heavier and slower than Vale; not designed for CI gating. |
| **Acrolinx** (commercial) | composite scoring | score 1–100 across clarity, consistency, tone, brand, terms, spelling, grammar, **readability**, inclusive language ([Acrolinx score](https://support.acrolinx.com/hc/en-us/articles/204251822-Configuring-How-Acrolinx-Scores-Are-Calculated)) | This is the only mainstream tool that gates on a *number*, and Microsoft does it (§3). |
| **Lychee** | link integrity | dead links | GitLab runs it alongside Vale. Relevant to a heavily cross-referenced doc set. |

Research note: an academic comparison of 13 doc linters (markdownlint, Vale, textlint, proselint, alex, write-good, standard-readme, awesome-lint, Grammarly, …) across 26 quality dimensions exists in *Linting Style and Substance in READMEs* ([arXiv 2603.00331](https://arxiv.org/html/2603.00331v1)). Its finding relevant to you: no single quality measure captures every domain's needs, and formula/pattern approaches cannot reach "substance" questions like *is this appropriate for the intended audience*.

---

## 3. Real gating practice in industry

### GitLab — the most transferable model, and it is explicitly tiered

GitLab runs markdownlint, Vale, Lychee, mermaidlint, rubocop and eslint over docs in the build pipeline ([Documentation testing](https://docs.gitlab.com/development/documentation/testing/)). Their Vale policy assigns meaning to each level ([Vale testing page](https://docs.gitlab.com/development/documentation/testing/vale/)):

- **error** — "For branding guidelines, trademark guidelines, and anything that causes content on the documentation site to render incorrectly." Blocks the pipeline. Also the only level the local Git hook reports.
- **warning** — "general style guide rules, tenets, and best practices." Shown in the MR diff via Code Quality; does not fail CI.
- **suggestion** — "technical writing style preferences that may require refactoring." Editor-only; never in CI or diffs.

Two policies worth copying wholesale:

1. **Promotion ladder.** "If you add an error-level Vale rule, you must fix the existing occurrences of the issue in the documentation before you can add the rule. If there are too many issues to fix in a single merge request, add the rule at a warning level. Then, fix the existing issues in follow-up merge requests. When the issues are fixed, promote the rule to an error."
2. **The human review is deliberately non-blocking.** "Technical writers provide non-blocking reviews of all documentation changes, before or after the change is merged." ([Workflow](https://docs.gitlab.com/development/documentation/workflow/)) — i.e. GitLab blocks on *mechanical* checks and explicitly refuses to block on *editorial* judgment.

### Microsoft — the one clear case of a numeric merge gate

`MicrosoftDocs/microsoft-365-docs/.acrolinx-config.edn` ([source](https://github.com/MicrosoftDocs/microsoft-365-docs/blob/public/.acrolinx-config.edn)) sets a **minimum Acrolinx quality score of 80 required for merging**, scoped to `main` and `release-*` branches and the `microsoft-365/` and `copilot/` folders, with a changed-files cap of 60. It ships a documented **exception process**: add "Sign off" + "Acrolinx exception" labels → PubOps Team reviews, may fix directly, escalate, or approve the exception with GitHub Admin support. The template also carries an override that beats the score: "You should fix all spelling errors regardless of your total score."

Two things to note: the gate is a **composite** score (terminology, spelling/grammar, clarity, style), not a raw grade level; and it comes bundled with an explicit, staffed appeal path. A numeric gate without an appeal path is not what Microsoft actually does.

### Red Hat — configurable, and explicitly hands authority to the human

[Vale at Red Hat](https://redhat-documentation.github.io/vale-at-red-hat/user-guide.html) ships the RedHat style (`Spelling, PassiveVoice, CaseSensitiveTerms, Definitions, Usage, TermsSuggestions, Slash, Spacing, ConfigMap, Annotations`) with three levels: error = "Fix the language error"; warning = "Consider fixing"; suggestion = "Heads up! Verify the usage depending on the context. Content containing suggestions is fine." GitHub Actions supports `fail_on_error: true` to "block the merging of pull requests if the report has errors", but enforcement is **per-project opt-in**, and the guide states the principle plainly: **"You are in charge: review the report and decide what is useful to you."**

### Datadog — annotations, not gates; and a documented false-positive story

[Datadog engineering blog](https://www.datadoghq.com/blog/engineering/how-we-use-vale-to-improve-our-documentation-editing-process/): open-source `datadog-vale` with `words.yml` (flags "easily", "simply"), `oxfordcomma.yml`, `abbreviations.yml` (e.g. → for example), plus per-product vocabularies. GitHub Action surfaces issues in the **Files Changed** tab. The post does not claim merge blocking. It does report the classic failure mode: **"Vale rules were alerting on content in image shortcodes, which we expected the linter to ignore"** — requiring regex exclusion tuning. Second lesson: consuming Vale styles from a separate repo in the Action "turned out to be a bit challenging."

### Spectro Cloud — the cleanest statement of the division of labour

[Blog](https://www.spectrocloud.com/blog/how-we-use-vale-to-enforce-better-writing-in-docs-and-beyond): two layered styles (strict docs-team style + looser org-wide style consumed by other teams via GitHub packages), `MinAlertLevel = suggestion`, runs on all doc-touching PRs, **flags but does not auto-block merges**. Their framing:

> "Vale does not replace the need for an editorial review, but it does catch mistakes and helps the reviewer validate the text."

### PostHog — layered styles, and an explicit stance on LLMs

[PostHog handbook](https://posthog.com/handbook/docs-and-wizard/vale): three layers — `PostHogBase` (all markdown: American English, product names, en dashes, Oxford commas, spelling, inclusivity), `PostHogDocs` (definition-list formatting, direct address, UI styling), `PostHogEditorial` (bullet spacing, word choice, hedging). Philosophy: *"Use Vale to detect issues, then use LLMs to help fix them"* — LLMs are "not reliable linters" compared to deterministic tools. Human reviewers keep final authority.

### Netlify — a case that *does* fail the pipeline

[Netlify blog](https://www.netlify.com/blog/a-key-to-high-quality-documentation-docs-linting-in-ci-cd/): textlint enforcing terminology casing consistency; "if the linter detects any violations, the task would fail and stop the pipeline so that flawed documentation isn't published to users." Note *what* they gate on — a fully deterministic terminology rule, not a style judgment. They frame linting as complementary: it "can complement human proofreading."

### Dachary Carey (MongoDB docs) — the only readability-scoring-in-CI case I found, and she chose not to gate

[Post](https://dacharycarey.com/2023/03/10/docs-readability-scoring/): built a pipeline of `docdoctor` (TS CLI) → `restructured` (RST parser) → `textstat` (Python) computing **Flesch-Kincaid Grade Level and Flesch Reading Ease** per PR. Two findings that bear directly on your decision: markup interference — **"a fair amount of markup skews the readability scores"**, requiring markup stripping and punctuation re-insertion before scoring; and the deliberate design choice not to block — the goal was that *"providing docs writers feedback about readability on every PR makes readability visible."* Behaviour change through visibility, not enforcement.

### Docs-as-code canonical references

- [Write the Docs — Docs as Code](https://www.writethedocs.org/guide/docs-as-code/): "Documentation as Code refers to a philosophy that you should be writing documentation with the same tools as code." Five components: **Issue Trackers, Version Control (Git), Plain Text Markup, Code Reviews, Automated Tests.** Notes teams "can block merging of new features if they don't include documentation."
- **Anne Gentle, *Docs Like Code*** — the canonical book for the practice.
- [Google Markdown style guide](https://github.com/google/styleguide/blob/gh-pages/docguide/style.md) — "minimum viable documentation": *"A small set of fresh and accurate docs is better than a sprawling, loose assembly."* Concrete rules: single H1, ATX headings, unique fully-descriptive heading names, 4-space nested list indent, lazy numbering, 80-char lines. And directly relevant to your table problem: **use tables only when you have "relatively uniform data distribution across two dimensions" and "many parallel items with distinct attributes"; otherwise "Lists…sometimes suffice to present the same information."** Its review philosophy explicitly favours low friction: reviewers should "LGTM immediately and trust that comments will be fixed appropriately."

### [실무 의견] Practitioner sentiment (HN, "Vale.sh – A Linter for Prose", [item 37371426](https://news.ycombinator.com/item?id=37371426))

Benefits cited: consistency enforcement across teams; custom rules for recurring domain-specific mistakes ("I work on a number of API and programming language standards… Being able to write rules for common mistakes with these has helped me many times").

Complaints, and they cluster:
- **Alert flooding on adoption** — users report receiving "hundreds of automated comments in a single PR" when switching on a full packaged style.
- **Activation energy** — a technical writer: "it's a big lift… vale doesn't make this super easy… there's an activation energy that I haven't been able to get over yet."
- **Strong opposition to blocking on style:** *"never block a docs contribution on a prose style rule violation that has no functional effect on the content."*

Also from Vale-community write-ups: "Written text is complicated, and Vale will find false positives, with no sure-fire ways of deciding when a rule should be a suggestion, warning, or an error" ([tw-docs.com](https://tw-docs.com/docs/vale/vale-styleguides/)).

---

## 4. Critique of readability formulas for technical docs

This section is the strongest evidence in the whole axis, and it points one direction. The definitive source is **Janice (Ginny) Redish, "Readability formulas have even more limitations than Klare discusses," *ACM Journal of Computer Documentation* 24(1), Aug 2000, 132–137** ([full text PDF](https://redish.net/wp-content/uploads/Redish_on_Readability_Formulas.pdf); [ACM DL](https://dl.acm.org/doi/10.1145/344599.344637)). I read the full 8-page paper. Her arguments, in her words:

**(a) Formulas are correlations, not diagnoses.** "A readability formula is a mathematical equation that is meant to *predict* the level of reading ability needed to understand a particular piece of prose… They say nothing about the *causes* of any problems people might have in understanding a document… Readability formulas give you no help in finding or fixing problems."

**(b) They were built for children's schoolbooks and are decades stale.** "The research on grade-level readability formulas is more than 50 years old… The formulas are out of date." And on transfer to adults: "The two audiences (children in school at grade level and adults with a low reading level) are so different that the same readability formula cannot possibly be adequate for both. But readability formulas do not distinguish audiences. Usability testing does."

**(c) The underlying validity bar is shockingly low.** Citing Duffy (1985): "the accepted correlation in the grade-level formulas is that if 50% of the children at a given grade level got 50% of the questions on a reading passage correct, that passage was considered acceptable at that grade level. Should we be happy if 50% of our readers understand 50% of our documents?"

**(d) Flesch specifically was never validated on technical material.** "Flesch based his scale on articles in popular magazines not on technical material. Moreover, he created the formula by correlations with older comprehension tests and other formulas, not by redoing the research with adult readers."

**(e) They measure only what is countable.** "in constructing the formulas, developers invariably dismiss all the features that cannot be easily counted even though they know that these features influence the readability (usability) of a document… 'the features included in the published formulas are usually chosen as much for how easy they are to count as for their predictive value.'"

**(f) The list of things formulas totally ignore — this list *is* your diagnosis.** Redish enumerates what readability formulas cannot see:
- Is the content right for the audience?
- Is the document organized so that users can find what they need?
- Are there any headings? Are the headings meaningful and useful to the audience?
- Is there a table of contents? Is it useful?
- Is there an index? Does it have users' words in it?
- Does the page layout help users find what they need?
- Are there visuals (tables, charts, screen shots, lists) to help users?
- Is the text divided into short sections and paragraphs (chunks) so that users are invited to use them?
- Are the sentences grammatical?
- Are the words ones that these users know?

"Given this long list, it is difficult to see why anyone would want to limit the definition of a 'readable' document to 'short sentences' and 'simple words,' the features counted by readability formulas."

**(g) They break outright on tables and lists — decisive for your doc set.** "Readability formulas assume that you are writing prose paragraphs. They count sentence length by going from period to period. If you use bulleted lists to chunk your material and lay your text out with white space, readability formulas will say you have long sentences. Yet usability studies have consistently shown the value of lists and white space as aids to locating and understanding information."

**(h) They are unreliable.** "the same passage may come out at very different grade levels on different formulas," and the score varies passage to passage within one document.

**(i) Improving the score does not improve comprehension — and can invert it.** Klare (1976) reviewed 36 studies attempting to improve comprehension via readability scores: "Only about half succeeded and to improve comprehension they had to change the readability scores by an average of 6.5 grade levels." Worse, Charrow & Charrow (1979) on jury instructions: "Comprehension went up. But… In many cases, their revisions got better comprehension scores but *worse* readability scores. (This happened primarily because they added words to show the relationships among the information items in the instructions.)" — i.e. **the connective tissue that makes a spec followable is exactly what the formula penalizes.**

**(j) Short sentences are not automatically easier.** Flesch Reading Ease scores "I wave my hand" and "I waive my rights" identically. And: "He is the defendant. He is fifteen years old. He is in his teens. Someone says he stole from the store." vs "The defendant is a fifteen-year old teenager who is accused of shoplifting." — "The second, longer sentence is actually easier to understand, although it has the poorer readability score."

**(k) Goodhart's law, stated explicitly, plus a warning against exactly the tool you're contemplating.** "Rewriting to get a better score is misusing the formula… Klare explained it best when he suggested that expecting comprehension to improve by writing to a readability formula is like lighting a match under a thermometer to warm up a room. The temperature on a thermometer is an index of how warm the room is. Lighting a match under the thermometer will make the index value go up, but the room won't get any warmer."

And, near-verbatim about automated enforcement: **"The temptation may be especially great when each draft can be quickly measured right in the word processor and when the writer is required to achieve a particular grade level or readability score."**

**(l) The one legitimate use she concedes.** "If you do use a readability formula and your document gets a very poor score, that probably indicates that people will have problems with it… The poor score is a red flag… But the poor score doesn't tell you what else is wrong with the document… nor does it give you any hints on how to fix it." Conversely: "A good score does not mean you have a usable or useful document."

**(m) What to do instead.** "readability formulas are a simplistic answer to a very complex problem." Her recommended replacement is usability testing with representative readers.

### Corroborating sources

- **ISO plain language standard (ISO 24495-1:2023)**, endorsed by a 25-country expert group, per the Government of Canada Language Portal ([Our Languages blog](https://our-languages.canada.ca/en/blogue-blog/readability-formulas-eng)): **"Plain language focuses on how successfully readers can use the document rather than on mechanical measures such as readability formulas."** The article notes no formulas are mentioned anywhere else in the standard.
- Same source, citing **Kern (1980)**: formulas "cannot match material to readers at targeted grade levels"; "Rewriting to lower the reading-grade level score does not increase comprehension"; and they distract from "organizing the material to meet the reader's information needs."
- **Formula disagreement on domain vocabulary**: a passage with short sentences but polysyllabic jargon scores well on Flesch-Kincaid (sentence-length weighted) and badly on Dale-Chall (word-list based). Flesch-Kincaid treats "tort" as a simple word and "hippopotamus" as a difficult one ([ckmtools readability formula comparison](https://ckmtools.dev/blog/readability-formula-guide)). For a banking corpus — 원장/정산/멱등성, idempotency key, settlement netting, reconciliation — Gunning Fog's `complex_words` is *defined as* 3+ syllable words, so your correct domain terms are the metric's failure condition.
- Practitioner-side agreement [실무 의견]: technical-writing blogs note that "in specific professional fields, there can be a plethora of words no readability score will find appropriate, causing technical documentation for such fields to not pass the test," and that above ~75 Flesch Reading Ease "you may be losing precision, which matters in technical writing where exact phrasing carries meaning" ([ClickHelp](https://clickhelp.com/clickhelp-technical-writing-blog/readability-score-pros-and-cons/), [Docsie](https://www.docsie.io/blog/glossary/readability-score/)).
- W3C has an open issue on its own references to Flesch Reading Ease / Flesch-Kincaid in WCAG 2.2 Understanding docs ([w3c/wcag#4022](https://github.com/w3c/wcag/issues/4022)) — i.e. even the accessibility standards body treats these formulas as contested.

**Conclusion for the methodology: do not make a readability formula a merge gate.** Every failure mode Redish names is amplified by your corpus — tables and cross-reference lists destroy sentence segmentation, mandatory domain terms are counted as defects, and the connectives that make a business rule followable raise the score. The formula would reward exactly the fragmentation you are trying to fix.

---

## 5. Synthesis for a ~50-document banking design corpus

### 5.1 Mechanically enforceable — safe to run at `error` (blocks merge)

These share one property: **a machine can be wrong about them only if the rule is written wrong, never because the machine misjudged intent.**

| Check | Tool / extension point | Why it's a readability gate, not a pedantry gate |
|---|---|---|
| **Document template conformance** — ADR must carry Context / Decision / Consequences; use-case contract must carry Preconditions / Main flow / Postconditions / Invariants; runbook must carry Symptom / Diagnosis / Action / Rollback | **markdownlint `MD043`** (required heading structure), one config per doc type | Highest-value gate available. Readers navigate by structure; a predictable skeleton is what makes 50 docs scannable. This is enforceable *and* is the actual fix for your diagnosis. |
| Heading hygiene — single H1, no level skipping, no duplicate headings, first line is H1 | `MD001`, `MD025`, `MD041`, `MD024`, `MD022` | Broken heading trees break the TOC and in-page navigation. |
| Table well-formedness — column count matches header, consistent pipe style, blank-line separation | `MD056`, `MD055`, `MD058`, `MD060` | Malformed tables render wrong; that is GitLab's stated `error` criterion ("causes content to render incorrectly"). |
| **Terminology single-naming** — one term per domain concept | Vale `substitution` + `Vale.Terms` + Vocabularies | The strongest domain win in a banking corpus. Same concept named three ways across a registry, a contract, and a runbook is a genuine comprehension defect. |
| **Term-pair consistency** — if both spellings are acceptable, only one per document | Vale `consistency` | Cheap, zero false positives. |
| Heading capitalization scheme | Vale `capitalization` (`scope: heading`, `match: $sentence`) **with a curated exceptions/vocabulary list** | Only safe *after* the vocabulary is populated — see Google.Headings' exceptions list. |
| Undefined acronyms on first use | `Microsoft.HeadingAcronyms`, `Google.Acronyms`, or a custom `conditional` rule | For a corpus dense with domain acronyms this is real reader relief. |
| Placeholder residue — `TBD`, `TODO`, `XXX`, `???`, `<TODO>` | Vale `existence` | Objective. |
| **Cross-reference integrity** — every referenced doc/anchor/rule ID resolves | Lychee (links) + Vale `script` (Tengo) for ID-level checks | Directly attacks "heavy cross-referencing": a reference that doesn't resolve is a dead end. |
| **Registry ↔ contract invariants** — e.g. every business rule ID appears in exactly one registry row and is cited by ≥1 use-case contract; every ADR referenced by a contract exists | Vale `script` (Tengo), or a small custom script in CI | Not prose linting at all — but it is the check that makes cross-referencing trustworthy enough to be readable. |

### 5.2 Advisory — run at `warning` (visible in the diff, never blocks)

These are heuristics with real false-positive rates on specification prose. GitLab's exact category: "general style guide rules, tenets, and best practices."

| Check | Tool | Why not a gate |
|---|---|---|
| Sentence length cap | `Microsoft.SentenceLength` (`occurrence`, max 30) | Countable, but Redish (j) — a longer sentence showing relationships can be *easier*. Also fires spuriously on table cells and list items. |
| Passive voice | `Google.Passive` / `Microsoft.Passive` | **High false-positive rate on your genre specifically.** "The transaction is rejected when the balance is insufficient" is correct spec prose — the actor is genuinely the system, and the rule is about the transaction. Also ships at `suggestion` upstream for a reason. |
| Wordiness substitutions | `Microsoft.Wordiness` (has auto-fix) | Good editorial nudge; occasionally wrong when precision demands the longer form. |
| Hedging / weasel words | `proselint.Hedging`, `write-good.Weasel` | Useful signal in a *decision* document (an ADR full of hedges is a real smell) — but human-judged. |
| Condescension ("simply", "obviously", "just", "easily") | custom `substitution` (Datadog's `words.yml`, Spectro Cloud's condescension rule) | Cheap and well-liked; still occasionally legitimate. |
| Latin abbreviations, Oxford comma, dash/quote style, double spaces | `Google.Latin`, `OxfordComma`, `EmDash`, `Spacing` | Consistency polish. Gating on these is what generates the "hundreds of comments in a single PR" complaint. |

### 5.3 Readability metrics — report, never gate

Recommended posture, following the only team that actually built this ([Carey](https://dacharycarey.com/2023/03/10/docs-readability-scoring/)) and Redish's own single concession (§4l):

- Compute FK grade and Gunning Fog per document via Vale's `metric` extension point and **surface them as a PR comment / trend dashboard**, at `suggestion` level. Visibility, not enforcement.
- Treat only a **very poor** score as a *red flag prompting a human look* — never as pass/fail, and never as a target to optimize toward.
- **Strip tables, code fences, and cross-reference lists before scoring**, or the number is noise (Carey: "a fair amount of markup skews the readability scores"; Redish (g): period-to-period counting turns bulleted lists into "long sentences").
- Never write the threshold into the acceptance criteria of a doc. That is the condition Redish singles out as most corrupting: "when the writer is required to achieve a particular grade level or readability score."

If leadership insists on a numeric gate, the only defensible precedent is **Microsoft's Acrolinx model**: a *composite* score dominated by terminology / spelling / consistency (things machines judge correctly), threshold 80, plus a **staffed exception path with labels and a review team** ([.acrolinx-config.edn](https://github.com/MicrosoftDocs/microsoft-365-docs/blob/public/.acrolinx-config.edn)). Not a raw grade level, and never without the appeal route.

### 5.4 Must stay human-judged

Redish's ignored-list (§4f) is, almost line for line, your stated diagnosis. Turn it into the review rubric — no tool covers any of these:

1. **Is the content right for this audience?** (Who reads a business rule registry — an implementer, an auditor, an ops on-call? Different answers imply different documents.)
2. **Is it organized so a reader can find what they need**, or does finding anything require traversing three cross-references?
3. **Are the headings meaningful** — not merely correctly capitalized? (A linter checks capitalization; only a human checks whether "Section 4.2.3" tells you what's inside.)
4. **Is a table the right form here?** This is the crux of your diagnosis and it is categorically unlintable. Google's own guidance gives the human heuristic: tables only for "relatively uniform data distribution across two dimensions" with "many parallel items with distinct attributes"; otherwise "Lists…sometimes suffice" ([Google docguide](https://github.com/google/styleguide/blob/gh-pages/docguide/style.md)).
5. **Is the text chunked so readers are invited to use it**, or is it a wall of rows?
6. **Can the document's core invariant be stated in one sentence a reader can hold in their head?**
7. **Is there a worked example** grounding the abstract rule?
8. **Is the cross-referencing serving the reader or offloading assembly work onto them?** — the specific pathology you diagnosed.

### 5.5 Process design — copy these four patterns

1. **Three tiers with declared semantics** (GitLab): `error` = renders wrong / brand / trademark / structural contract violated → blocks. `warning` = style guide, best practice → visible in diff, no block. `suggestion` = editor-only.
2. **Promotion ladder** (GitLab, verbatim policy): a new rule enters at `warning`; the existing backlog is cleared in follow-up MRs; only then is it promoted to `error`. This is the antidote to the "hundreds of comments in one PR" adoption failure [실무 의견, HN].
3. **A documented escape hatch** — `<!-- vale off -->`, per-rule disables, and an exception-label path for the numeric checks (Microsoft's model). A gate with no override becomes a gate people route around.
4. **Human review rubric, non-blocking, with required/optional separation.** Red Hat's peer review guide ([redhat-documentation.github.io/peer-review](https://redhat-documentation.github.io/peer-review/)) is the best public template — five categories (**Language, Style, Minimalism, Structure, Usability**), an explicit scope boundary ("Subject matter experts and QE are responsible for testing and technical accuracy" — reviewers own usability, style, clarity), a two-tier outcome (**required changes**: style violations, typos, template adherence; **optional suggestions**: wording, reorganization — writer's discretion), and concrete comment-quality guidance:
   - **Support claims** — "Use documented resources, such as style guides or Red Hat writing conventions" (i.e. cite the rule, don't assert taste)
   - **Maintain respect** — pose uncertain points as questions; use "consider" / "suggest"
   - **Stay focused** — review only changed content plus necessary context
   - **Provide alternatives** — offer a specific rewrite rather than "this doesn't make sense"
   - **Include positive feedback**

   Pair with Google's low-friction norm — "LGTM immediately and trust that comments will be fixed appropriately" — to prevent the rubric becoming a perfectionism ratchet.

### 5.6 The one-line argument to put in front of the team

Readability *can* be an enforced gate — but the enforceable part is **structure, terminology, and reference integrity**, not prose quality and not a formula. Structure is where your actual defect lives (dense tables, heavy cross-referencing, no reading path), it is mechanically checkable via `MD043` + Vale `conditional`/`consistency`/`script` + link integrity, and it is the one part of "readability" that a CI job can be right about. The formula-based part must be reported, not gated — because on a table-dense, domain-term-dense corpus, optimizing Flesch-Kincaid would actively make the docs worse (Charrow & Charrow: the revisions that raised comprehension *lowered* the score).
