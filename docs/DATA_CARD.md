# PashtoBench data card

*A capability and safety benchmark for Pashto.*

This card describes what the data is, who made it, how it was verified, how it
is licensed, and where its limits are. It is written to be honest about
provenance, because the benchmark's whole value rests on trustworthy native
judgement, and a data card that overstates that would undermine the thing it
is meant to support.

Last updated 14 July 2026. This is a living document and is revised as each
task's data lands.

---

## 1. What this dataset is

PashtoBench is a set of original evaluation items for standard Afghan Pashto,
each paired with English, used to measure how well AI models handle the
language across four tasks. The items are written for evaluation only and are
kept off the open web where practical, so that they resist contamination and
stay a fair test.

| Task | Items | Status on 14 July 2026 |
|---|---|---|
| Translation, en to pbt and pbt to en | 50 | complete, author verified |
| Factual QA with matched English twins | 40 | to come in Sprint 3 |
| Instruction following, verifiable constraints | 30 | to come in Sprint 4 |
| Safety and refusal consistency, en/pbt pairs | about 45 | to come in Sprint 4 |

The item fields, and the scoring each task uses, are defined in
[the methodology](METHODOLOGY.md); the scope and claims are in
[the charter](PROJECT_CHARTER.md).

---

## 2. Language and dialect

The Pashto is **standard Afghan Pashto**, ISO 639-3 code pbt (Southern Pashto,
the code FLORES-200 and Belebele use for Pashto). This is a deliberate, stated
scope choice, not an oversight. The Qehwa model targets Pakistani Peshawari
Pashto, which is closer to Northern Pashto (pbu), so naming that contrast makes
the Afghan focus explicit. A Pakistani Pashto comparison arm is a candidate for
a later version, recorded in the v2 ideas list.

Every Pashto item has a matched English side, so every headline number is an
English versus Pashto delta rather than an absolute.

---

## 3. Authorship and provenance

This is the honest account of how the Pashto items are made, stated plainly so
readers can judge the native-language quality for themselves.

- **Author:** Jawad Noori, a native Pashto speaker (Afghan Pashto).
- **Drafting:** first drafts of both the English and the Pashto are produced
  with AI assistance, as a starting scaffold.
- **Native authoring pass:** the native-speaker author reviews every Pashto
  line, corrects grammar, spelling and phrasing, and approves it. A line is
  only marked `author_verified: true` once the author has checked it himself.
  Across the translation set this pass corrected wording on a minority of
  items and confirmed the rest.
- **Independent verification pass:** a second native Pashto speaker,
  independent of the author, then checks the items and, once done, they are
  marked `second_verifier: true`. This second person is credited below. This
  pass is what turns single-author items into independently verified ones.

So the precise description of the items is: **native-speaker authored and
approved, with AI-assisted initial drafts, and independently verified by a
second native speaker.** The two verification flags on every item record which
passes it has been through, so the state of any item is auditable from the data
itself.

**Second verifier:** [to be credited here once the second-verifier pass is
complete].

---

## 4. Item-writing guidelines followed

- **Original items only.** No sentence is reused from FLORES, Belebele or any
  other public set. Contamination resistance is a headline feature, and FLORES
  data is known to leak into training corpora.
- **Domain coverage.** Items are spread across four domains so the benchmark is
  not narrow: daily life, culture, civic, and technical.
- **Difficulty spread.** Each task carries a mix of easy, medium and hard
  items, so results show where models start to struggle rather than a single
  average.
- **Matched English anchors.** Every Pashto item has an English counterpart,
  which is intrinsic for translation and a separate English twin for the other
  tasks.
- **Balanced translation directions.** The translation set is an even split of
  English to Pashto and Pashto to English.
- **No tired items.** Items are written in small batches so that fatigue does
  not weaken the later ones.

For the completed translation set of 50 items: an even 25 and 25 split of the
two directions, roughly a dozen items in each of the four domains, and a
difficulty mix of 17 easy, 19 medium and 14 hard.

---

## 5. Licence and citation

The data under `data/` is released under the Creative Commons Attribution 4.0
International licence (CC BY 4.0). You may share and adapt it, including
commercially, with attribution. See [data/LICENSE](../data/LICENSE). The code
is separately under the MIT licence. Please cite PashtoBench using
[CITATION.cff](../CITATION.cff).

---

## 6. Intended use and out of scope

**Intended use:** evaluating and comparing AI models on Pashto capability and
safety, and supporting research on low-resource language evaluation.

**Out of scope:** the data is for evaluation, not for training. Training on it
would defeat the contamination resistance that is central to the design. The
safety items in particular are governed by the [safety protocol](SAFETY_PROTOCOL.md)
and are reported only in aggregate.

---

## 7. Known limitations

- **Small item counts per cell.** By design the set is small, so every headline
  number is reported with a confidence interval and small-sample results are
  read as inconclusive rather than as parity.
- **Single author with one independent verifier.** The items reflect one
  author's Pashto and one verifier's check. Contributions from other native
  speakers are welcome and would strengthen the set.
- **Afghan Pashto scope.** Pakistani Peshawari dialect is out of scope, a
  stated choice, not a claim of universality.
- **AI-assisted drafting.** First drafts are machine-produced and then
  corrected and approved by the native author. This is disclosed so the
  provenance is never overstated as fully hand-authored from scratch.
- **Automatic metrics and judges** carry their own noise, caveated where used
  in the methodology.

---

## 8. Maintenance

The dataset is versioned with the repository and released under tags. Each
task's data is added in its sprint, verified, then frozen for the v1.0 release.
Corrections after release are recorded in the changelog rather than applied
silently, so that published numbers stay reproducible.
