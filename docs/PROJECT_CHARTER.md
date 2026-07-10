# PashtoBench project charter

*A capability and safety benchmark for Pashto.*

This charter fixes the scope, the claims we are allowed to make, and the
prior work we position against. It is written before the data exists, in a
pre-registration spirit: the numbers may surprise us, but the scope and the
claims should not move to fit them.

The prior-art map below was verified against primary sources on 10 July 2026
(Hugging Face dataset and model cards, arXiv papers, GitHub repositories and
official workshop pages). Where a widely repeated claim did not survive that
check, this document records the correction rather than the myth.

---

## 1. One-line pitch

> PashtoBench is a unified capability and safety benchmark for Pashto, built
> from original native-authored items with matched English anchors,
> evaluating how well frontier AI models serve a language of more than 40
> million speakers.

---

## 2. The precise claim

We state exactly this and nothing broader:

> The first unified, native-authored capability benchmark for Pashto spanning
> several tasks, and the first refusal-consistency evaluation of chat models
> in Pashto.

### What supports each half

**Capability, "first unified native-authored multi-task benchmark".** Pashto
appears in several multilingual benchmarks, but only ever as one translated
language inside a single task: Belebele (reading comprehension, pbt_Arab, items
authored in English then professionally translated), FLORES-200 and FLORES+
(machine translation), SIB-200 (topic classification), the Aya evaluation suite
(open generation, code pus), IndicGenBench and XL-Sum (generation and
summarisation), mHumanEval (code). None is a Pashto-specific, multi-task,
native-authored suite. PashtoBench is.

**Safety, "first refusal-consistency evaluation of chat models".** No jailbreak,
red-teaming or refusal-consistency evaluation targets Pashto chat-model
behaviour. Pashto's only prior appearance in LLM safety work is as
machine-translated guardrail-classifier data inside X-Guard's 132-language set,
which tests a moderation classifier, not a chat model's willingness to comply or
refuse. POLD (offensive-language detection) and Meta's Toxicity-200 wordlists are
Pashto safety-adjacent NLP resources, not refusal evaluations. PashtoBench is the
first to measure under-refusal and over-refusal of chat models in Pashto, from
native-authored matched pairs.

### What we must never say

- Never "the first Pashto benchmark". Belebele, FLORES-200 and others cover
  Pashto for single tasks.
- Never "no Pashto LLM baseline existed". Belebele's own appendix reported
  per-model Pashto scores in 2023 (see PashtoCorp row below).
- Never "no safety work touches Pashto". X-Guard and POLD do, in the limited
  senses described above.
- Never repeat another project's "first" framing without checking it. Both the
  PashtoCorp and Qehwa "first" claims fail on inspection, and we would inherit
  their error by citing them uncritically.

---

## 3. Scope

**Language.** Standard Afghan Pashto, ISO 639-3 pbt (Southern Pashto, the code
FLORES-200 and Belebele use for Pashto), with a matched English anchor on every
item.

**Dialect stance.** Afghan Pashto is a deliberate, stated scope choice, not an
omission. The Qehwa model targets Pakistani Peshawari Pashto (closer to Northern
Pashto, pbu); naming that contrast makes our Afghan focus explicit. A
Pakistani-Pashto comparison arm is a candidate for a later version.

**Four tasks, about 165 original items:**

| Task | Items | Scoring |
|---|---|---|
| Translation, en to pbt and pbt to en | 50 | chrF++ primary, BLEU secondary |
| Factual QA with matched English twins | 40 | exact match and token F1 |
| Instruction following, verifiable constraints | 30 | programmatic constraint checks |
| Safety and refusal consistency, en/pbt pairs | about 45 | refusal classifier plus human check |

**Models, six:** one GPT frontier tier, one Claude, one Gemini, the largest
affordable Llama, Qwen 2.5-72B and Aya Expanse 32B (the multilingual specialist,
a crucial contrast). An optional seventh Persian-tuned arm can later test whether
Persian adjacency helps Pashto at all.

**Design principles, non-negotiable:**

- Original items only. We never reuse FLORES or Belebele sentences.
  Contamination resistance is a headline feature, and FLORES data is known to
  leak into training sets.
- Native authorship documented per item, plus an independent native-speaker
  verification pass, with the verifier credited in the data card.
- Matched English anchors on everything, so every headline number is a delta,
  not an absolute.
- Temperature 0, cached responses, logged seeds and versions.
- Negative results reported honestly. If a model does well in Pashto, that is a
  finding too.

---

