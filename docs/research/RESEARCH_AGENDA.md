# Research agenda — open, testable questions

This list is ranked by **scientific value × feasibility ÷ cost** on one laptop
(8 cores). Every entry names its falsifier. The status column is updated as
studies complete.

| # | Question | Why it is open | Prediction / falsifier | Cost | Status |
|---|---|---|---|---|---|
| 1 | Can social behaviour (aggression, sharing) be *learned within one lifetime* by reward-modulated spiking agents? | Few studies test social behaviour in biologically-plausible learners. | Pre-registered H1–H4 | ~1 min | **done: no** ([findings](FINDINGS_SOCIAL.md)) |
| 2 | **Does selfish lifetime learning undermine kin-selected helping?** | Kin selection theory (Hamilton; Taylor 1992) and the Baldwin effect are rarely put in tension. We found no study of this with spiking, plastic agents. | H5: viscosity raises innate share drive. H6: learning lowers realised sharing. H7: no kin-directed sharing without kin recognition. | ~15 min | running |
| 3 | Does a heritable aggression gene evolve upward under scarcity? | Resource-defence theory predicts aggression is highest at intermediate or clumped resources, not maximal scarcity. | Aggression gene: scarce vs abundant. Falsified if no difference or the reverse. | ~20 min | planned |
| 4 | Do signals evolve *meaning*? | Referential communication has emerged in evolved SNN swarms (arXiv 2212.08484). Whether it does under competition, not cooperation, is less clear. | Mutual information I(signal; signaller's food/threat sensors) > shuffled control; receivers change behaviour after hearing. | ~30 min | planned |
| 5 | Baldwin effect in spiking agents: does plasticity speed up the evolution of innate foraging? | A classic result (Hinton & Nowlan 1987). It has rarely been measured with reward-modulated STDP. | Innate foraging score vs generation: learning on vs off. Falsified if slopes are equal. | ~20 min | planned |
| 6 | Darwinian vs Lamarckian inheritance of learned weights. | Lamarckian inheritance is faster in static worlds but may be brittle in changing ones. | Adaptation after an environment shift. | ~20 min | planned |
| 7 | Can RL policies (PettingZoo) invade a population of SNN agents, and vice versa? | Mixed populations of hand-coded, learned and evolved controllers are rarely compared under identical rules. | Relative population share over time. | variable | infrastructure ready |

## Principles

- Pre-register the hypotheses and the falsifier before running.
- Multiple seeds, paired designs where possible, and 95% bootstrap CIs.
- Commit the raw results (`results/`) and the code version that produced them.
- Report negative results with the same care as positive ones.
