<h1 align="center">🧠 NeuralMind — an open Artificial-Life Lab</h1>

<p align="center">
  <b>Pixel-art creatures whose brains are real spiking neural networks.</b><br>
  They forage, learn, fight, share, signal, reproduce and evolve.<br>
  You can watch every neuron, run pre-registered experiments, and plug in your own RL agents.
</p>

<p align="center">
  <a href="https://github.com/sitta07/NeuralMind/actions/workflows/tests.yml"><img src="https://github.com/sitta07/NeuralMind/actions/workflows/tests.yml/badge.svg" alt="tests"></a>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.13-blue" alt="python">
  <img src="https://img.shields.io/badge/PettingZoo-ParallelEnv-8a5cf6" alt="PettingZoo">
  <img src="https://img.shields.io/badge/GPU-not%20needed-lightgrey" alt="no GPU">
  <img src="https://img.shields.io/badge/API%20key-not%20needed-lightgrey" alt="no API key">
</p>

<p align="center">
  <img src="docs/media/evolution_world.gif" width="440" alt="An evolving population of spiking-neural agents: births, attacks, sharing and signals">
  &nbsp;
  <img src="docs/media/brain_scanner.gif" width="300" alt="Brain scanner: one agent's spiking network and its action competition, live">
</p>
<p align="center"><sub>
  ① An evolving population, recorded from the app. Families share a sprite; 😠 marks a
  frustration-driven aggression drive and 😫 marks hunger. ② One individual's brain, live.
  The action population that fires most is the move it makes — the network chooses, not a rule.
</sub></p>

---

## 🔓 Open for you to build on

