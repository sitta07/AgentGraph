# Literature check: which NeuralMind findings are already known?

Date of search: 2026-10-16. Scope: the findings in
`docs/research/SYNTHESIS_LEARNING_SIDE_EFFECT.md`, `RESEARCH_AGENDA.md`,
`FINDINGS_E.md`, `FINDINGS_F.md`, `FINDINGS_Q2.md`, `FINDINGS_Q3.md`,
`FINDINGS_N2.md` and `docs/GUIDE.md` sections 12–14.

How to read the status column:

- **known**: prior work reports the same effect or derives it in theory.
- **partly known**: the mechanism or a close analogue is published, but not
  in this form (for example, in theory but not in behaving agents, or in
  another kind of system).
- **not found in what we searched**: no matching report turned up in the
  searches listed at the end. That is a statement about the search, not a
  claim that the finding is new. The search was limited (see "Limits").

I opened every source cited below this session, at least its abstract page
or bibliographic record. Where I saw only metadata, or only a secondary
summary, the entry says so.

## Summary table

| # | Finding (ours) | Status | Closest prior work | What is different here |
|---|---|---|---|---|
| 1 | With one scalar reward expectation, R-STDP depresses the busiest input pathways (locomotion). Social actions then win the spike-count contest more often, so sharing roughly doubles and attacks rise about 10×, although nothing about them was rewarded (I, J, K, P) | **partly known** (the bias is known in theory; we found no report of it as a behavioural side effect) | Frémaux, Sprekeler & Gerstner 2010 derive the bias term ⟨S⟩⟨e_ij⟩ and show that R-STDP fails when the success signal is not specific to the stimulus. Skorheim et al. 2014 report that rewarded STDP in a foraging agent becomes unstable without synaptic balancing, with stereotypy-like behaviour | Prior work shows the bias as a failure to learn a target (single neurons, spike trains). Here it shows up as a measurable change in social behaviour in an embodied, evolving multi-agent population. The route also differs: the bias works through competition between action populations, not through the output of one neuron |
| 2 | A per-state critic removes 58–76% of the side effect (R) | **known** (it was predicted) | Frémaux et al. 2010 (Fig. 3C: a critic with a separate reward estimate per stimulus "rescues" R-STDP). Frémaux & Gerstner 2016: "The mean reward must be evaluated in a stimulus-specific fashion" | Ours is a confirmation in a new setting. The fix is only partial here (58–76%, foraging cost halved, not removed), so the critic is not the whole story |
| 3 | Updating only on positive reward errors reverses the drift: locomotion weights grow 73% and the social rise disappears (P) | **partly known** | Frémaux et al. 2010 Fig. 2B: the sign of the mean success offset decides whether the STDP bias or the anti-STDP bias dominates. Jordan et al. 2021 find that the baseline choice decides which weight configurations learning can escape | Prior work changes the offset in single-neuron tasks. Ours is an embodied behavioural test of the sign effect |
| 4 | "Learned" social behaviour was an artefact of the learning rule. It was not learned from the consequences of social actions (synthesis) | **partly known** as a general class of error | Galán et al. 2009 define an artefact as a result caused by an accessory assumption the modeller thought did not matter. Similar cases: Huberman & Glance 1993 (spatial cooperation depends on the update schedule); Galán & Izquierdo 2005 (Axelrod's norms result reverses with run length and parameters); Lowe et al. 2019 (communication metrics show "communication" that has no effect) | We found no case where social behaviour in plastic or spiking agents was traced to an unsupervised bias of a reward-modulated rule. The ablation chain (J, K, P, R) that isolates the mechanism is the main contribution |
| 5 | No learning rule tested makes lifetime learning pay. Learners eat 7–31% less than non-learners (P, R, T) | **partly known** | Skorheim et al. 2014: rewarded STDP alone is not enough without stabilising mechanisms. Paenke, Jin & Branke 2009 and Thomsen & Rasmussen 2023 show that whether learning pays depends on environmental change and learning cost | Expected for a static world. That learning *lowers* food intake, not only fails to raise it, follows from the bias in finding 1 |
| 6 | Hiding effect: with learning, innate foraging evolves less (E) | **known** as a phenomenon; the route here is unusual | Mayley's "hiding effect" (1997, cited by later work; we did not open the original). Paenke, Sendhoff & Kawecki 2007 give a general condition: plasticity slows evolution when it flattens the slope from genotype to log fitness. Hinton & Nowlan 1987 for the opposite (Baldwin) case | In the classic hiding effect, learning *helps* weak genotypes catch up. Here learning on average *lowers* foraging (finding 5), yet innate foraging still evolves less. It may be noise or flattening (Paenke's framework) rather than compensation. That has not been tested |
| 7 | Lamarckian inheritance of learned weights: 9/12 populations extinct vs 1/12 Darwinian. Early birth rate about 3× higher. The per-state critic does not prevent it (N, N2) | **partly known** (Lamarckian brittleness is reported; collapse of a whole population in a static world was not found) | Sasaki & Tokoro 1999: populations with lower inheritance of acquired characters are more stable under environmental change. de Bruin et al. 2026: Lamarckian inheritance does worse only when changes are conflicting and unpredictable. Luo et al. 2023/2024: Lamarckian inheritance does *better* in robot evolution. Rauch, Sayama & Bar-Yam 2002: fast-reproducing lineages go extinct through local overexploitation | Prior work measures fitness or adaptation speed, mostly in changing environments, in single-agent or non-interacting settings. Ours is extinction of a whole interacting population in a *static* world, after a reproductive boom. We found no report of that |
| 8 | Viscous offspring placement delays extinction (F, F2: pooled fresh seeds 17/22 vs 7/22, post hoc) | **partly known** | Kerr et al. 2006 (restricted migration favours restraint, a "tragedy of the commons" avoided). Werfel & Bar-Yam 2004 (local spreading makes selfish exploiters drive themselves extinct). Rauch et al. 2002. Rankin, Bargum & Kokko 2007 (review of tragedies of the commons and extinction) | These are host–pathogen or abstract models. Ours shows the same direction in a neural-agent ecology, but we have not shown that restraint evolves. The mechanism is still open |
| 9 | Newborns placed beside a stranger: 34/36 extinct vs 13/36 beside the parent (Q–Q3). Parents commit 42% of kills (on their own offspring) in viscous worlds. Energy recycling does not explain the benefit (Q3) | **not found in what we searched** (as a specific result) | The theory of relatedness versus local competition between kin: Taylor 1992; Wilson, Pollock & Dugatkin 1992; Queller 1992; West, Pen & Griffin 2002. The experimental separation of relatedness and scale of competition: Griffin, West & Buckling 2004 | That theory is about the *evolution of altruism*. Our result is about *population persistence*, and "stranger" placement keeps local density while breaking local kinship. We did not find this manipulation in neural-agent or individual-based work. Filial killing as a large share of kills was not found in the models we looked at |
| 10 | Signals carry no meaning (M, S), even when food needs a partner | **partly known** (a null result in a setting where theory expects one) | Mitri, Floreano & Keller 2009 (competing robots suppress information). Floreano et al. 2007 (communication evolves with high relatedness and colony-level selection; deception evolves under individual selection). Lowe et al. 2019 on measurement | Consistent with that work: our selection is individual-level, with competition for food |