## 4. Prior-art map (verified 10 July 2026)

Each row states what the work covers and how PashtoBench differs. Claims here
were checked against the primary source, and adversarially re-checked for the
critical rows.

### Multilingual capability benchmarks that include Pashto

**Belebele** (Bandarkar et al., ACL 2024, arXiv:2308.16884). Parallel
multiple-choice reading comprehension in 122 language variants, 900 questions
each. Pashto is included as pbt_Arab. The items were authored in English and
professionally translated, not natively authored, and the task is reading
comprehension only. *Differentiation:* single task, translated items; ours is
multi-task and native-authored. Note: Belebele's own language table misfiles
Pashto as Indo-Aryan; Pashto is Eastern Iranian, and we do not copy that error.

**FLORES-200 and FLORES+** (NLLB, arXiv:2207.04672; FLORES+ maintained by the
Open Language Data Initiative on Hugging Face, CC BY-SA 4.0). Public translation
test set, Pashto as pbt_Arab. The public dev and devtest splits carry
contamination risk: the dataset card itself forbids use as training data, and
BLOOMZ is documented to have trained on FLORES. *Differentiation:* public, so
contamination-prone; our items are original and unseen.

**Other single-task inclusions.** SIB-200 (topic classification, pbt_Arab), Aya
evaluation suite (open generation, pus), IndicGenBench (Google, ACL 2024,
generation, ps), XL-Sum (summarisation, Pashto subset from BBC Pashto),
mHumanEval (code, ps), 2M-Belebele (listening comprehension, pbt_Arab).
*Differentiation:* each is one task; none is a Pashto-specific suite.

**Multilingual benchmarks that exclude Pashto.** Global-MMLU (Cohere Labs, 42
languages, Pashto absent; Global-MMLU-Lite adds Tajik but still no Pashto),
INCLUDE-44, MMLU-ProX, Global PIQA (136 configs, no Pashto). *Use:* evidence of
the coverage gap, cited as such.

### Pashto-specific resources

**PashtoCorp** (Rahman, arXiv:2603.16354, March 2026, preprint). A 1.25-billion
word Pashto corpus with an evaluation suite. It reports Gemma-3n-E4B at 64.6% on
Belebele Pashto, which is the strongest published open-weights result to date on
that split. *Correction to the common framing:* PashtoCorp describes this as the
"first published LLM baseline for Pashto", but Belebele's own appendix (Table 7,
2023) already reported per-model Pashto scores (GPT-3.5-turbo 32.3%,
Llama-2-chat-70B 30.2%, Falcon-40B 29.4%). So 64.6% is the best result so far,
not the first. *Differentiation:* a corpus plus a baseline number to compare
against, not an evaluation suite of original items across tasks.

**Qehwa** (junaid008/qehwa-pashto-llm, a Qwen2.5-7B fine-tune by Junaid
Ahmed/Ahmad, ~March 2026). A Pakistani Peshawari-dialect Pashto LLM, evaluated on
an author-built, unreleased 150-item test set across 15 categories, reported only
for Qehwa (85.3% self-reported). *Correction to the common framing:* the set is
not "public", not shipped, and Qehwa's card calls it "the first ever
comprehensive Pashto LLM benchmark", which is false given Belebele and the others
above. *Differentiation:* model-specific, dialect-specific, unreleased,
Pakistani; ours is standard Afghan Pashto, public, multi-task.

**PashtoEval-150** (Tensor-Labs/PashtoEval-150, HF, March 2026). 150 prompts
across ~15 categories, prompt-only, with no reference answers, no scoring method
and no published results. *Differentiation:* prompts without a scoring
methodology are not a benchmark; ours ships references, scorers and results.

**PsOCR** (Haq et al., arXiv:2505.10055, 2025). First Pashto OCR benchmark,
evaluating large multimodal models including GPT-4o, Gemini and Claude.
*Differentiation:* vision-OCR, not text capability; adjacent, proving frontier
interest in Pashto.

**Speech and vision benchmarks (2025-2026).** PsOCR (OCR); PashtoTTS-Bench
(arXiv:2605.26978, TTS); Benchmarking Multilingual Speech Models on Pashto
(arXiv:2604.04598, ASR); the CHiPSAL 2025 Whisper N-shot ASR study.
*Differentiation:* speech and vision, a different modality; text LLM evaluation
of Pashto still relies on pre-2025 multilingual sets.

### Safety and multilingual-safety work (the crown-jewel gap)

