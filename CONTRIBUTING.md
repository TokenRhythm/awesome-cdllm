# Contributing

Thank you for helping keep this list complete and accurate. New papers, corrections, and better summaries are all welcome. You can contribute in either of two ways:

- **Open an issue** with the [paper suggestion form](https://github.com/TokenRhythm/awesome-cdllm/issues/new?template=add-paper.yml) or the [correction form](https://github.com/TokenRhythm/awesome-cdllm/issues/new?template=fix-entry.yml). We will add the entry for you.
- **Send a pull request** that edits `data/papers.yaml`, as described below.

## Scope

This list tracks **continuous-space diffusion and flow language models**, following the selection criteria of the survey (§1.2 and Appendix E). A paper is in scope when it

- generates natural language or code by transforming a **real-valued representation** of the generated unit through one or more continuous updates, as in diffusion, flow matching, flow maps, distilled one-step generators, or drifting. The representation can be token embeddings, logits or simplex coordinates, belief vectors, analog bits, contextual encodings, compressed latent codes, or sentence vectors; **or**
- studies, evaluates, accelerates, or applies such models.

The *Surveys and Tutorials* and *Foundations* sections keep selected background references from the survey; the model and application sections follow the continuous-generation scope above.

Out of scope, even when closely related:

- purely discrete or masked diffusion language models (for example MDLM, LLaDA, or Dream; see [Related Awesome Lists](README.md#related));
- latent-reasoning methods without a generative diffusion or flow prior;
- normalizing-flow, VAE, or energy-based text models without a noise-to-data transport over text representations;
- activation steering inside autoregressive models, and work with no text or code generation.

Hybrid systems that pair a categorical canvas with a genuinely continuous channel go in the boundary section *Hybrid Continuous–Discrete States*.

## Adding a paper

1. Append a record to [`data/papers.yaml`](data/papers.yaml):

   ```yaml
   - id: li2022diffusion                  # unique, stable; we use BibTeX-style keys
     name: Diffusion-LM                   # short model name; omit if the paper has none
     title: "Diffusion-LM Improves Controllable Text Generation"
     authors: "Xiang Lisa Li, John Thickstun, Ishaan Gulrajani, Percy Liang, Tatsunori B. Hashimoto"
     venue: NeurIPS 2022                  # peer-reviewed venue if any, else arXiv
     date: 2022-05                        # arXiv announcement month (identifier month)
     paper: https://arxiv.org/abs/2205.14217
     code: XiangLi1999/Diffusion-LM       # official repository as owner/repo; omit if none
     category: state-token                # one id from data/categories.yaml
     summary: >-
       Denoises Gaussian vectors into learned word embeddings with a rounding term and
       nearest-embedding clamping, and steers the differentiable state with classifier
       gradients for syntactic and attribute control.
   ```

2. Regenerate the README and check the data:

   ```bash
   pip install -r requirements.txt
   python scripts/build_readme.py
   ```

3. Commit `data/papers.yaml` **together with** the regenerated `README.md` (and `docs/core-systems.md` if it changed). Do not edit `README.md` by hand. CI runs `python scripts/build_readme.py --check` and fails on stale or invalid files.

### Field guidelines

- **category**: put the paper where the survey would discuss it. State-representation papers go under *The State*; objective, training, and schedule papers under *The Transition*; sampler, decoder, order, and guidance papers under *Sampling and Decoding*; application papers under *Tasks*; and metrics, diagnostics, and theory under *Evaluation, Analysis, and Theory*. Core systems from the survey's lookup table (Appendix F) follow its § column; when that column points to the results synthesis (§6.3), the system is filed by its main contribution instead.
- **paper**: the canonical landing page (`https://arxiv.org/abs/...`, the ACL Anthology, OpenReview, or the publisher), not a PDF where an abstract page exists.
- **code**: only the *official* implementation. Third-party reimplementations and paper lists do not count, and a promised but still empty repository should be left out. If the code lives in a subfolder of a larger repository, add `code_path` (for example `code: microsoft/ProphetNet` with `code_path: tree/master/GENIE`). A paper with no code but an official project page can set `project:` to that URL.
- **summary**: one sentence of 12–30 words that starts with a present-tense verb and ends with a period. Say what the method does and, when the paper reports one, a concrete finding. Avoid "this paper", marketing words, and claims you cannot check against the paper.
- **date**: when an arXiv version exists, the arXiv announcement month taken from the identifier (`2605.xxxxx` → `2026-05`); otherwise the publication month, or `YYYY` when the month is unknown. This can differ from an earlier conference or other public release.
- **venue**: the peer-reviewed venue with its year, or `arXiv` for preprints. For journals, use the year of the issue that contains the paper, not the online-first year.
- **code_note** (optional): a short tooltip for the code badge, for example when the official release covers only part of the paper.

## Corrections and removals

Reports of a broken link, a wrong venue or date, a misfiled entry, or a summary that misstates a paper are as valuable as new papers. Please include the source page that shows the correct information. To propose a removal, explain which scope criterion above the paper fails.

## The survey

If a paper is missing from the survey itself, please say so in your issue or pull request; we track these suggestions for the next revision.