## 1. The R-STDP bias, and whether it causes behavioural side effects

**Established evidence (theory and single-neuron simulation).**

- Frémaux, Sprekeler & Gerstner (2010) split the average weight change into
  two terms: a covariance term and ⟨S(R)⟩⟨e_ij⟩. The second term is "an
  unsupervised bias to the weight dynamics". The mean success signal ("success
  offset") sets the trade-off between the two. Offsets of about 25% of the
  success signal's SD are enough to stop R-STDP from learning. Below
  −0.4 σ_R, "R-STDP not only fails to learn the task, but sometimes even
  leads to unlearning". With two stimuli and one running-average baseline,
  learning works only while the two mean rewards happen to match: "as soon as
  a minor discrepancy in mean reward appears … performance drops to
  prelearning level". A critic that keeps a separate mean per stimulus
  rescues it (Fig. 3). R-max, whose eligibility trace has zero mean, does not
  have the bias. Read from the EPFL PDF.
  doi:10.1523/JNEUROSCI.6249-09.2010,
  https://infoscience.epfl.ch/record/153015
- Frémaux & Gerstner (2016), a review: the neuromodulator should signal
  "actual reward minus expected reward". "The mean reward must be evaluated in
  a stimulus-specific fashion". If the baseline is wrong, "the learning rule
  does not function properly as a reward-based learning rule". They also note
  that Izhikevich's gating keeps the Hebbian term slightly negative, which
  produces a downward drift of all weights. doi:10.3389/fncir.2015.00085,
  https://www.frontiersin.org/articles/10.3389/fncir.2015.00085/full
