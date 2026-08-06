# [보존] 1차 R3의 하위 워커 결과 — 기업 스타일 가이드·표 복잡도 상한 (완주분)

Research complete. Findings below.

---

# Axis: Corporate/community style guides — concrete rules

**Sourcing note on fidelity.** Microsoft Learn pages returned their **raw source markdown** (frontmatter + body), so Microsoft quotes below are verbatim with high confidence. Google, W3C/WAI, GOV.UK, Write the Docs, and NN/g pages were fetched as rendered HTML and summarized by the fetch layer; quoted strings are what that layer returned as quotation and I've cross-checked the load-bearing ones with a second targeted fetch. Where a number or phrase is doing real work in the argument, I flag it.

---

## 1. Google developer documentation style guide

### 1.1 Highlights page (the "top rules" page exists)

URL: https://developers.google.com/style/highlights

The page is an explicit condensed rule set. Items relevant to this rewrite:

- "Use second person: 'you' rather than 'we'."
- "Use active voice: make clear who's performing the action."
- "Put conditions before instructions, not after."
- "Use sentence case" for document titles and section headings.
- "Use numbered lists" for sequences; "Use bulleted lists" for most other lists; "Use description lists" for pairs of related pieces of data.
- "Use descriptive link text."
- "Write accessibly." / "Write for a global audience."
- "Don't pre-announce anything."

Note the highlights page has **no** entry recommending tables. The only list-shaped guidance promoted to the highlights tier is numbered / bulleted / description lists.

### 1.2 Tables — the decision rule (this is the most directly useful page)

URL: https://developers.google.com/style/tables

Google gives an explicit **arity-based selection rule**:

| Data shape | Prescribed form |
|---|---|
| Single-unit items | "Use a numbered list, lettered list, or bulleted list." |
| Paired data (term + description) | "Use a description list (or, in some contexts, a table)." |
| Three or more related pieces per item | "Use a table." |

Places explicitly **not** to use tables:

- "Don't use tables to lay out a page; use your site's standard CSS instead."
- "If you have only one column in your table, turn the table into a list."
- "Don't use tables to lay out code snippets."
- "Don't use tables to lay out long one-dimensional lists in multiple columns."
- "Avoid tables in the middle of a numbered procedure."
- Avoid single-row tables (exception: consistency in reference documentation).

Structural constraints (these are the ones that cap complexity):

- "Don't merge cells. Don't use `colspan` or `rowspan` attributes."
- "Use table headings for the first column and the first row only." — i.e. **one header row, one header column, no multi-level headers.**
- "Sort rows in a logical order, or alphabetically if there is no logical order."
- "Introduce tables with a complete sentence that describes the purpose."
- "Don't put a table in the middle of a sentence."
- Column headers: sentence case, concise, no terminal punctuation.

### 1.3 Accessibility page — the hard numeric sentence rule and the anti-table rule

URL: https://developers.google.com/style/accessibility

- **"Try to use fewer than 26 words per sentence."** — This is Google's only hard numeric sentence-length rule and it lives on the accessibility page, not the grammar pages.
- **"Don't use tables unless it's the best method to present your information. Tables are challenging for screen readers."** — This is a much stronger stance than the tables page alone, and it is the single most quotable Google rule against a table-first document.
- "Break up walls of text to aid in scannability. For example, separate paragraphs, create headings, and use lists."
- "Links should make sense when read out of context." / "Don't use *click here* or *read this document*."
- "Use a heading hierarchy." / "Don't skip levels of the heading hierarchy. For example, put an h3 element only after an h2 element." / "Don't have empty headings or headings with no associated content."
- "Left-align text for readability. Don't center or full-justify text."

### 1.4 Cross-references — the cognitive-load rule

URL: https://developers.google.com/style/cross-references

This page is the direct authority against cross-reference-heavy docs. Verified verbatim on a second fetch:

