# Synthesis: "learned" social behaviour was a side effect of the learning rule (C → R)

This page collects one line of work across nine experiments. Each experiment
has its own write-up. The numbers below are copied from those write-ups and
are not new analyses.

## The original observation

In C (2026-10-12), agents that learned during their lifetime shared about
**twice as often** as agents with fixed, evolved wiring. Later runs (E, G)
showed they also attacked about 10× as often. The reward was selfish. We had predicted that learning
would *lower* sharing ([C](FINDINGS_EVOLUTION_KIN.md)). The effect replicated
in C2, E and G.

## Explanations that were ruled out, or explained only part of it

| Explanation | Test | Outcome |
|---|---|---|
| Learners meet more neighbours (crowding) | C2, H9: condition on a neighbour in reach | the effect is 100.6% of the unconditional one, so crowding is **ruled out** ([C2](FINDINGS_C2.md)) |
| Gifts reward the receiver, which reinforces sharing (a reciprocity loop) | G: remove the gift reward | explains **≈22%** ([G](FINDINGS_G.md)) |
| One global reward strengthens every social action, rewarded or not | I: credit only the executed action | removes about half of the signalling rise and **none** of the attack rise ([I](FINDINGS_I.md)) |

## What the weights showed

In I, every input weight **fell** over a lifetime, and locomotion weights fell
the most (−3.2% vs −0.4 to −1.1% for the social actions). Agents choose an
action by a spike-count competition between action populations. So if the
locomotion populations weaken, social actions win more often even though
nothing about them was learned.

## Causal tests

| Experiment | Intervention | Share of the learned social rise removed |
|---|---|---|
| [J](FINDINGS_J.md) | freeze locomotion input weights | all of it (social rates at no-learning level) |
| [K](FINDINGS_K.md) | let locomotion learn, but hold each neuron's total input fixed | 80–95% |
| [P](FINDINGS_P.md) | skip weight updates with a negative reward error | all of it (locomotion weights then *grow* by 73%) |
| [R](FINDINGS_R.md) | keep the reward expectation per sensor state (Frémaux et al. 2010) | 58–76% |

## The mechanism, as far as tested

1. The critic keeps a **single scalar** reward expectation. In a world where
   reward depends strongly on the situation, about 58% of reward errors are
   negative (exploratory probe, [K](FINDINGS_K.md)).
2. Reward-modulated STDP multiplies the reward error by the eligibility
   trace. The busiest pathways, which are the locomotion inputs, have about
   8× the eligibility of the social ones. So they absorb most of the
   depression.
3. Locomotion weakens. Social action populations win the spike-count
   competition more often, so attacking, signalling and sharing rise.
4. Frémaux, Sprekeler & Gerstner (2010) describe this bias term for R-STDP.
   They show it disappears when the expectation is subtracted per stimulus.
   R confirms that a per-state critic removes most of the effect here.

Steps 1–2 rest on an exploratory probe (`drift_probe.py`). Steps 3–4 are
supported by pre-registered tests (J, K, P, R).

## Consequences

- **Learning costs foraging.** In P, learners ate ~31% less than
  non-learners. With the per-state critic the cost was ~14% (R, T). In
  [T](FINDINGS_T.md), adding chosen-only credit or a 4× lower learning rate
  narrowed it further, to −12% and −7%, but no rule tested makes lifetime
  learning pay. So far, less learning is always better in these worlds.
- **Hiding effect.** With learning, innate foraging evolves less
  ([E](FINDINGS_E.md)). In R this gap looked smaller with the per-state
  critic. That observation was not pre-registered and did not replicate in T.
- **Lamarckian inheritance** collapses populations, 9/12 vs 1/12 extinct
  ([N2](FINDINGS_N2.md)). The per-state critic does not prevent it, so that
  collapse needs a different explanation.
- **Earlier claims to re-read.** Statements before J that agents "learn to
  share" or "learn aggression" should be read as side effects of the
  learning rule. They were not learned from the consequences of social
  actions.

## What is still open

- Whether lifetime learning can pay at all here. It probably needs a world
  that changes within a lifetime in a way that hurts fixed wiring. N and N3
  did not achieve that (agenda item 16).
- Whether the side effect matters for kin-directed sharing. The kin bias in
  C and C2 is larger with learning, and it has not been re-tested with the
  per-state critic.
