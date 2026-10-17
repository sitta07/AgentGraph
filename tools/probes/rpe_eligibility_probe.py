"""Why does weight move to silent sensors? Log, per decision of agent 0, the
RPE and its eligibility summed over all input synapses."""
import numpy as np
from neuralmind import world as W
FULL = {"substeps": 32, "reset_each_decision": True, "normalize": True, "normalize_to": "innate"}
orig = W.Agent.learn_and_affect
rec = []
def wrap(self, reward, sensors, *a, **k):
    e = sum(float(cn._stdp.eligibility.sum()) for cn in self._plastic) if self.id == 0 else 0
    rpe = orig(self, reward, sensors, *a, **k)
    if self.id == 0:
        rec.append((rpe, e))
    return rpe
W.Agent.learn_and_affect = wrap
for label, extra in (("align", {"n_hazard": 0}), ("approach", {"n_hazard": 0, "reward_mode": "approach"}), ("eat_only", {"n_hazard": 0, "r_align": 0.0}), ("align_no_norm", {"n_hazard": 0, "normalize": False})):
    for seed in (11, 12, 13):
        rec.clear()
        w = W.World2D(W.WorldConfig(**{**FULL, **extra}, seed=seed, max_ticks=500))
        for ep in range(3):
            w.reset(keep_weights=ep > 0)
            w.run(learning=True)
        r = np.array(rec); rpe, e = r[:, 0], r[:, 1]
        pos = rpe > 0
        print(f"{label:20s} seed {seed} mean rpe {rpe.mean():+.4f}  E[rpe*e] {(rpe*e).mean():+.4f}  "
              f"corr {np.corrcoef(rpe, e)[0,1]:+.3f}  elig|rpe>0 {e[pos].mean():.1f} elig|rpe<0 {e[~pos].mean():.1f}  frac+ {pos.mean():.2f}")