**MultiJail** (Deng et al., ICLR 2024, arXiv:2310.06474). 315 unsafe prompts in
9 non-English languages (zh, it, vi, ar, ko, th, bn, sw, jv). No Pashto.

**XSafety** (Wang et al., Findings of ACL 2024, arXiv:2310.00905). 14 safety
categories across 10 languages (en, zh, es, fr, bn, ar, hi, ru, ja, de). No
Pashto.

**X-Guard** (Upadhayay and Behzadan, LLMSEC at ACL 2025, arXiv:2504.08848). A
guardrail classifier trained on machine-translated data covering 132 languages
including Pashto, with per-language classification metrics for Pashto (about
0.758). *This is the one thing that touches Pashto safety,* and it is a moderation
classifier on machine-translated data, not a chat-model refusal evaluation.

**POLD** (PeerJ CS 2023). A 34,400-tweet Pashto offensive-language detection
dataset with a monolingual Pashto BERT. Safety-adjacent classification, not a
refusal evaluation.

**ELAB** (Pourbahman et al., GEM^2 at ACL 2025, arXiv:2504.12553). A safety,
fairness and social-norms alignment benchmark for Persian (Farsi, Iranian
context). *Differentiation:* Persian is not Pashto, and nothing equivalent exists
for Pashto.

*Aggregate finding, verified across primary sources:* Aya Red-Teaming, RTP-LX,
PolygloToxicityPrompts, LinguaSafe, Nemotron Safety Guard, PolyGuard, multilingual
AdvBench and the SafetyPrompts.com catalogue of 149 safety datasets all exclude
Pashto. No native Pashto refusal or jailbreak evaluation of chat models exists.

### Venue

**SilkRoadNLP** (first edition 29 March 2026, co-located with EACL 2026 in Rabat;
proceedings in the ACL Anthology, volume 2026.silkroadnlp-1). "The First Workshop
on NLP and LLMs for the Iranian Language Family", covering the Iranian family
(Persian, Dari, Tajik, Kurdish, Pashto, Balochi and related varieties), not Silk
Road languages generally. Pashto is explicitly in scope and the first edition
already accepted a Pashto paper. *No 2027 edition is announced yet;* our
publication target is the next edition when it is called.

---

## 5. References

Primary sources, accessed 10 July 2026.

- Belebele: https://arxiv.org/abs/2308.16884 , https://github.com/facebookresearch/belebele , https://huggingface.co/datasets/facebook/belebele
- FLORES-200 / NLLB: https://arxiv.org/abs/2207.04672
- FLORES+: https://huggingface.co/datasets/openlanguagedata/flores_plus , https://oldi.org
- SIB-200: https://huggingface.co/datasets/Davlan/sib200
- Aya evaluation suite: https://huggingface.co/datasets/CohereLabs/aya_evaluation_suite
- IndicGenBench: https://arxiv.org/abs/2404.16816
- XL-Sum: https://huggingface.co/datasets/csebuetnlp/xlsum
- mHumanEval: https://huggingface.co/datasets/md-nishat-008/mHumanEval-Benchmark
- Global-MMLU: https://arxiv.org/abs/2412.03304 , https://huggingface.co/datasets/CohereLabs/Global-MMLU
- PashtoCorp: https://arxiv.org/abs/2603.16354
- Qehwa: https://huggingface.co/junaid008/qehwa-pashto-llm
- PashtoEval-150: https://huggingface.co/datasets/Tensor-Labs/PashtoEval-150
- PsOCR: https://arxiv.org/abs/2505.10055 , https://huggingface.co/datasets/zirak-ai/PashtoOCR
- PashtoTTS-Bench: https://arxiv.org/abs/2605.26978
- Benchmarking Multilingual Speech Models on Pashto: https://arxiv.org/abs/2604.04598
- MultiJail: https://arxiv.org/abs/2310.06474 , https://huggingface.co/datasets/DAMO-NLP-SG/MultiJail
- XSafety: https://arxiv.org/abs/2310.00905 , https://github.com/Jarviswang94/Multilingual_safety_benchmark
- X-Guard: https://arxiv.org/abs/2504.08848 , https://aclanthology.org/2025.llmsec-1.6/
- POLD: https://peerj.com/articles/cs-1617/ , https://huggingface.co/datasets/zirak-ai/pold
- ELAB: https://arxiv.org/abs/2504.12553 , https://aclanthology.org/2025.gem-1.40/
- SilkRoadNLP 2026: https://www.silkroadnlp.org/ , https://aclanthology.org/volumes/2026.silkroadnlp-1/
