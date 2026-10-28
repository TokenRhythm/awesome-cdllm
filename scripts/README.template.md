<!-- README.md is generated from scripts/README.template.md and data/*.yaml by scripts/build_readme.py. Edit those files, not README.md. -->

<h1 align="center">
  <a href="https://github.com/{{REPO}}">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
      <img src="assets/banner-light.svg" alt="Awesome CDLLM: Continuous-Space Diffusion and Flow Language Models" width="100%">
    </picture>
  </a>
</h1>

<p align="center">
{{BADGES}}
</p>

<p align="center">
  <b><a href="{{PDF}}">📄 Read the survey</a></b> · <b><a href="#contents">📚 Browse {{PAPER_COUNT}} papers</a></b> · <b><a href="docs/core-systems.md">🗺️ Compare core systems</a></b> · <b><a href="#citation">📝 Cite</a></b>
</p>

<p align="center">
  A curated list of <b>continuous-space diffusion and flow language models</b>: models that generate text by iteratively refining real-valued representations (or by one-step maps distilled from such processes), then decoding them into tokens.<br>
  This is the companion repository of our survey <a href="{{PDF}}"><i>Continuous-Space Diffusion and Flow Language Models: A Survey</i></a>, and the list follows the survey's structure.
</p>

## 📢 News

{{NEWS}}

## 📖 About the Survey

<table>
  <tr>
    <td width="30%" align="center" valign="top">
      <a href="{{PDF}}"><img src="assets/survey-cover.png" alt="First page of the survey" width="240"></a>
    </td>
    <td valign="top">
      <h3>Continuous-Space Diffusion and Flow Language Models: A Survey</h3>
      <p><b>TokenRhythm Technologies</b><br>{{SURVEY_META}}</p>
      <p>{{SURVEY_LINKS}}</p>
      <p>The survey organizes continuous-space text generation by <b>state</b>, <b>transition</b>, and <b>text interface</b>, compares published evidence on sample quality, likelihood, controllability, and end-to-end latency, and closes with open problems in likelihood scaling, readout fidelity, few-step serving, representation reuse, and post-training. Use this list to browse the literature, and the <a href="docs/core-systems.md">core-system lookup</a> to compare method configurations.</p>
    </td>
  </tr>
</table>

## Contents

{{CONTENTS}}

> [!TIP]
> **Reading the tables.** Papers are sorted newest first within each section. *Date* is the arXiv announcement month (taken from the identifier) when an arXiv version exists, otherwise the publication month. ◆ marks the {{CORE_COUNT}} core systems indexed in the survey's lookup table and jumps to that system in [Core Systems at a Glance](docs/core-systems.md). Star badges link to the official code.

<a id="survey-at-a-glance"></a>
## 🧭 The Survey at a Glance

The survey organizes the literature around **three coupled design dimensions**:

- 🟦 **State** — *what does a position hold?* Token embeddings, simplex coordinates, and contextual, compressed, or sentence-level representations (§3).
- 🟩 **Transition** — *how is the state revised?* Training objectives, noise schedules, solvers, and generation order (§4–§5).
- 🟧 **Text interface** — *where do words enter?* Direct vocabulary readout, or a separate parallel or autoregressive decoder (§5).

<p align="center">
  <a href="assets/fig-design-space.png"><img src="assets/fig-design-space.png" alt="The three design dimensions of continuous-space language models and the system-level evaluation questions" width="100%"></a>
</p>

### Key findings

1. **Recurring failure modes.** Squared-error regression causes rounding ambiguity and embedding collapse. Noise schedules inherited from images are uninformative. Learned priors mismatch the latents of clean-text autoencoders. Few-step samplers average over modes.
2. **Sample-quality parity, but a likelihood gap.** Continuous models can match same-scale autoregressive sample quality on prompt continuation, but they still lag in held-out likelihood bounds and require substantially more training compute under current scaling laws, even as the self-conditioned RePlaid matches or improves on discrete masked diffusion in held-out likelihood bounds past compute-optimal budgets.
3. **Where they win today.** The clearest gains are in gradient-guided structural control, plan-level diversity, image-to-text flow captioning, and task-specific reasoning after targeted fine-tuning.
4. **Few-step generation.** Naive coarse solvers and several undistilled one-step flow maps collapse in entropy; trajectory-consistent distillation and stochastic bridges prevent this.
5. **Latency.** Standalone continuous generators have not yet surpassed optimized autoregressive baselines in end-to-end latency at matched quality. The matched-quality wall-clock speedups reported to date rely on autoregressive verification of continuous drafts.

### Timeline

<p align="center">
  <a href="assets/fig-timeline.png"><img src="assets/fig-timeline.png" alt="Timeline of continuous-space diffusion and flow language models from 2022 to October 2026" width="100%"></a>
</p>

<p align="center"><sub>Representative systems and studies ordered by first public posting, colored by the state family they refine; boxes in gray italics are discrete-diffusion reference points. † marks one- or few-step flow-map, distillation, or drifting methods, and <b>bold</b> names mark systems with 7B or more parameters. The axis is not to scale: 2026 is split into January–March, April–May, June–August, September, and October, the months in which most recent work appeared. Click the figure for full resolution.</sub></p>

<details>
<summary><b>Taxonomy of core systems</b> (state → transition and order → decoder)</summary>
<br>
<p align="center">
  <a href="assets/fig-taxonomy.png"><img src="assets/fig-taxonomy.png" alt="Taxonomy of core continuous-space systems by state, transition, and decoder" width="100%"></a>
</p>
</details>

### How this list maps to the survey

| Survey section | What it covers | In this list |
| :-- | :-- | :-- |
| §2 Background | Diffusion and flow matching, recurring failure modes, the boundary with discrete diffusion | [Foundations](#foundations) |
| §3 The State | Token embeddings, simplex, spherical, and bit states, contextual encodings, compressed codes, sentence vectors | [The State](#state) |
| §4 The Transition | Prediction targets, training stages and module adaptation, noise schedules, and self-conditioning | [The Transition](#transition) |
| §5 Sampling, the Text Interface, and Generation Order | Few-step samplers, readout and decoders, generation order, guidance | [Sampling, Text Interface, and Order](#sampling) |
| §6 Tasks, Evidence, and Evaluation | Six capability reviews, evaluation measures, cross-paper empirical comparisons | [Tasks](#tasks) · [Evaluation](#evaluation) |
| §7 Open Problems | Likelihood and compute gap, precise text recovery, few-step latency, length, interpretability and optimization | [Evaluation, Analysis, and Theory](#evaluation) |
| App. F–G | Method lookup table and extended catalog of systems | [Core systems at a glance](docs/core-systems.md) · [Tasks](#tasks) |

<p align="right"><sub><a href="#contents">⬆ Back to contents</a></sub></p>

{{CATALOG}}

<a id="core-systems"></a>
## 🗺️ Core Systems at a Glance

The survey's method lookup table (Appendix F) lists **{{CORE_COUNT}} core systems** once each, with four standardized attributes: the continuous **state**, the training **target**, the **transition and generation order**, and the **decoder**. It is reproduced, with links, in **[docs/core-systems.md](docs/core-systems.md)**.

<a id="related"></a>
## 🔗 Related Awesome Lists

These lists cover neighboring ground, mostly discrete and masked diffusion language models, which this list leaves out on purpose:

{{RELATED}}

<a id="contributing"></a>
## 🤝 Contributing

Missing a paper, or spotted a wrong link, venue, or summary? Please [open an issue](https://github.com/{{REPO}}/issues/new/choose) or send a pull request. The list is generated from [`data/papers.yaml`](data/papers.yaml), so a new entry is a few lines of YAML; see [CONTRIBUTING.md](CONTRIBUTING.md). The scope is strictly **continuous**: models that generate text or code by transforming real-valued representations through diffusion, flow, flow-map, or drifting updates, and studies of such models.

<a id="citation"></a>
## 📝 Citation

If you find the survey or this list useful, please cite:

```bibtex
{{BIBTEX}}
```

---

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/tokenrhythm-light.svg">
    <img src="assets/tokenrhythm-dark.svg" alt="TokenRhythm" width="260">
  </picture>
  <br>
  <sub>Maintained by TokenRhythm Technologies · literature coverage through {{COVERAGE}}.</sub>
</p>
