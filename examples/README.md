# NeuralMind examples

## Interactive simulation viewer

Generate a self-contained HTML viewer of a recorded simulation (no external
libraries, no network calls — it opens straight in any browser):

```bash
python -m neuralmind.cli visualize --steps 450 --seed 0 --out examples/neuralmind_viewer.html
```

Then open `examples/neuralmind_viewer.html`. You get:

- a **spike raster** for an input → excitatory/inhibitory network (blue = input,
  orange = excitatory, green = inhibitory);
- a **population firing-rate** chart;
- **affect variables** (valence / arousal / threat) read out from the live
  population activity;
- **play / step / reset / timeline** controls, with a readout that always shows
  the recorded values at the current step.

A stimulus pulse is delivered during the middle third of the run, so you can see
activity and the threat read-out rise and then return to baseline. Every value
shown is read from the recorded simulation state (see `neuralmind/recorder.py`),
not illustrative mock data.

The generated `.html`/`.png` files are git-ignored; regenerate them with the
command above.