- Legenstein, Pecevski & Maass (2008) define the reward signal as zero-mean.
  They note that all synapses are depressed by the negative part of the STDP
  window, and that weights can grow without bound, so they clip them.
  doi:10.1371/journal.pcbi.1000180,
  https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000180
- Izhikevich (2007): dopamine-gated STDP with eligibility traces solves the
  distal reward problem. Abstract page opened. doi:10.1093/cercor/bhl152,
  https://academic.oup.com/cercor/article/17/10/2443/314939
- Florian (2007): reward-modulated STDP derived from a policy-gradient rule,
  with and without eligibility traces. Europe PMC record opened.
  doi:10.1162/neco.2007.19.6.1468
- Greensmith, Bartlett & Baxter (2004): in policy-gradient learning a
  baseline changes the variance but not the expected gradient, and the average
  reward baseline can be suboptimal. That is why the bias appears only for
  rules whose eligibility trace has a non-zero mean, as Frémaux et al. point
  out. https://jmlr.org/papers/v5/greensmith04a.html

**Closest behavioural or embodied precedents.**

- Skorheim, Lonjers & Bazhenov (2014), a spiking foraging agent with rewarded
  STDP: "Rewarded STDP is homeostatically unbalanced". Without input
  balancing, "the network quickly became unstable and the virtual entity moved
  in random or repetitive circles". In a biased environment it over-learned a
  few responses, which they compare to motor stereotypies. They do not analyse
  the reward baseline. doi:10.1371/journal.pone.0090821 (full text read via
  Europe PMC)
