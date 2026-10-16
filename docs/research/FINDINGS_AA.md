# Findings: Experiment AA — social agents fail to learn because they freeze in hazards

**Status:** completed 2026-10-17. 48 runs: 4 conditions × 12 training seeds
(850–861), each agent tested on 16 held-out worlds (9400–9415). Seeds and
worlds had never been run. Single agents, W "full" dynamics, 1500 training
ticks. Pre-registered at commit `26791d3`, spec unchanged, no deviations.
Two pilots preceded registration (seeds 720–725 and 740–743). One pilot
figure in the registered background has a typo: the lone non-social agent's
mean trained food was 15.5, not 15.25. Run time 22 min.
Report: [`results/AA_social_body/`](../../results/AA_social_body/REPORT.md).

**Question.** In [Z](FINDINGS_Z.md), learning failed among social peers.
A pilot then showed that a social agent fails even alone, where its social
sensors read zero. A trace showed it entering a hazard and staying there,
turning and attacking, until it died. Attack, share and signal do not move
the body. Is the hazard the problem?

| Hypothesis | Test | Result |
|---|---|---|
| H46a: without hazards, a lone social agent's learning pays | +6.2 [4.6, 7.7] food per episode | **supported** |
| H46b: removing hazards raises its learning gain | +5.1 [3.5, 6.6] | **supported** |
| H46c: with hazards, it gains less than a lone non-social agent | −12.8 [−14.0, −11.5] | **supported** |
| H46d: without hazards, it still gains less | −4.9 [−6.9, −3.3] | **supported** |

**By the pre-registered rule (H46a, b and d supported), hazards explain most
of the social agent's failure, and the social body impairs learning beyond
that.**

| condition | trained | trained, scrambled senses | untrained | learning gain | attack rate (trained) |
|---|---|---|---|---|---|
| solo, hazards | 15.9 | 3.1 | 2.0 | +13.9 | — |
| social alone, hazards | 2.1 | 1.8 | 1.0 | +1.1 | 0.22 |
| solo, no hazards | 16.4 | 4.8 | 5.2 | +11.2 | — |
| social alone, no hazards | 10.2 | 3.5 | 4.0 | +6.2 | 0.07 |

## Interpretation

- **The hazard trap.** With hazards, a trained lone social agent attacked
  in 22% of ticks, with no one to attack. Without hazards it attacked in 7%.
  The traced agent attacked while standing in a hazard. A plausible chain,
  not yet measured step by step: inside a hazard the hazard sensors fire,
  punishment weakens whichever movement pathway was active, and an action
  that does not move the body can win the decision. The agent then stays
  in the hazard and keeps being punished.
- **Without hazards, learning pays for the social agent too,** and the gain
  depends on the senses (10.2 real vs 3.5 scrambled). It is about half the
  non-social gain. Turns are also movements, but attack, share and signal
  are not, so a social agent covers less ground per tick.
- **This connects Z and X.** Social agents in groups and in evolving
  populations have the same body, so the same trap may operate there. That
  has not been tested in groups.
- This is a property of the agent design (3 of 6 actions do not move), not a
  general claim about spiking networks or social learning.

## Limits

- Single agents only. The trap is inferred from attack rates and one trace,
  not from a measured time-in-hazard.
- Hazards were removed entirely; hazard strength was not varied.

## Next step

Make the social actions also carry the agent forward (or make hazards push
agents out) and test whether learning then pays in social groups (Z design)
and in evolving populations (X design).
