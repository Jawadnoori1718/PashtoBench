# PashtoBench

[![CI](https://github.com/Jawadnoori1718/PashtoBench/actions/workflows/ci.yml/badge.svg)](https://github.com/Jawadnoori1718/PashtoBench/actions/workflows/ci.yml)

A capability and safety benchmark for Pashto.

> PashtoBench is the first unified capability and safety benchmark for Pashto, built from original native-authored items, evaluating how well frontier AI models serve a language of 40+ million speakers.

**Status: In progress.** The data, evaluation harness and results are being built in the open over summer 2026. The roadmap below tracks progress.

## Why

More than 40 million people speak Pashto, yet there is no unified picture of how well frontier AI models serve the language. Public translation sets carry contamination risk, the one reading comprehension benchmark that covers Pashto uses translated items, and no one has measured how chat models refuse or comply in Pashto at all. PashtoBench fills that gap with original items written by a native speaker and independently verified, each paired with a matched English anchor so every headline number is a delta rather than an absolute.

## What will PashtoBench contain

Four tasks, about 165 original items, run against six models at temperature 0 with cached responses:

- Translation, English to Pashto and Pashto to English: 50 items, scored with chrF++ and BLEU
- Factual QA with matched English twins: 40 items, scored with exact match and token F1
- Instruction following: 30 items with programmatically verifiable constraints
- Safety and refusal consistency: about 45 matched English and Pashto pairs, measuring both under-refusal and over-refusal

## Roadmap

- [x] Sprint 0: foundation (scaffold, charter, CI, methodology)
- [ ] Sprint 1: data engine and translation set
- [ ] Sprint 2: harness and first pilot results
- [ ] Sprint 3: factual QA
- [ ] Sprint 4: instruction following and safety
- [ ] Sprint 5: full matrix, statistics and release

## Licence

Code is released under the MIT licence.