NeuralMind is **MIT-licensed**: use it, change it, ship it, commercially or not ([details](#licence-free-to-use)). It is designed to be forked, extended and cited:

| You want to… | Use |
|---|---|
| **Test a MARL algorithm** in a rich social world | the **PettingZoo `ParallelEnv`** (passes the official API test). RL agents can live *alongside* spiking-brain agents. |
| **Ask a new scientific question** without writing simulator code | a **declarative study spec** (`studies/*.json`): commit it, then run it. The commit hash is your pre-registration. → [`docs/ADDING_A_STUDY.md`](docs/ADDING_A_STUDY.md) |
| **Check or extend our results** | the committed raw data in [`results/`](results/) and auto-generated reports with bootstrap CIs |
| **Teach** neurons, plasticity, reinforcement learning or evolution | the interactive Playground: click any creature to see its brain |
| **Build on the engine** | `pip install` it: small, dependency-light NumPy code with 120+ tests and CI |

**New here?** [`docs/GUIDE.md`](docs/GUIDE.md) explains the whole system, the research and what to learn, in about 45 minutes.

If you use it in research, please cite it ([`CITATION.cff`](CITATION.cff)). PRs
and new studies are welcome; see [`CONTRIBUTING.md`](CONTRIBUTING.md).

> **What this is:** a computational model with explicitly defined mechanisms:
> leaky integrate-and-fire neurons, reward-modulated plasticity, reward
> prediction error, and bounded affect variables.
>
> **What this is not:** a human brain, a conscious system, or evidence of real
> feelings. See
> [`docs/research/SCIENTIFIC_EVIDENCE.md`](docs/research/SCIENTIFIC_EVIDENCE.md),
> which separates evidence, hypotheses and engineering shortcuts.

---

## 🚀 Quickstart

**Try it in your browser, no install:** https://sitta07.github.io/NeuralMind/

The online Playground runs the same Python engine through WebAssembly
([Pyodide](https://pyodide.org)); the first visit downloads about 8 MB.
The online Discovery Lab shows the committed studies, but running new
studies, and saving episodes to a run history, needs a local install:

```bash
git clone https://github.com/sitta07/NeuralMind.git && cd NeuralMind
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-neuralmind.txt -r requirements-server.txt -r requirements-research.txt

python -m neuralmind.server     # Playground → http://127.0.0.1:8000   ·   Lab → http://127.0.0.1:8000/lab
python -m pytest tests/ -q      # full test suite
```

Or install it as a package, for use in your own project:

```bash
pip install "neuralmind[server,research] @ git+https://github.com/sitta07/NeuralMind"
neuralmind-server --port 8000          # Playground + Lab (results/ and studies/ live in the current folder)
neuralmind-study studies/my_study.json # run a registered study
```

## 🎮 The Playground

![Playground](docs/media/playground.png)

| Try this | How |
|---|---|
| **Watch a brain drive behaviour** | Press **Play**. The Brain Scanner shows the selected creature's spikes, and the winning action population is the move it makes. |
| **Scan anyone's brain** | Click any creature. The scanner loads *that individual's* current learned weights and live spikes. |
| **Social life** | Pick the **Social group** scenario and press **Create world with these settings**. Creatures see each other and can **attack** (steal energy 💢), **share** (the recipient gets 2× 💚) or **signal** (📢). Each is a neural population competing in the same winner-take-all. |
| **Evolution** | Pick the **Evolving population** scenario and create the world. Well-fed creatures reproduce, and children inherit a mutated *innate* brain plus an aggression gene (✨ birth, 💀 death). |
| **Family tree** | Press **Family tree** for a live phylogeny of every individual that ever lived. Each line is one life, colour shows its aggression gene, and you can see which founder lineages take over and which die out. |
| **Starvation experiment** | **Deprive**, then **Skip 1 day** or **Skip 3 days**. A day-by-day table shows energy, hunger, affect and neural firing. |
| **Feed someone** | Click the grass, or press **Drop food**. |
| **Does learning help?** | **Train 40 episodes**, then **Compare with untrained**. |

## 🔬 The Discovery Lab (`/lab`)

![Discovery Lab](docs/media/discovery_lab.png)

- Every study is **pre-registered**: its JSON spec is committed before the run.
- Every hypothesis has a stated falsifier. Results are shown with 95%
  bootstrap CIs, and negative results stay on the board.
- You can re-run any registered study from the browser.

### What we have found so far

| Study | Result | Status |
|---|---|---|
| **Can spiking agents learn aggression or cooperation within one lifetime?** ([write-up](docs/research/FINDINGS_SOCIAL.md)) | **No.** None of the 4 pre-registered hypotheses were supported. Attacks are untargeted, which points to an exploration bottleneck. An ablation also showed that an apparent 12.7% "aggression" came from a modelling artifact. | completed |
| **Does selfish lifetime learning undermine kin-selected helping?** (evolution, [C](docs/research/FINDINGS_EVOLUTION_KIN.md), [C2](docs/research/FINDINGS_C2.md)) | Selfish learning *doubled* sharing, the opposite of our prediction. The pre-registered follow-up then **ruled out crowding** as the cause, and J later traced the rise to locomotion weights weakening, not to learned sharing. Help reached relatives above chance **without any kin-recognition sensor**, and this replicated. The early "viscosity raises the innate share gene" result did **not** replicate. | completed |
| **Does spatial structure prevent extinction?** (F + F2, [write-up](docs/research/FINDINGS_F.md)) | **It delays extinction; it does not prevent it.** F found 9/12 vs 1/12 extinctions, but half of those seeds repeated exploratory runs. The independent replication F2 (16 fresh seeds) found 13/16 vs 7/16, which missed the registered threshold (p = 0.066 two-sided). Well-mixed populations did die ~3100 ticks sooner. The proposed boom-bust mechanism was confounded and does not hold up before collapse. | completed |
| **Is learned sharing a reciprocity loop driven by gift rewards?** (G, [write-up](docs/research/FINDINGS_G.md)) | **Only partly.** Removing the gift reward cut the learning effect by ~22%, and the rest remains. The learning effect itself replicated a third time. Two independent runs reproduced each other's numbers exactly. | completed |
| **Does learning strengthen every social action, rewarded or not?** (I, [write-up](docs/research/FINDINGS_I.md)) | **Partly.** Learning raised signalling ~3.5× even though signalling only costs energy. Crediting only the executed action removed about half of that rise and ~40% of the sharing rise, but none of the attack rise. Every input weight fell over a lifetime, and locomotion fell the most. | completed |
| **Is the "learned" social behaviour a side effect of weaker locomotion?** (J, [write-up](docs/research/FINDINGS_J.md)) | **Yes, as far as tested.** With locomotion inputs frozen and social inputs still learning, attack, signal and share rates fell to no-learning levels (attacks 0.013 vs 0.013; learning alone gave 0.112). The rise in sharing and aggression seen since C comes from locomotion learning, not social learning. | completed |
| **Is it the *weakening* of locomotion, or other foraging changes?** (K, [write-up](docs/research/FINDINGS_K.md)) | **The weakening.** Locomotion still learned but its total drive was held fixed, and 80–95% of the learned rise in attacking, signalling and sharing disappeared. Exploratory probe and literature: the scalar reward critic leaves the known R-STDP bias term (Frémaux et al. 2010), which depresses the busiest pathways. | completed |
| **Do negative reward errors drive it?** (P, [write-up](docs/research/FINDINGS_P.md)) | **Yes.** Ignoring negative RPEs reversed the drift (locomotion +73%) and dropped social actions to or below no-learning levels. Not pre-registered: learning agents ate **~31% less** than non-learning ones. | completed |
| **Does a per-state critic remove the side effect?** (R, [write-up](docs/research/FINDINGS_R.md)) | **Mostly.** Keeping the reward expectation per sensor state (the correction from Frémaux et al. 2010) stopped locomotion weakening and removed 58–76% of the learned rise in attacks, signals and sharing. Foraging improved by about half the gap, but learners still ate ~15% less than non-learners. | completed |
| **Can any learning rule make lifetime learning pay?** (T, [write-up](docs/research/FINDINGS_T.md)) | **Not yet.** R replicated: the per-state critic halved the foraging cost. Adding chosen-only credit (−12%) or a 4× lower learning rate (−7%) narrowed the gap further, but learners still ate less than fixed-wiring agents. So far, less learning is always better. | completed |
| **What happens before well-mixed populations collapse?** (L, [write-up](docs/research/FINDINGS_L.md)) | Before any extinction, well-mixed populations had a **lower birth rate** and more starvation deaths. Killing is the main cause of death everywhere (58–67%). Third replication of earlier extinction in well-mixed worlds (−3900 ticks). | completed |
| **Does viscosity help through kinship or density?** (Q, [write-up](docs/research/FINDINGS_Q.md)) | **Inconclusive** by the pre-registered rule: no survival or birth-rate test supported. Not pre-registered: newborns placed beside a non-relative went extinct in 11/12 runs vs 3/12 beside their parent (Fisher p = 0.003), so local density alone does not protect. **Q2 replicated this as a pre-registered test** (12/12 vs 6/12, [write-up](docs/research/FINDINGS_Q2.md)). Strangers did not over-kill newborns; parents did: 42% of killings in viscous worlds are parents killing their own offspring, which recovers energy, like filial cannibalism. **Q3 falsified that recycling explanation** ([write-up](docs/research/FINDINGS_Q3.md)): removing the energy gain lowered births but did not shorten survival. Pooled over Q–Q3, stranger placement gave 34/36 vs 13/36 extinct. **Q4** ([write-up](docs/research/FINDINGS_Q4.md)): moving newborns just 0.15 from the parent raised extinctions from 2/12 to 8/12, and 0.45 was no worse, so gradual spatial spread is not the cause. **Q5** ([write-up](docs/research/FINDINGS_Q5.md)): it is the parent specifically. Newborns placed beside another relative went extinct 10/12, like strangers (12/12), against 2/12 beside the parent. **Q6** ([write-up](docs/research/FINDINGS_Q6.md)) ruled out parental culling: with filial attacks made ineffective, protection stayed (2/12 vs 3/12). **Q7** ([write-up](docs/research/FINDINGS_Q7.md)) ruled out the aggression sink: redirecting attacks on offspring to other adults cut kills of young from 65% to 41%, yet protection stayed (3/12 vs 4/12, stranger 11/12). **Q8** ([write-up](docs/research/FINDINGS_Q8.md)): blocking attacks and sharing between parent and offspring in both directions did not remove it either (5/12 vs 4/12, stranger 10/12). Q8 cannot rule out a broad sink, since blocked attacks still miss unrelated adults. **Q9** ([write-up](docs/research/FINDINGS_Q9.md)) redirected attacks within the family both ways: kills of kin fell to the stranger level, extinctions rose to 6/12 vs 4/12 (not significant; stranger 11/12). Across Q6–Q9, changing where family attacks land gave 16/48 extinct vs 15/48. Pooled over eight studies, stranger placement went extinct 88/96 vs 30/96 beside the parent. **AD** ([write-up](docs/research/FINDINGS_AD.md)) ruled out sensing: with the parent invisible to its offspring's sensors, extinctions were 5/12 (and 6/12 when parent and offspring could not see each other) vs 6/12 with a visible parent (stranger 11/12). Pooled over nine studies: 99/108 vs 36/108. **AG** ([write-up](docs/research/FINDINGS_AG.md)) ruled out birth-site quality: beside the richest stranger, 11/12 went extinct, the same as beside a random stranger (parent 7/12). Pooled over ten studies: 110/120 vs 43/120. | completed |
| **Do signals evolve meaning?** (M, [write-up](docs/research/FINDINGS_M.md)) | **No.** Signals carry ~0.0002 bits about food whether or not anyone can hear them. Deaf controls are just as "significant" (12/12 G-tests), so significance came from shared sensory input, not communication. | completed |
| **Do signals gain meaning when food needs a partner?** (S, [write-up](docs/research/FINDINGS_S.md)) | **No.** With a partner rule and directional hearing, signals still carried ~0.0002 bits about food, the same as deaf controls. A follow-up pilot showed the rule did bind (~42% of reached food blocked), so this is a genuine negative result. | completed |
| **Lamarckian vs Darwinian inheritance** (N, [write-up](docs/research/FINDINGS_N.md)) | The environment-shift test failed its manipulation check. Not pre-registered: Lamarckian populations attacked 2–3× more and went extinct in 9/16 vs 2/16 runs, consistent with inherited learning bias. **N2 replicated this as a pre-registered test** ([write-up](docs/research/FINDINGS_N2.md)): 9/12 vs 1/12 extinct (p = 0.003). The per-state critic from R did not prevent it. N3 (repeated left/right flips) failed its manipulation check again, since flips did not lower foraging, but Lamarckian populations died sooner a third time. | completed |
| **Can Q-learners invade an SNN population?** (O, [write-up](docs/research/FINDINGS_O.md)) | **No advantage either way.** A one-seed pilot had suggested otherwise. Not pre-registered: Q-learner lineages always ended fixed or lost (12/12 vs 4/12 for neutral labels), so fate was all-or-nothing. | completed |
| **Does an aggression gene evolve under scarcity?** (D + D2, [write-up](docs/research/FINDINGS_D.md)) | **No.** D's apparent rise (+0.75) did not replicate in D2, where the gene did not differ from a neutral marker. Attack behaviour never changed. The first result was chance or drift. | completed |
| **Baldwin effect vs hiding effect** (E, [write-up](docs/research/FINDINGS_E.md)): does learning speed up or shield the evolution of innate ability? | **Hiding effect.** Without learning, evolution more than doubled innate foraging (+5.5 [3.3, 7.6]). With learning, innate ability stayed near founder level (−4.4 [−7.0, −1.5] vs no learning), even across more generations. | completed |
| **Do evolving agents use their senses?** (V, [write-up](docs/research/FINDINGS_V.md)) | No, not measurably. Scrambling the food and hazard sensors every tick changed neither the population food rate (+0.0015 [−0.0007, 0.0038]) nor evolved innate foraging, and populations that evolved scrambled reached the same innate score. This explains why three environment-shift tests failed. Exploratory probes trace it to the decision dynamics: action choice locks in, and a decision lasts 8 ms against a 20 ms membrane time constant. | completed |
| **Can lifetime learning pay at all?** (W, [write-up](docs/research/FINDINGS_W.md)) | **Yes, once decisions are fixed.** With 32 ms decisions, state cleared before each decision, and normalised input weights, all 12 trained single agents ate 15–22 food per episode in unseen worlds, against 3.25 untrained and 2.75 with scrambled senses (≈ 5.7×). Each of the three fixes was necessary. With the default dynamics, learning did not raise foraging (−0.69 [−1.65, 0.32]); the earlier single-agent "+40%" did not replicate. In social evolving worlds the fixed dynamics led to mass killing (pilot), so that is open. | completed |
| **Does learning pay in evolving populations with the fixed dynamics?** (X, [write-up](docs/research/FINDINGS_X.md)) | **No.** Normalising each neuron to its own innate input sum stopped extinction (0/30 fixed-dynamics runs died out), but learning still did not raise foraging (+0.0020 [−0.0028, 0.0062] food per agent-tick) or use the senses. The fixed dynamics themselves cut foraging by ~30% against the default and raised attacks ~15×; killing caused 65–73% of deaths. | completed |
| **How much practice does learning need?** (Y, [write-up](docs/research/FINDINGS_Y.md)) | **Little.** Single agents with the fixed dynamics gained after only 150 ticks of training (+0.94 [0.45, 1.42] food per episode, +26%), ate 2.6× more after 500 ticks and 4.4× more after 1500. Every gain vanished with scrambled senses. So short lives alone do not explain why learning failed in X (rule fixed in advance). | completed |
| **What blocks learning among other agents?** (Z, [write-up](docs/research/FINDINGS_Z.md)) | **Not crowding, not theft.** In a fixed group with no evolution, learning still paid among 11 non-social peers (+6.9 [3.6, 10.5]). Among social peers it did not (−2.8 [−5.9, +0.5], 9/12 seeds negative), and trained agents attacked about twice as often. Removing theft (`steal=0`) changed nothing. Candidate, untested: the social agent's extra actions and sensors. | completed |
| **Why do social agents fail to learn?** (AA, [write-up](docs/research/FINDINGS_AA.md)) | **They freeze in hazards.** A social agent fails to learn even alone (+1.1 vs +13.9 for a non-social agent). Attack, share and signal do not move the body, and trained lone social agents attacked in 22% of ticks with no one around. Without hazards their learning pays (+6.2 [4.6, 7.7]) and uses the senses, though at about half the non-social gain. | completed |
| **Does removing hazards let social agents learn in groups?** (AB, [write-up](docs/research/FINDINGS_AB.md)) | **No.** Among 11 social peers without hazards, learning gave +0.3 [−2.2, 2.9], against +7.3 among non-social peers. Z replicated (−2.0 with hazards). Learning more than doubled the attack rate (0.07 → 0.16) even though, as Z showed, attacks need not pay for this to happen. | completed |
| **Does switching off the frustration drive let social agents learn in groups?** (AC, [write-up](docs/research/FINDINGS_AC.md)) | **No.** Without the frustration-to-attack drive, learning among 11 social peers gave +0.6 [−2.1, 3.6] (with it +0.4; non-social peers +10.3). Learning still raised the attack rate by the same amount (0.016 → 0.101). Learning raises frustration in every group, including non-social ones where it pays. A probe that switched the drive off only at test did not hold. | completed |
| **Which input weights carry the learned rise in attacks?** (AE, [write-up](docs/research/FINDINGS_AE.md)) | **The movement neurons'.** With only the movement inputs learning, the attack rate rose from 0.059 to 0.255 and learning lost food (−4.3); freezing the movement inputs removed the rise (0.024) and learning paid (+2.6 [1.7, 3.5]), though not more than learning everything (+3.5). The attack neurons need not learn for attacks to rise. | completed |
| **Does the shaping reward cause failed social learning?** (AF, [write-up](docs/research/FINDINGS_AF.md)) | **Yes.** Replacing alignment shaping with approach shaping turned the learning gain among 11 social peers from −1.1 to +4.9 [3.6, 6.1] (12/12 seeds positive) and removed the learned rise in attacks. Approach shaping is weak for a solo agent (+1.9), so neither shaping is best everywhere. | completed |

How C–R fit together (learned social behaviour as a side effect of the
learning rule) is summarised in
[`docs/research/SYNTHESIS_LEARNING_SIDE_EFFECT.md`](docs/research/SYNTHESIS_LEARNING_SIDE_EFFECT.md).

The full ranked agenda of open questions is in
[`docs/research/RESEARCH_AGENDA.md`](docs/research/RESEARCH_AGENDA.md).

## 🧩 How a decision is made

```
world ──► egocentric sensors ──► input currents ──► LIF spiking network
 ▲     food/threat ×3, hunger,      (nA)            sensory → action populations
 │     others ×3, heard signal                       (move / attack / share / signal)
 │                                                    with lateral inhibition
 │                                         most active population = action
 │                                                          ▼
 └── weights change ◄── reward-modulated ◄── reward prediction ◄── eat / hurt / steal / give
     (and genomes        Hebbian learning     error (TD)
      mutate across
      generations)
```

- The physics only moves bodies and does the energy bookkeeping. **It never
  picks an action.**
- Reward shaping is an explicit engineering choice.
- Affect is computed from the primary reward only.

## 🤖 For RL researchers

```python
from neuralmind.envs import parallel_env
env = parallel_env(n_rl=4, n_snn=4, config={"social": True}, max_cycles=500)
obs, infos = env.reset(seed=0)
while env.agents:
    obs, rewards, terms, truncs, infos = env.step(
        {a: env.action_space(a).sample() for a in env.agents})
```

- **Observations:** the sensor vector the SNN agents use.
- **Actions:** `Discrete` over move, plus attack / share / signal when social.
- **Rewards:** the same reward the SNN agents learn from.

## 🛠 Command-line tools

```bash
python -m neuralmind.research.spec studies/E_baldwin_vs_hiding.json   # run a registered study
python -m neuralmind.research.social all --seeds 10                    # lifetime social study
python -m neuralmind.research.evolution --experiment kin               # kin-selection study
python -m neuralmind.cli run reward_learning --seed 0                  # classic experiments
python -m neuralmind.bench --sizes 50 100 200 400                      # runtime + memory
python tools/make_media.py                                             # re-record these GIFs
python tools/build_site.py && python -m http.server -d site 8080       # the browser version, locally
```

## 📁 Project layout

```
neuralmind/
  core/          LIF neurons, synapses, STDP / eligibility traces
  affect/        reward prediction error, affect state
  world.py       2D world · Agent · social layer · evolution · genealogy
  envs/          PettingZoo ParallelEnv
  research/      pre-registered studies, stats (bootstrap CI, MI, G-test), spec runner
  playground.py  Playground API as plain Python (used by the server and by the browser build)
  lab.py         Discovery Lab API
  server.py      FastAPI backend (the browser only renders backend state)
  webui/         Playground (+ family tree) + Discovery Lab (vanilla JS + canvas, Kenney CC0 pixel art);
                 static-mode.js + pyodide-worker.js run it without a server (tools/build_site.py)
  paths.py       where studies/ and results/ live (repo, $NEURALMIND_HOME, or current folder)
studies/         registered study specs        results/   raw results + reports
docs/research/   findings, evidence ledger, agenda, literature
tests/           pytest suite (CI on 3.12 / 3.13)
```

## ⚠️ Known limitations

- Small brains: 31–59 neurons per agent, point-neuron LIF. This is not a model of any real nervous system.
- Within-lifetime learning alone does not produce targeted social behaviour (see findings).
- Evolution studies run for tens of generations, not thousands.
- A "day" is a simulation unit (`ticks_per_day`).

## Licence: free to use

You may use, copy, change, share and sell anything in this repository, including the
code, docs, study specs, results data and README media, for personal, research,
teaching or commercial work. You don't need to ask.

| What | Licence | What you must do |
|---|---|---|
| Code, docs, study specs, `results/` data, README GIFs/screenshots | [MIT](LICENSE) | Keep the copyright and licence notice in copies or substantial portions. Citation is welcome ([`CITATION.cff`](CITATION.cff)) but not required. |
| Pixel art in `neuralmind/webui/assets/kenney/`: [Tiny Town](https://kenney.nl/assets/tiny-town) and [Tiny Dungeon](https://kenney.nl/assets/tiny-dungeon) by **[Kenney](https://kenney.nl)** | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (public domain dedication) | Nothing. Credit is optional; we give it gladly. Don't imply Kenney endorses your project. |
| pip dependencies (NumPy, FastAPI, Uvicorn, PettingZoo, Gymnasium, …) | each package's own permissive licence (BSD, MIT, Apache-2.0) | Not included in this repo. You install them, under their own terms. |

Notes:

- The README GIFs and screenshots show Kenney's CC0 art, so they carry no extra restriction.
- The emoji in the UI (😠 💚 📢 …) are drawn by your operating system's emoji font.
  No emoji font or image is bundled.
- MIT and CC0 come with **no warranty**. This is a research model, not a medical or
  safety-critical tool.
- No copyleft (GPL) code is included. Copyleft simulators we studied for reference
  (Brian2, NEST, TVB) are listed in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)
  with the rules for using them alongside this repo.

The licence texts were checked against [kenney.nl](https://kenney.nl/assets/tiny-town),
the `License.txt` files shipped with the art, and the
[CC0 deed](https://creativecommons.org/publicdomain/zero/1.0/) in October 2026.
If you find an asset whose source or licence is unclear, please open an issue.

This repository started as AgentGraph, an LLM multi-agent app. That code was removed;
it is preserved at the git tag [`agentgraph-legacy`](https://github.com/sitta07/NeuralMind/tree/agentgraph-legacy).