- "In general, cross-references link to nonessential information that adds to the reader's understanding."
- "When used well, cross-references help readers navigate and understand documentation. But cross-references can easily become disruptive."
- **"Each link creates a decision for the reader, adding cognitive load. Each link is also a chance for the reader to leave the page and lose their place."**
- "When you include links, choose the most relevant destination."
- Prefer in-page help over a link when you would only be: defining a term, briefly explaining a concept, or giving a couple of steps.
- "Generally, within a given page, don't provide duplicate links to the same destination." Exceptions: linking to a specific section, very long pages with distant duplicates, or genuinely separate entry points (e.g. a procedure and a troubleshooting section).
- Standard phrasing: "For more information, see …" / "For more information about …, see …" (use *about*, not *on*).

Caveat: the page has **no** dedicated "See also" section rule and **no** explicit inline-vs-end-of-section placement rule — I checked twice. Don't attribute one to Google.

### 1.5 Link text

URL: https://developers.google.com/style/link-text

- "Use short, unique, descriptive phrases that provide context for the material that you're linking to."
- "Write link text that makes sense without the surrounding text. Don't use phrases such as *this document*, *this article*, or *click here*."
- Preferred technique: "match the link text to the page title or heading that you're referencing."
- Put important words at the beginning of the link phrase.
- "If you have punctuation immediately before or after a link, put the punctuation outside of the link tags where possible."

### 1.6 Lists

URL: https://developers.google.com/style/lists

- Numbered: "A set of items where the sequence is significant, such as ordered steps, phases, or priorities."
- Bulleted: "A set of items that's not a sequence, such as a set of nonsequential options or examples."
- Description lists: "A set of terms, each with a description, definition, or explanation."
- Parallelism: "Use the same syntax/structure for all list items in a given list, if possible."
- Capitalization: "Start each list item with a capital letter, unless case is an important part of the information."
- Punctuation: end with a period **except** if the item is a single word, or the item contains no verb.
- Lead-in: "Introduce a list with a complete sentence, not a partial one that's completed by the list items."
- "Don't use a list to show only one item; a single item isn't really a list."
- Nested ordered lists use lowercase letters or lowercase Roman numerals.

### 1.7 Headings

URL: https://developers.google.com/style/headings

- "Use sentence case for all headings and titles to improve readability and navigation."
- Task-based headings: "start with a bare infinitive" verb (e.g. *Create a table*, not *Creating a table*).
- Conceptual sections: "use a noun phrase that doesn't start with an -ing verb."
- "When possible, avoid using -ing verb forms as the first word in any heading or title" — rationale given: gerunds "are inconsistently translated" and "increase character count in limited spaces."
- "Don't skip levels of the heading hierarchy."
- "Don't use empty headings. Make sure headings are followed by content."
- "Use a unique level-1 heading (h1) for each page."

### 1.8 Global audience / sentence structure

URL: https://developers.google.com/style/translation

- **"Write shorter sentences. The shorter the sentence, the easier it is to translate."**
- "Longer sentences can impair understanding, cause rendering issues on the page or product interface, lengthen translation time, and increase translation and review costs."
- "Use standard English word order. Sentences follow the subject + verb + object order."
- "Try to keep the main subject and verb as close to the beginning of the sentence as possible."
- "Use the conditional clause first" — circumstance before instruction.
- "Don't use too many modifiers" — avoid more than two nouns modifying another noun. (Directly relevant to banking-domain compound noun stacks.)
- "Clarify antecedents" — replace ambiguous pronouns with nouns.
- "Don't omit relative pronouns" — keep *that* / *which*.

### 1.9 Voice

URL: https://developers.google.com/style/voice

- "Use active voice (in which the grammatical subject of the sentence is the person or thing performing the action) instead of passive voice."
- "Make clear who's performing the action."

### 1.10 Google Technical Writing course (separate from the style guide, still Google-official)

URL: https://developers.google.com/tech-writing/one/lists-and-tables

