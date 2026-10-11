# NeuralMind — Scientific Evidence and Limitations

This document separates **(E) established biological/computational findings**,
**(H) hypotheses still debated in the field**, and **(A) engineering
abstractions** we adopt for tractability. Every mechanism in the code links back
to an entry here. Nothing in NeuralMind should be read as a claim of
consciousness, sentience, or subjective experience.

## 1. Leaky integrate-and-fire (LIF) neuron — `core/neurons.py`
- **(E)** The LIF neuron is a standard reduced model of a spiking neuron; its
  subthreshold `tau_m dV/dt = -(V - V_rest) + R I` dynamics and threshold-reset
  behaviour are textbook (Gerstner & Kistler 2002, *Spiking Neuron Models*;
  Tuckwell 1988; Lapicque 1907).
- **(A)** Point neuron (no morphology), current-based input, fixed hard
  threshold, no spike-frequency adaptation, forward-Euler integration with a
  `dt <= tau_m` stability guard. These are simplifications, not biology.

## 2. Spike-timing-dependent plasticity (STDP) — `core/plasticity.py`
- **(E)** Synaptic strength depends on the relative timing of pre- and
  post-synaptic spikes, with potentiation for pre→post and depression for
  post→pre over ~tens of ms (Bi & Poo 1998, *J. Neurosci.* 18:10464). The
  decaying-trace implementation follows Song, Miller & Abbott (2000, *Nat.
  Neurosci.* 3:919) and the review by Morrison, Diesmann & Gerstner (2008).
- **(A)** We use **pair-based** STDP with additive updates and hard weight
  bounds — not triplet STDP (Pfister & Gerstner 2006) or weight-dependent rules.

## 3. Reward-modulated (three-factor) plasticity — `core/plasticity.py`, `network.apply_reward`
- **(E/H)** Combining a local STDP eligibility trace with a global neuromodulatory
  signal ("three-factor learning") is a well-developed theory (Izhikevich 2007,
  *Cereb. Cortex* 17:2443; Frémaux & Gerstner 2016, *Front. Neural Circuits*).
- **(A)** Our eligibility trace is a simple exponentially-decaying accumulator;
  the modulator is applied at trial end. This is a minimal instance of the idea,
  not a detailed dopamine-system model.

## 4. Temporal-difference RPE — `affect/reward.py`
- **(E)** TD learning and the reward prediction error `δ = r + γV(s') − V(s)`
  are established in reinforcement learning (Sutton 1988; Sutton & Barto 2018).
- **(H)** The identification of phasic **dopamine** with the TD **RPE**
  (Schultz, Dayan & Montague 1997, *Science* 275:1593) is highly influential but
  remains debated and refined. We treat `δ` purely as a learning signal and do
  **not** claim it *is* dopamine.

## 5. Affect state — `affect/affect_state.py`
- **(E)** The **circumplex / core-affect** model represents affect along
  **valence** and **arousal** axes (Russell 1980, *J. Pers. Soc. Psychol.*
  39:1161; Posner, Russell & Peterson 2005).
- **(H)** Associating **threat** processing with amygdala circuits (LeDoux 2000,
  *Annu. Rev. Neurosci.* 23:155) and **frustration** with reward omission
  (Amsel 1992) is supported but simplified; we do **not** assign brain regions
  to variables in code.
- **(A)** `valence`, `arousal`, `threat`, `frustration`, `motivation` are
  **bounded leaky-integrator variables with hand-chosen gains**. They are
  candidate modelling constructs, **not** measured quantities and **not**
  subjective feelings. Units are dimensionless model quantities.

## 6. Experiments
- **Reward learning** (`experiments/reward_learning.py`): a **qualitative** RL
  prediction (reward shifts choice above chance). Validated against that
  qualitative expectation and an explicit `learning=False` baseline — **not**
  calibrated to any biological dataset.
- **Threat avoidance** (`experiments/threat_avoidance.py`): abstracted Pavlovian
  conditioning; the **paired > unpaired** associative-gain contrast is the
  qualitative hallmark of associative learning. No biological magnitude claimed.
- Future experiments (pain-related input, social attachment, memory under
  stress, forgetting/interference) will be added as **exploratory** unless a
  validated expected result exists, per acceptance criterion 15.

## What NeuralMind does NOT establish
- It does not demonstrate subjective pain, fear, love, or any felt experience.
- It does not model a complete human (or any real) brain or connectome.
- Its parameters are illustrative; qualitative, not quantitative, biology.