- Vassiliades, Cleanthous & Christodoulou (2011): R-STDP spiking agents in
  the iterated prisoner's dilemma. The level of cooperation depended on the
  eligibility-trace time constant. The authors added global reinforcement
  signals "to prevent synaptic saturation" when output neurons compete. This
  shows details of the learning rule shaping a social outcome, but not the
  baseline bias. doi:10.1109/TNN.2011.2111384 (announcement and abstract:
  https://mailman.srv.cs.cmu.edu/pipermail/connectionists/2011-April/024464.html)
- Jordan, Schmidt, Senn & Petrovici (arXiv 2005.14149, eLife 2021) evolved
  plasticity rules for spiking reinforcement learning. Rules that use the
  expected reward as the baseline did badly: the agent can get stuck receiving
  negative rewards that it already expects. The best rules used optimistic
  baselines that learn mainly from negative rewards. This is the opposite
  choice to our `pos_only` arm (P), which shows that the best baseline depends
  on the task. https://arxiv.org/abs/2005.14149
- Evans (2015), a dopamine-modulated STDP robot that learns and unlearns food
  attraction. The abstract reports no side effects.
  https://arxiv.org/abs/1502.06096

**What is different here (hypothesis, not established).** Our mechanism is
the multi-stimulus case of Frémaux et al. (their Fig. 3B), spread over many
sensor states. Locomotion inputs have the largest mean eligibility and are
most active in states with below-average reward, so they take most of the
negative bias. Because actions are chosen by a contest between populations,
weakening one population changes how often the others are chosen. We found
no paper that reports this route from the R-STDP bias to a change in social
behaviour. Two caveats:

- The step "58% of reward errors are negative, and locomotion has 8× the
  eligibility" rests on an exploratory probe that was not pre-registered.
- We did not compute Frémaux's decomposition (per-pathway ⟨S⟩ × ⟨e⟩)
  directly. See next experiment 1.

## 2. Emergent social behaviour later traced to an artefact

**Established evidence.**

- Galán et al. (2009) define an artefact as a significant result caused by
  an accessory assumption, one included only to make the model run, that the
  developer wrongly thinks does not matter. The scalar critic fits this
  definition: it was an implementation choice that turned out to drive the
  social result. https://www.jasss.org/12/1/1.html
- Galán & Izquierdo (2005) re-implemented Axelrod's evolution of norms. Longer
  runs, a different mutation rate, different payoffs or a different selection
  method reversed the result. https://www.jasss.org/8/3/2.html
- Huberman & Glance (1993): results on "territoriality and cooperation"
  differ greatly when time is discrete rather than continuous, an artefact of
  the update schedule. doi:10.1073/pnas.90.16.7716,
  https://arxiv.org/abs/chao-dyn/9307017
- Lowe et al. (2019): agents whose messages predict their own actions appear
  to communicate, but the messages have no effect on the other agent. This is
  a measurement artefact found by ablation. https://arxiv.org/abs/1903.05168
- Lehman et al. (2020): a collection of cases where digital evolution
  exploited bugs or loopholes. https://arxiv.org/abs/1803.03453
- Leibo et al. (2017): in independent deep-Q learners, aggression ("tagging")
  depends on resource abundance. This is a contrast case: there the
  aggression is a learned, reward-driven response to scarcity.
  https://arxiv.org/abs/1702.03037

**Gap.** The examples above are about update schedules, parameters, run
length or metrics. We found none where social behaviour in plastic or
spiking agents was traced to an unsupervised bias of the plasticity rule. We
also did not search the ALife conference proceedings exhaustively.

## 3. Evolution of altruism, aggression and communication in embodied agents

- Waibel, Floreano & Keller (2011): simulated foraging robots. Hamilton's rule
  predicted the minimum relatedness needed for altruism in every
  cost/benefit condition. doi:10.1371/journal.pbio.1000615 (Europe PMC
  record). The abstract does not say whether the controllers were plastic, and
  I did not check the full text.
- Floreano, Mitri, Magnenat & Keller (2007): communication evolved readily
  with high relatedness and colony-level selection. Deceptive signalling
  evolved under individual-level selection with unrelated robots.
  doi:10.1016/j.cub.2007.01.058
- Mitri, Floreano & Keller (2009): competing robots evolved to suppress the
  information in their light emissions. Suppression stayed incomplete, because
  selection weakened as the information content fell.
  doi:10.1073/pnas.0903152106
- Burtsev & Turchin (2006): agents with simple neural nets evolved hawk, dove,
  bourgeois and new cooperative attack/defence strategies.
  doi:10.1038/nature04470,
  https://ideas.repec.org/a/nat/nature/v440y2006i7087d10.1038_nature04470.html
- Dridi & Akçay (2018): reinforcement learners whose subjective rewards evolve.
  Conditional-cooperation rewards are evolutionarily stable, and selfish
  always-defect learners also succeed. doi:10.1086/694822, preprint
  https://www.biorxiv.org/content/10.1101/074096v2
- Hermsen (2022): altruists self-organise into colonies that act as units of
  selection. Defectors win inside each colony, but altruism persists through
  colony turnover. doi:10.1371/journal.pcbi.1010612
- PolyWorld (Yaeger, Artificial Life III, 1994): agents with Hebbian synapses
  that eat, mate and fight. **Only a secondary description was opened**
  (https://cs.tau.ac.il/~ruppin/ALseminar/naphtali.html), so it is not used
  as evidence here.

**Bearing on our work.** Our failure to find meaningful signals (M, S) and
the absence of learned targeting match the robot results: communication
needs relatedness or group-level selection, and competition favours
suppression. We found no study in this group that combines reward-modulated
lifetime plasticity with kin structure and asks whether learning raises or
lowers helping (agenda item 2). Dridi & Akçay is the closest, but it uses
abstract repeated games.

## 4. Baldwin effect vs hiding effect

- Hinton & Nowlan (1987): learning speeds up the evolution of a needle-in-a-
  haystack genotype. https://www.cs.toronto.edu/~hinton/absps/evolution.htm
- Mayley (1996, CSRP 409, "No pain, no gain"): genetic assimilation needs a
  cost of learning and correlation between neighbourhoods in genotype and
  phenotype space.
  https://www.sussex.ac.uk/informatics/cogslib/reports/csrp/csrp409.pdf
- Mayley (1997, ECAL, "Guiding or hiding"), where the term "hiding effect"
  comes from: **I did not find or open the original.** It is cited here only
  as the source of the term.
- Paenke, Sendhoff & Kawecki (2007): plasticity speeds evolution when the
  "fitness gain gradient" has the same sign as the direction of selection, and
  slows it when the signs are opposite. This covers developmental noise as
  well as learning. doi:10.1086/518952
- Frank (2011): non-heritable developmental variability can *speed* evolution
  by smoothing the genotype–fitness landscape.
  https://arxiv.org/abs/1109.5633

**Status.** The hiding effect itself is known. What may be unusual in E is
that learning on average lowers foraging (P: −31%), yet still reduces the
evolution of innate foraging. The classic story is that learning lets weak
genotypes catch up. An alternative that fits Paenke et al. is that learning
adds variance or flattens the slope from innate wiring to fitness. A second
confound is that E's assay runs genomes with learning switched off, so
genomes adapted to *living with* the learning drift may score poorly for
that reason. Neither alternative has been tested.

## 5. Lamarckian inheritance and population collapse

- Sasaki & Tokoro (1999): learning neural agents (food vs poison) with
  different rates of inheritance of acquired characters. Lower inheritance
  gives more stable populations under environmental change. The Darwinian
  population adapts best to dynamic environments. doi:10.1162/106454699568746
  (Crossref record with abstract)
- de Bruin, Glette & Ellefsen (2026): Lamarckian inheritance does worse than
  Darwinian only when changes both conflict with control and are
  unpredictable. https://arxiv.org/abs/2605.15769
- Luo et al. (2024, 2023): Lamarckian inheritance improves evolution of
  modular robots, including in dynamic environments.
  https://arxiv.org/abs/2403.19545, https://arxiv.org/abs/2309.13099
- Thomsen & Rasmussen (2023): an agent-based comparison of Darwinian,
  Baldwinian and Lamarckian strategies. Lamarckian strategies win at low
  learning cost. https://arxiv.org/abs/2305.00491
- Curran & O'Sullivan (ECAL 2009): a proof that Lamarckian inheritance can
  dominate individual learning under some conditions.
  https://research.ucc.ie/en/publications/an-analysis-of-lamarckian-learning-in-changing-environments/
- Rauch, Sayama & Bar-Yam (2002): in spatial host–pathogen models, mutants
  with high reproduction go extinct through local overexploitation. Mean
  offspring number is a poor measure of fitness there.
  https://necsi.edu/relationship-between-measures-of-fitness-and-time-scale-in-evolution

**Status.** Prior work compares adaptation speed or fitness, mostly in
changing environments, and the results go both ways. We found no report of
Lamarckian inheritance causing *population extinction* in a *static* world
of interacting agents. N2's pattern (boom: birth rate about 3× higher, then
collapse) resembles the overexploitation route in Rauch et al. Two candidate
explanations are untested:

- learned drift accumulates across generations;
- populations converge quickly and lose diversity.

The literature has general claims that Lamarckian search causes premature
convergence, but I did not open a primary source that shows it, so none is
cited.

## 6. Population viscosity, dispersal and persistence

**Theory of altruism under viscosity (established).**

- Taylor (1992): in a patch-structured, inclusive-fitness model, more
  cooperation with relatives and more competition with relatives cancel
  exactly. I opened only the Crossref metadata. The content is as summarised
  in the abstracts of Lehmann et al. 2008 and Kanwal & Gardner 2022, which I
  did open. doi:10.1007/BF02270971
- Wilson, Pollock & Dugatkin (1992), "Can altruism evolve in purely viscous
  populations?" Crossref metadata only. doi:10.1007/BF02270969
- Queller (1992), "Does population viscosity promote kin selection?"
  Crossref metadata only. doi:10.1016/0169-5347(92)90120-Z
- West, Pen & Griffin (2002): competition between relatives can reduce or
  cancel the kin-selected benefits of altruism.
  https://era.ed.ac.uk/handle/1842/473
- Lehmann, Ravigné & Keller (2008), doi:10.1098/rspb.2008.0276, and Kanwal &
  Gardner (2022), doi:10.1098/rspb.2021.2668: the cancellation breaks down
  under other life cycles or density-dependent dispersal.
- Le Galliard, Ferrière & Dieckmann (2005): habitat saturation mediates the
  joint evolution of altruism and mobility. doi:10.1086/427090

**Persistence and extinction (closest to F/Q).**

- Kerr et al. (2006): with spatially restricted migration, prudent phage win.
  With unrestricted migration, rapacious phage evolve and productivity falls.
  doi:10.1038/nature04864
- Werfel & Bar-Yam (2004): with local spreading, selfish exploiters drive
  themselves extinct, and signalled reproductive restraint evolves.
  https://necsi.edu/the-evolution-of-reproductive-restraint-through-social-communication
- Rankin, Bargum & Kokko (2007): a review of tragedies of the commons,
  including extinction through individual-level selection.
  doi:10.1016/j.tree.2007.07.009, https://eprints.gla.ac.uk/11211. Also
  Rankin, López-Sepulcre, Foster & Kokko (2007, J. Evol. Biol.): aggression
  and selfishness can lower population size and lead to extinction.
  doi:10.1111/j.1420-9101.2007.01337.x
- Gyllenberg, Parvinen & Dieckmann (2002): dispersal can evolve to a level
  that causes extinction (evolutionary suicide). Crossref metadata opened;
  the content comes from the search-engine summary of the abstract.
  doi:10.1007/s002850200151
- Griffin, West & Buckling (2004): relatedness and the scale of competition
  were varied independently. Relatedness raised cooperation, more local
  competition lowered it, and the two interacted. doi:10.1038/nature02744

**Status.** The direction of F/F2 (viscosity delays extinction) matches
known host–pathogen and individual-based results, so it is partly known.
Q–Q3 separate kinship from local density by placing newborns beside a
stranger. This is the same logic as Griffin et al. (2004), applied to
persistence rather than to the evolution of a trait. We did not find this
manipulation, or its 34/36 vs 13/36 outcome, in neural-agent or
individual-based work. In the theory above, a parent killing its own
offspring is an extreme case of local competition between kin. We found no
model in which that makes up a large share of kills.

## Suggested next experiments (most informative per the literature)

1. **Test the Frémaux decomposition directly, then remove the bias at its
   source.** For each pathway, log the success signal and eligibility over a
   lifetime. Predict each pathway's weight drift from the per-state product
   ⟨S | state⟩⟨e_ij | state⟩, and pre-register the predicted drift ratio
   between locomotion and social inputs. Then add an arm whose eligibility
   trace has zero mean (for example, subtract each synapse's running mean
   eligibility, which is the property that makes R-max insensitive to the
   success offset), keeping the scalar critic. Prediction: the social rise
   disappears even with the scalar critic. Falsifier: the social rise stays
   when ⟨e⟩ ≈ 0. Source: Frémaux, Sprekeler & Gerstner 2010 (Eq. 17, Fig. 2–3).
2. **Measure Paenke's fitness gain gradient instead of inferring hiding.**
   Take a panel of genomes from E with innate foraging scores spread out. Run
   each with learning on and off in the same social world. Regress log
   lifetime reproduction on innate score. Hiding predicts a shallower slope
   with learning on. Also test the evolved genomes *with* learning on, to
   separate hiding from assay mismatch. Source: Paenke, Sendhoff & Kawecki
   2007.
3. **A 2×2 that separates relatedness from the scale of competition.**
   Factor 1: newborn placement (beside the parent vs beside a stranger).
   Factor 2: scale of competition (food regrows where it was eaten vs food is
   redistributed globally). Also log the spatial clustering of lineages and
   local food depletion before collapse. Kin theory predicts an interaction:
   placement matters less when competition is global. The overexploitation
   account (Rauch et al. 2002; Kerr et al. 2006) predicts that high-birth-rate
   lineages deplete their patch first. Source: Griffin, West & Buckling 2004.
   For N2, the same logging plus an inheritance-rate continuum (0, 0.25, 0.5,
   1) follows Sasaki & Tokoro 1999.

## What we searched

Tools: a web search engine (standard and extended modes) and direct page
fetches. Databases and pages used: Europe PMC REST API (abstracts and some
full texts), Crossref API (metadata), arXiv abstract pages, publisher pages
(PLoS, Frontiers, OUP, JMLR, JASSS, NECSI, RePEc), the EPFL Infoscience PDF
of Frémaux et al. 2010, and university repositories (Edinburgh, Glasgow,
Sussex, UCC). PubMed Central, Springer, MIT Press and IEEE pages blocked
automated access. For those, Europe PMC or Crossref was used instead.

Queries (abridged):

- Frémaux Sprekeler Gerstner 2010 functional requirements reward-modulated STDP
- Legenstein Pecevski Maass 2008; Izhikevich 2007 distal reward; Florian 2007; Frémaux Gerstner 2016 three-factor
- reward-modulated STDP unsupervised bias weight drift action selection embodied agent side effect
- reward-modulated STDP robot foraging spiking multi-agent evolution reward baseline failure
- "three-factor" learning rule spurious bias reward prediction error not stimulus specific behaviour drift agents
- spiking agent reward-modulated plasticity action selection frequent action pathway negative RPE homeostasis
- state-dependent vs scalar baseline, policy gradient bias
- Vassiliades Cleanthous Christodoulou spiking IPD; Bing/Knoll R-STDP robot; Soltoggio neuromodulated plasticity
- artificial life emergent cooperation artefact of learning algorithm; null model emergent sharing; evolved plastic agents aggression side effect
- Lehman surprising creativity; Huberman Glance 1993; Galán Izquierdo 2005; Galán et al. 2009; Lowe et al. 2019; Leibo 2017; Q-learning IPD initialization artefact
- Waibel Floreano Keller 2011; Mitri et al. 2009; Floreano et al. 2007; Burtsev Turchin 2006; Avida kin selection; PolyWorld; Dridi Akçay; Ackley Littman
- Mayley 1996/1997; Paenke 2007; Frank 2011 developmental variability; Baldwin effect spiking R-STDP
- Lamarckian inheritance learned weights collapse / brittle / diversity; Sasaki Tokoro; Whitley 1994; Ku Mak Siu; Paenke Jin Branke 2009
- Taylor 1992; West Pen Griffin 2002; Queller 1992; Wilson Pollock Dugatkin 1992; Mitteldorf Wilson 2000; Kerr 2006; Rankin Kokko 2007; Gyllenberg 2002; Werfel Bar-Yam 2004; Rauch Sayama Bar-Yam 2002; Griffin West Buckling 2004; Le Galliard 2005; filial infanticide viscous models

## Limits of this search

- It was one session of web searching, not a systematic review. No Google
  Scholar, Web of Science or Scopus. No forward-citation search on Frémaux et
  al. 2010, which is the most likely place to find a prior behavioural report
  of finding 1. That is the main gap.
- ALife and ECAL proceedings, GECCO, and neuromorphic robotics venues were
  searched only through the general search engine.
- Several sources were read at abstract level only. For Taylor 1992, Wilson
  et al. 1992, Queller 1992 and Gyllenberg et al. 2002 only metadata was
  opened. Mayley 1997 and PolyWorld (1994) were not opened, so nothing rests
  on them.
- Some candidate sources were not verified and are deliberately left out:
  Paenke et al. ECAL 2007 on the "adaptive disadvantage of Lamarckianism",
  Whitley et al. 1994, Ku, Mak & Siu 2000, Mitteldorf & Wilson 2000, and
  Ackley & Littman 1994.
- The page summaries come from an automated reader, which can miss or
  paraphrase details. Direct quotes from Frémaux et al. 2010, Jordan et al.
  and Mayley 1996 were checked against PDF text extracted locally.
- "Not found in what we searched" means only that. A focused search by
  someone in theoretical neuroscience or social evolution could turn up prior
  reports.