- **"Avoid putting too much text into a table cell. If a table cell holds more than two sentences, ask yourself whether that information belongs in some other format."** — This is the closest thing to a published *cell density limit* from a major vendor, and it maps almost exactly onto the "dense tables" diagnosis.
- "Label each column with a meaningful header. Don't make readers guess what each column holds."
- "All items in a parallel list match along the following parameters: Grammar, Logical category, Capitalization, Punctuation."
- "The first item in a list establishes a pattern that readers expect to see repeated in subsequent items."
- "Consider starting all items in a numbered list with an imperative verb."
- "We recommend introducing each list and table with a sentence that tells readers what the list or table represents." (Course says terminate that sentence with a colon; note this **conflicts** with the Microsoft tables rule below, which says end it with a period, not a colon. Pick one and record the decision.)

---

## 2. Microsoft Writing Style Guide

### 2.1 Top 10 tips for Microsoft style and voice

URL: https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice (verbatim from source markdown)

1. **"Use bigger ideas, fewer words"** — "Our modern design hinges on crisp minimalism. Shorter is always better."
2. **"Write like you speak"** — "Read your text aloud. Avoid jargon and overly complex or technical language. It should sound like a friendly conversation."
3. **"Project friendliness"** — use contractions (*it's, you'll, you're, we're, let's*).
4. **"Get to the point fast"** — "Lead with what's most important. Front-load keywords for scanning. Make customer choices and next steps obvious."
5. **"Be brief"** — "Give customers just enough information to make decisions confidently. Prune every excess word."
6. **"When in doubt, don't capitalize"** — "Default to sentence-style capitalization… Don't use title-style capitalization (Like This)."
7. **"Use end punctuation in the right places"** — "Don't use a period or a colon at the end of titles, headings, subheadings, and UI titles."
8. **"Remember the last comma"** — serial/Oxford comma.
9. **"Don't be spacey"** — one space after periods; no spaces around dashes.
10. **"Revise weak writing"** — "Most of the time, start each statement with a verb. Edit out *you can* when it isn't necessary. Avoid weak phrasing like *there is*, *there are*, and *there were*."

### 2.2 Scannable content (the parent page)

URL: https://learn.microsoft.com/en-us/style-guide/scannable-content/

- "Long spans of dense text are daunting and unapproachable to readers. Write short headings, short sentences, and short paragraphs that are easy to read—and more visually appealing."
- Framed as a three-step: "1. Use short, simple words. 2. Get to the point. 3. Then stop."
- **"Short paragraphs, like this one, help to break up long passages of text. Three to seven lines is about the right length for a paragraph."** — concrete numeric paragraph limit.
- "It's also fine to have a single-line paragraph now and then."
- Navigation in long docs: break into sections; "include a table of contents with links to subheadings"; "Add *Back to top* links at the end of sections."
- Patterns: "Lead with what's most important. Place important keywords near the beginning of headings, table entries, and paragraphs so they're easy to spot."
- "Apply the same sentence structures to similar information… use the same syntax for cross-references and other common content elements."
- Content above the fold gets read; readers scan in an F shape; put the most important information upper-left.

### 2.3 Tables

URL: https://learn.microsoft.com/en-us/style-guide/scannable-content/tables (verbatim)

- Definition of a legitimate table: "In a table, data is arranged into two or more rows (plus a header row) and two or more columns."
- **"Don't use a table just to present a list of items that are similar. Use a list instead."**
- Tables are "sometimes useful for": data or values; simple instructions; categories of things with examples; "collections of things with two or more attributes."
- **"Limit the number of columns in tables and keep the text in each cell brief—ideally one line."**
- "Make entries in a table parallel. For example, make all the items within a column a noun or a phrase that starts with a verb."
- "Place information that identifies the contents of a row in the leftmost column of the table."
- "Don't leave a cell blank or use an em dash to indicate there's no entry for that cell. Instead, use *Not applicable* or *None*."
- **"Don't organize a table so that the column header forms a complete sentence when combined with the cell contents. This can make the table difficult to localize."**
- "Column headers identify the data each column contains. Make headers precise for usability. For example, don't use 'Name'. Instead, make column headers specific as in 'Group' or 'Employee'."
- Long tables: keep the header row always visible (fixed header on web; repeat header rows in documents).
- Punctuation: "If there's text that introduces the table, it should be a complete sentence and end with a period, not a colon."
- Cell punctuation: "use periods or other end punctuation only if the cells contain complete sentences or a mixture of fragments and sentences."

### 2.4 Responsive content — the reinforcing table limit

URL: https://learn.microsoft.com/en-us/style-guide/responsive-content (verbatim)

- **"Limit the number of columns in tables and keep the text in each cell brief—ideally one line. Tables with more than a few narrow columns might be hard to read. Too much text in a cell might cause a table to exceed the height of a mobile screen."**
- "Try to write sentences and paragraphs that are short enough to read on a mobile screen without scrolling."
- "Try to keep headings to one, short line. Two-line headings take up twice as much scarce vertical space."
- "Short sections—headings and the text that follows—are easier to read on small screens. Short sections also make it easier for customers to stop reading and later pick up where they left off."

### 2.5 Lists — the hardest numeric limit in any major guide

URL: https://learn.microsoft.com/en-us/style-guide/scannable-content/lists (verbatim)

- **"A list should have at least two items but (if possible) no more than seven items. Each item should be fairly short—the reader should be able to see at least two, and preferably three, list items at a glance."**
- "It's OK to have a couple of short paragraphs in a list item, but don't exceed that length too often."
- "Make all the items in a list consistent in structure. For example, each item should be a noun or a phrase that starts with a verb."
- Bulleted: "things that have something in common but don't need to appear in a particular order." Numbered: "sequential items (like a procedure) or prioritized items (like a top 10 list)."
- **Term lists — the explicit table replacement**: "If you must define, describe, or explain a set of terms or concepts, **a common alternative to a table is a list where each item consists of a term followed by a definition.**" Prescribed format: bulleted; term in sentence case and **bold**; period (in plain text) between term and definition; definition starts with a capital and ends with a period whether or not it's a full sentence.
- Lead-in: "Introduce the list with a heading, a complete sentence, or a fragment that ends with a colon." If a heading introduces it, "don't use explanatory text after the heading. Also, don't use a colon or period after the heading."
- "Don't use semicolons, commas, or conjunctions (like *and* or *or*) at the end of list items."
- Global tip: "If your content will be localized, avoid lists where the list items complete an introductory fragment. They can be difficult to translate."

### 2.6 Headings

URL: https://learn.microsoft.com/en-us/style-guide/scannable-content/headings (verbatim)

- "Think of headings as an outline, only more interesting—pithy, even. If readers don't read the headings, they probably won't read the text that follows, either."
- **"Avoid having two headings in a row without text in between—that might indicate a problem with organization or that the headings are redundant. But don't insert filler text just to separate the headings."**
- "If you can't find at least two distinct topics, skip the second-level headings."
- **"Use headings judiciously. One heading level is usually plenty for a page or two of content."** (The style guide itself uses four levels, offered as the long-content case.)
- "Keep headings as short as possible, and put the most important idea at the beginning."
- "Be as specific as you can, and be even more detailed with lower-level headings."
- **"Focus on what matters to customers… In most cases, don't talk about products, features, or commands in headings. Concentrate on what customers can achieve or what they need to know."**
- **"Use parallel sentence structure for all headings at the same level. For example, use noun phrases for first-level headings, verb phrases for second-level headings, and infinitive phrases for headings in instructions."**
- "Consider infinitive phrases, such as *To create a heading*, for headings and titles related to tasks. For headings that aren't related to tasks, use a noun phrase."
- "Don't end headings with a period." Sentence-style capitalization. Avoid ampersands, plus signs, and hyphens in headings.
- Run-in headings (bold lead-ins inside a paragraph) are endorsed as a compact structuring device: "they're ideal for packaging blurbs, web content, screen callouts, and the like," including for "cross-references" via a *See also* run-in.

### 2.7 Word choice / sentence structure

URL: https://learn.microsoft.com/en-us/style-guide/word-choice/ and .../use-simple-words-concise-sentences (verbatim)

- "To improve readability and comprehension, choose your words wisely and use them consistently. **If you mean the same thing, use the same word.**"
- "Make every word count. Concise, clear sentences save space, are easy to understand, and facilitate scanning."
- "Choose simple verbs without modifiers. Whenever you can, avoid weak or vague verbs, such as *be, have, make,* and *do*." (use → utilize/make use of; remove → extract/take away/eliminate; tell → inform/let know)
- "Don't use two or three words when one will do." (to → in order to; also → in addition; connect → establish connectivity)
- "Omit unnecessary adverbs… *quite, very, quickly, easily, effectively*."
- **"Use one term consistently to represent one concept."**
- "Use words that can be both nouns and verbs carefully—*file, post, mark, screen, record,* and *report*."

**Gap found:** Microsoft's style guide does **not** publish a numeric grade-level or reading-level target on its public pages. `learn.microsoft.com/en-us/style-guide/accessibility/writing-style-guidelines` returns 404; the readability targets commonly attributed to Microsoft come from `use-simple-words-concise-sentences` (qualitative only) and from third parties. **Do not claim a Microsoft grade-level number.** If a numeric readability target is wanted, source it from GOV.UK/Home Office (below), not Microsoft.

---

## 3. Write the Docs (community consensus)

### 3.1 Style guides page

URL: https://www.writethedocs.org/guide/writing/style-guides/

- "A style guide contains a set of standards for writing and designing content. It helps maintain a consistent style, voice, and tone across your documentation, whether you're a lone writer or part of a huge docs team."
- **"A consistent tone and style makes your content easier to read, reducing your users' cognitive load and increasing their confidence in the content's authority."**
- Scope can be minimal or vast: "as simple as a list of decisions you've made about how to refer to different items you frequently write about. Or… as complicated as the mighty tomes of major publication houses."
- Community recommendation is to **adopt an existing guide rather than write one from scratch**: Microsoft Writing Style Guide, Apple Style Guide, Google, Red Hat, Salesforce, Rackspace, Mailchimp, Adobe; plus AP Stylebook and Chicago as fallbacks.
- Should cover per-deliverable guidance: "API reference manuals, tutorials, release notes, or overviews of complex technical concepts."

### 3.2 Documentation principles — the two that matter most here

URL: https://www.writethedocs.org/guide/writing/docs-principles/

- **ARID — "Accept (some) Repetition In Documentation."** Explicitly positions documentation *against* DRY: while DRY applies to code, documentation needs some repetition of business logic to be effective. This is the single strongest community-consensus warrant for **replacing a cross-reference with a restated fact**.
- **Skimmable — "Structure content to help readers identify and skip over concepts which they already understand or are not relevant to their immediate questions."** Achieved via descriptive headings, meaningful hyperlinks, and putting identifiable concepts early in paragraphs.
- **Exemplary — "Include (some) examples and tutorials in content."** Note the built-in tension the page states: excessive examples reduce skimmability; separate examples from dense reference material.
- **Consistent — "Use consistent language and formatting in content."**
- **Current — "Consider incorrect documentation to be worse than missing documentation."**
- **Nearby — "Store sources as close as possible to the code which they document."**
- **Unique — "Eliminate content overlap between separate sources."** ⚠️ This is the counterweight to ARID and you must handle it explicitly: ARID licenses repetition *within* a reader's path; Unique forbids the *same content maintained in two sources*. The reconciliation the page implies: repeat the fact inline for readability, but keep exactly one source of truth for it.
- Publication principles: Discoverable, Addressable, Cumulative, Complete, Beautiful; plus Precursory ("Begin documenting before you begin developing") and Participatory.

### 3.3 Docs as code

URL: https://www.writethedocs.org/guide/docs-as-code.html

- "Documentation as Code (*Docs as Code*) refers to a philosophy that you should be writing documentation with the same tools as code": issue trackers, version control, plain text markup (Markdown/reStructuredText/AsciiDoc), code reviews, automated tests.
- Benefits claimed: "Writers integrate better with development teams"; "Developers will often write a first draft of documentation"; "You can block merging of new features if they don't include documentation."
- Cultural claim: "enables a culture where writers and developers both feel ownership of documentation."
- **Relevant caution for your diagnosis:** the page endorses automated tests on docs but says nothing about optimizing docs *for* machine verification. Docs-as-code justifies CI linting of style rules; it does not justify a table-shaped document. That distinction is worth making explicitly in the methodology.

### 3.4 Diátaxis (widely adopted in the WTD community)

URL: https://diataxis.fr/

- Four forms tied to four distinct needs: tutorials (learning-oriented), how-to guides (task-oriented), reference (information-oriented), explanation (understanding-oriented).
- The framework "solves problems related to documentation *content* (what to write), *style* (how to write it) and *architecture* (how to organise it)."
- Structural pairing: tutorials/how-to guides on one axis, reference/explanation on the other — reference and explanation are separate artifacts.
- **Application to your corpus:** a business rule registry is *reference* (tables are legitimate there); a use-case contract and an ADR are *explanation*; a runbook is *how-to*. Table-density that is correct in the registry is a defect in the ADR. This gives you a principled per-document-type table policy rather than a blanket rule.

---

## 4. Table complexity limits — published, concrete

This is the best-sourced part of the axis. Multiple independent authorities converge on the same caps.

### 4.1 GOV.UK content publishing guidance — the only published numeric size envelope

URL: https://guidance.publishing.service.gov.uk/formatting-content/text-formatting/tables/ (redirected from gov.uk/guidance/content-design/tables)

- "Use tables to present data or information that can be organised in a structured way, like numbers, text or statistics."
- **"Do not use tables for cosmetic reasons or when you can use normal page structure to present the information, for example headings and lists."**
- **Too small:** "the minimum size should be 2 columns and 3 rows (including headings)" — below that, write it as normal text.
- **Too large:** "on a desktop, you can usually see 4 or 5 columns and 10 rows without scrolling." Beyond that: break into smaller tables, or publish as a spreadsheet attachment.
- **"Your table can only have one heading row and one heading column."**
- "Your table must have: no split or merged cells."
- **"only one item per row cell – do not use line breaks"** — multiple items per cell break assistive technology.
- Empty cells: use "no data" or "not applicable"; only the top-left cell may be empty.
- Avoid complex tables with multiple heading rows/columns; if unavoidable, headings must be "descriptive and unique."

This gives you a defensible, citable numeric cap: **≈5 columns × 10 rows, one header row, one header column, one item per cell.** Note the 4–5 column figure is stated as a viewport observation rather than a hard rule, so cite it as "GOV.UK's practical ceiling," not "GOV.UK forbids more than 5 columns."

### 4.2 W3C/WAI — accessibility effectively caps table complexity

URLs:
- https://www.w3.org/WAI/tutorials/tables/
- https://www.w3.org/WAI/tutorials/tables/tips/
- https://www.w3.org/WAI/tutorials/tables/multi-level/

The WAI tutorial is structured as a **complexity ladder**, and each rung costs more markup:

1. Single header row → `<th>` / `<td>` is enough.
2. Two headers (row + column) → must add `scope="col"` / `scope="row"`.
3. Irregular headers → must add `colgroup` / `rowgroup`.
4. Multi-level headers → must add explicit `id` and `headers` attributes on every cell.

The rung-4 page contains the key admission:

- **"In many cases, it is worth considering to restructure the information in such tables to make them less complex for all readers, for example by splitting the information in smaller, more manageable tables."**
- The worked example splits one accommodation table into two (Paris, Rome), and W3C notes this makes the information **"easier to understand for everyone and easier to code,"** with better authoring-tool support.
- Rung 4 is triggered by "tables with three or more header cells associated with each data cell" or headers that repeat/change partway through — a usable **objective trigger** for "this table is too complex."

From the Tips page:

- **"Break up complex tables into simple individual tables, each containing the data for one sub-topic."**
- Start a new `<table>` when the topic changes rather than inserting extra header rows mid-table (extra header rows confuse screen readers).
- Each distinct data point needs its own cell; don't use `<br>` to fake rows — text resizing breaks the alignment.
- Never use tables for layout; legacy layout tables need `role="presentation"`.
- Don't cut tables off on small screens — provide scrolling rather than overflow hidden.
- Left-align text, right-align numeric data.

**The argument this enables:** accessibility conformance and human readability are not in tension here — WCAG-driven structure rules (one logical header dimension, no merged cells, no nested tables, split when complex) *are* the readability rules. A table that can't be marked up simply is a table that can't be read simply.

### 4.3 Convergence summary on table limits

| Rule | Google | Microsoft | GOV.UK | W3C/WAI |
|---|---|---|---|---|
| Don't use a table where a list works | ✅ ("If you have only one column… turn the table into a list") | ✅ ("Don't use a table just to present a list of items that are similar. Use a list instead.") | ✅ ("Do not use tables… when you can use normal page structure… headings and lists") | — |
| Limit columns | ✅ (implicit; responsive CSS) | ✅ ("Limit the number of columns") | ✅ (4–5 practical ceiling) | ✅ (split instead) |
| Cell text must be short | ✅ (tech-writing course: >2 sentences → wrong format) | ✅ ("ideally one line") | ✅ ("only one item per row cell") | ✅ (one data point per cell) |
| One header row + one header column only | ✅ ("first column and the first row only") | ✅ (header row) | ✅ (explicit) | ✅ (multi-level → restructure) |
| No merged cells | ✅ ("Don't use `colspan` or `rowspan`") | — | ✅ ("no split or merged cells") | ✅ |
| Split complex tables | — | — | ✅ | ✅ (explicit) |
| Prefer term/description list over table | ✅ (description lists for pairs) | ✅ ("a common alternative to a table is a list where each item consists of a term followed by a definition") | — | — |

### 4.4 Readability numbers (for a target, if you want one)

- **Google:** "Try to use fewer than 26 words per sentence." — https://developers.google.com/style/accessibility
- **Home Office (UK government) UCD Manual:** "writing for a maximum reading age of 9, even if you are writing for a specialist audience"; "Simple language doesn't mean dumbing down – short, clear sentences are easier to understand for everyone." Recommends Word's reading-age checker, Hemingway Editor, Readable, Rewordify. — https://design.homeoffice.gov.uk/accessibility/written-content/readability
- **Microsoft:** paragraphs of "Three to seven lines"; lists of 2–7 items. — https://learn.microsoft.com/en-us/style-guide/scannable-content/ and .../lists
- ⚠️ The "15–20 words per sentence" figure circulating for GOV.UK traces to the Plain English Campaign and to individual council/ONS guides, not to a GOV.UK primary page I could verify. Treat as **[실무 의견]** unless you find the primary. The reading-age-9 target *is* on a government primary source (Home Office).

### 4.5 [실무 의견] — supporting research and opinion, clearly non-official

- **NN/g, "How Users Read on the Web"** — https://www.nngroup.com/articles/how-users-read-on-the-web/ : "79 percent of our test users always scanned any new page they came across; only 16 percent read word-by-word." Recommends highlighted keywords, meaningful sub-headings, bulleted lists, "one idea per paragraph," inverted pyramid, and "half the word count (or less) than conventional writing." Measured: concise text +58% usability, scannable layout +47%, objective language +27%, combined **+124%**. This is 1997 research and the methodology is dated; cite it as directional evidence for scanning behavior, not as a modern controlled result.
- **NN/g, "Data Tables: Four Major User Tasks"** — https://www.nngroup.com/articles/data-tables/ : first column should be a human-readable record identifier; default column order should reflect importance to the user; keep related columns adjacent to avoid eye movement between distant columns. NN/g publishes **no numeric column cap** — don't attribute one to them.
- Practitioner blogs converge on "if a cell holds more than two sentences, it belongs elsewhere" and "display only essential columns," but these restate the Google/Microsoft rules without adding authority.

---

## 5. Synthesis: rules that most directly attack dense-table / cross-reference-heavy documents

**Against dense tables — five citable rules, strongest first:**

1. **Google, accessibility page:** *"Don't use tables unless it's the best method to present your information. Tables are challenging for screen readers."* — Reframes tables as the exception requiring justification, not the default. https://developers.google.com/style/accessibility
2. **Microsoft, lists page:** *"If you must define, describe, or explain a set of terms or concepts, a common alternative to a table is a list where each item consists of a term followed by a definition."* — This is the literal migration path for a business rule registry that is currently a wide table: **bold term + period + definition sentence**, in a bulleted list. https://learn.microsoft.com/en-us/style-guide/scannable-content/lists
3. **Google, tables page — the arity rule:** 1 unit per item → list; 2 units (term+description) → description list; **3+ related units → table.** This is an objective, mechanical test you can apply document-by-document to decide whether each existing table earns its shape. https://developers.google.com/style/tables
4. **Google tech-writing + Microsoft, jointly — the cell density cap:** *"If a table cell holds more than two sentences, ask yourself whether that information belongs in some other format"* / *"keep the text in each cell brief—ideally one line."* A registry table whose cells hold multi-sentence rule bodies fails both. https://developers.google.com/tech-writing/one/lists-and-tables and https://learn.microsoft.com/en-us/style-guide/scannable-content/tables
5. **W3C/WAI + GOV.UK — the complexity ceiling:** one header row, one header column, no merged cells, one item per cell, ≈5 columns × 10 rows; *"In many cases, it is worth considering to restructure the information in such tables… by splitting the information in smaller, more manageable tables."* Anything needing `id`/`headers` markup is by definition too complex and should be split. This converts "hard to read" from a taste judgment into a **conformance failure**. https://www.w3.org/WAI/tutorials/tables/multi-level/ and https://guidance.publishing.service.gov.uk/formatting-content/text-formatting/tables/

**Against cross-reference density — three citable rules:**

1. **Google:** *"Each link creates a decision for the reader, adding cognitive load. Each link is also a chance for the reader to leave the page and lose their place."* Plus the operative test: if the link would only define a term, briefly explain a concept, or give a couple of steps — **inline it instead of linking.** Plus *"within a given page, don't provide duplicate links to the same destination."* https://developers.google.com/style/cross-references
2. **Write the Docs, ARID:** *"Accept (some) Repetition In Documentation."* Explicit community rejection of DRY-for-docs. This is the principle that licenses your rewrite to restate a business rule at its point of use instead of shipping the reader to a registry. Pair it honestly with the **Unique** principle ("Eliminate content overlap between separate sources") — the reconciliation is *one source of truth, many restatements in reading paths*, not *many maintained copies*. https://www.writethedocs.org/guide/writing/docs-principles/
3. **Google link text:** every remaining link must be *"short, unique, descriptive"* and *"make sense without the surrounding text"* — ideally matching the target's title/heading. Cross-references written as bare IDs (`BR-NNN`, `UC-NN`) fail this test outright and are a mechanical find-and-fix across your ~50 docs. https://developers.google.com/style/link-text

**The structural move that ties both together:** Diátaxis says reference and explanation are different artifacts. Tables and cross-reference webs are legitimate *reference* affordances. The diagnosis "optimized for machine verification, hard for humans" is most precisely stated as: **reference-mode formatting has leaked into explanation-mode and how-to-mode documents.** The rewrite rule then becomes per-document-type rather than global — keep the registry tabular but conforming (≤5 columns, one-line cells, one header dimension), and convert ADRs, use-case contracts, and runbooks to prose + term lists + numbered procedures with inlined rule statements.

**A concrete, lintable rule set you can adopt wholesale** (all rules above are mechanically checkable in CI, which preserves the docs-as-code posture without preserving the table-shaped output): sentence < 26 words; paragraph 3–7 lines; list 2–7 items; table cells ≤ 1 line / ≤ 2 sentences; table ≤ 5 columns; exactly one header row and one header column; no merged cells; no link text shorter/vaguer than the target's heading; no duplicate links to the same destination within a page; sentence-case headings, parallel per level, no stacked headings, no skipped levels.
