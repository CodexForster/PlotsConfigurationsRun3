# Simultaneous optimization of the ZH3l selection thresholds

This folder **trains all the thresholds at the same time** to maximize the significance, then **validates** the result on events that were not used in the training and **drops the changes whose gain is too small**.

The method is the one of the `SoftQuantize` branch of
[smart-pixels-ml](https://github.com/ArghyaRanjanDas/smart-pixels-ml/tree/SoftQuantize) (`models/SoftQuantizeLayer.py`,
`models/AnnealingScheduler.py`, `Thr_summary.png`):
- every hard threshold is replaced by a sigmoid whose sharpness k is annealed from soft to hard during the training;
- the thresholds are trained by gradient descent;
- the training is repeated from several starting points, and the evolution of the thresholds with the epochs is
  plotted.

It is gradient-based optimization of a differentiable relaxation of the cuts: the same machinery as the training of a
neural network, but the only trainable parameters are the thresholds, one per cut, so the result stays a cut-based
selection that can be put back in `cuts.py`.

Only numpy and matplotlib are needed (the gradients are computed analytically, no TensorFlow/PyTorch). It runs from the
per-event arrays cached by `cut_scan.py`, so the trees are not read again: on lxplus or on a laptop.

## Contents

1. [Quick start](#quick-start)
2. [Input](#input)
3. [Method: how the thresholds are trained](#method-how-the-thresholds-are-trained)
4. [Validation: best run, hard-cut Z, pruning](#validation-best-run-hard-cut-z-pruning)
5. [Outputs and how to read them](#outputs-and-how-to-read-them)
6. [Options](#options)
7. [Caveats](#caveats)
8. [Applying the result](#applying-the-result)
9. [Files](#files)

## Quick start

    # from the PlotsConfigurationsRun3 folder:
    # 1. per-event arrays from cut_scan (on lxplus; only needed once, or when samples/aliases change)
    cd ../mkShapesRDF && source start.sh && cd -
    cd ControlRegions/WZ_zh3l/2022_v12_wClaude_SR/cut_scan
    python3 cut_scan.py --cache arrays.npz
    cd -

    # 2. optimization
    cd zh3l-threshold-optimization-ml
    CACHE=../ControlRegions/WZ_zh3l/2022_v12_wClaude_SR/cut_scan/arrays.npz
    python3 optimize_thresholds.py --cache $CACHE --region incl --runs 4 --epochs 150 --no-gif   # quick test
    python3 optimize_thresholds.py --cache $CACHE --jobs 8                                        # full: 1j, 2j, incl

    # only redo the plots (no training)
    python3 optimize_thresholds.py --cache $CACHE --replot

Outputs go to `results/<region>/`. Start with `summary.txt`, then `pruning.png`, `run_summary.png` and
`threshold_evolution_all.png`.

Timing: the training time scales with (number of events) × (number of cuts) × epochs × runs. As a reference, on a
synthetic sample of 180k events (10 cuts, 2j region), one run of 300 epochs takes ~35 s on one core. The default
(20 runs × 600 epochs) is then ~25 min per region on one core, ~3-4 min with `--jobs 8`.

## Input

The `.npz` cache written by `cut_scan.py --cache`: for every MC sample (signal and backgrounds, as in `samples.py`
of the SR configuration) the per-event weight `w` (lumi × the same weights as in the plots) and the value of every
cut variable (`cv_pt1`, `cv_pt3`, `cv_met`, ...) after the loose base selection of `cut_scan`. The signal samples are
the ones of `SIGNAL` in `cut_scan.py` (`ZH_hww`, `ggZH_hww`); without signal in the cache the script stops.

The cut definitions (variable, operator, nominal threshold, scan range and step) are imported from `cut_scan.py`
(`get_cuts()`), so the two tools always use the same cuts. The regions are the same as in `cut_scan`:
`1j` (exactly 1 jet), `2j` (≥ 2 jets) and `incl` (≥ 1 jet). Each region is optimized separately.

Which cuts are trained:
- **trained**: the cuts that `cut_scan` scans and that are applied in the nominal selection: `pt1`, `pt2`, `pt3`,
  `lep4veto`, `mOSll_min`, `Zwindow`, `Z4lveto`, `dphi`.
- **fixed**: `bveto` and `njet` (`op='fixed'` in `cut_scan`), and the total charge requirement (in the base
  selection), are applied as they are.
- **frozen**: `--freeze pt1,pt2` keeps the listed cuts at their nominal value (applied as hard cuts, not trained).
- **skipped**: `met` and, in 2j, `mjj_window` are not applied in the nominal selection (`nominal=None` in
  `cut_scan`), so they are neither trained nor applied. When one of them gets a nominal value in `get_cuts()` of
  `cut_scan.py`, it is trained like the other cuts, with no change needed here.

(The "off" machinery described in [cuts that are off in the nominal selection](#cuts-that-are-off-in-the-nominal-selection)
is therefore not used. It would only be used if the skipping in `Problem` (`softcuts.py`) were removed, to let the
optimizer decide whether to switch these cuts on.)

## Method: how the thresholds are trained

### All thresholds are learned simultaneously

At every step (epoch) the yields are computed with **all** the cuts applied at their current thresholds, the gradient
of the significance with respect to **every** threshold is computed, and **all** the thresholds are moved together.
The difference with `cut_scan` is that the correlations between cuts are taken into account. For example, if
tightening `Z4lveto` (|m(lll) − m_Z|) already removes most of the Zγ, loosening pT3 becomes cheaper, and the optimizer
sees it.

### 1. Normalized coordinates

Each cut j is "keep if x > t" or "keep if x < t". With s_j = +1 (`>`) or −1 (`<`) and τ_j the scan step of that
variable in `cut_scan` (2.5 GeV for pT1, 1 GeV for pT3, 0.2 for Δφ, 2 GeV for min m(OS ll), ...):

    v_ij = s_j x_ij / τ_j,     θ_j = s_j t_j / τ_j,     keep event i  ⇔  v_ij > θ_j for every cut j

so every cut becomes a ">" cut and **one unit of θ is one scan step** of that variable. This makes the learning rate,
the sharpness k and the L1 penalty below mean the same thing for all the cuts, whatever their units.

### 2. Soft cuts

A hard cut gives each event a factor 0 or 1. As a function of the threshold that is a step function, whose derivative
is zero almost everywhere, so gradient descent cannot move it. It is replaced by a sigmoid:

    p_ij = σ(k (v_ij − θ_j)),   σ(z) = 1 / (1 + e^(−z))

- k small (≈ 0.5–2): events within a few steps of the threshold get a fractional weight (0.3, 0.7, ...).
- k large (≈ 50): p is 0 or 1 except within 1/50 of a step of the threshold, i.e. practically the hard cut.

`soft_vs_hard_cut.png` shows p for several k, as `SoftQuant.png` in smart-pixels-ml.

Each event gets the product of the factors of all the cuts, and the soft yields are

    P_i = Π_j p_ij,      S = Σ_{i ∈ signal} w_i P_i,      B = Σ_{i ∈ background} w_i P_i

with w_i the same event weights as in the plots (negative NLO weights included).

### 3. Gradients

Because d ln p_ij / dθ_j = −k (1 − p_ij), the derivatives of the yields with respect to all the thresholds are

    ∂S/∂θ_j = −k Σ_{i ∈ sig} w_i P_i (1 − p_ij),      ∂B/∂θ_j = −k Σ_{i ∈ bkg} w_i P_i (1 − p_ij)

Only events near threshold j (where 1 − p_ij is not 0 or 1) and passing the other cuts (P_i not ≈ 0) contribute. These
are exactly the events that a small move of the threshold would add or remove. All the gradients are computed in one
pass over the events.

### 4. Objective: significance

By default the Asimov significance, the same as in `cut_scan`:

    Z_A = √(2 [(S + B) ln(1 + S/B) − S]),   ∂Z_A/∂S = ln(1 + S/B) / Z_A,   ∂Z_A/∂B = (ln(1 + S/B) − S/B) / Z_A

`--objective s_over_sqrtb` uses S/√B instead. Both are statistics-only significances (no systematic uncertainty).

### 5. Loss

The quantity that is minimized:

    L = −Z(S, B) / Z_nom  +  λ Σ_j |θ_j − θ_j^nom|  +  μ · max(0, 1 − N_eff(B) / N_min)²

- **−Z / Z_nom**: maximize the significance. Z_nom is the hard-cut significance of the nominal selection on the
  training sample, so the first term is −1 at nominal and the other terms are fractions of the nominal Z.
- **λ Σ |θ_j − θ_j^nom|** (`--lam`, default 0.002): L1 pull to the nominal thresholds. Moving a threshold by one scan
  step costs λ = 0.2% of the nominal Z, so a threshold moves only if the significance gained pays for it. This is
  the first filter against changes with little gain; the L1 form (rather than a quadratic one) keeps thresholds
  exactly at nominal when the gain is small. The second filter is the pruning on the test sample
  ([below](#3-pruning-dropping-the-changes-with-too-little-gain)).
- **MC statistics guard** (`--min-neff`, default 30; `--neff-weight` μ, default 1): N_eff(B) = (Σ a_i)² / Σ a_i², with
  a_i = w_i P_i over the background events, is the Kish effective number of MC events. Without this term, a very
  tight selection can look good because only a few MC events (sometimes with negative weights) are left. Below N_min
  the penalty grows quadratically.

### 6. Optimizer and annealing

- **Adam**, full batch: every epoch uses all the training events. The learning rate `--lr` (default 0.1) is in scan
  steps per epoch, with a cosine decay to `lr/10` at the end so that the thresholds settle.
- **Annealing of k** (`--k-start 0.5`, `--k-end 50`, `--k-schedule cosine`, as `AnnealingScheduler` in
  smart-pixels-ml):
  - **Early**, k is small: the soft yields are smooth functions of the thresholds. The thresholds can travel far
    without getting stuck on the statistical bumps of the weighted MC, and the gradient is felt even from events
    several steps away.
  - **Late**, k is large: the soft yields become the hard yields, so the thresholds settle where the **hard** cut is
    good, not where the soft approximation is good.

  This is why the trajectories in `threshold_evolution_*.png` move a lot in the first ~third of the training and then
  stabilize.
- After every step the thresholds are clipped to their allowed range: the `cut_scan` scan range, extended for the
  cuts that are off in the nominal selection.

### 7. Several runs

The training is repeated `--runs` times (default 20):
- **run 0** starts from the nominal thresholds and uses the training events as they are;
- **runs 1, 2, ...** start from random thresholds (nominal ± `--init-spread` × allowed range, uniform; default 0.5),
  and use a **bootstrap replica** of the training events (each event weight multiplied by a Poisson(1) number).

The spread of the final thresholds over the runs therefore includes the dependence on the starting point (local
optima) **and** the MC statistical fluctuations. Reading it:
- all runs end at the same value: that threshold is well determined;
- the runs are spread out: the significance is flat in that variable, and the precise value does not matter (or is
  not determined with the available MC statistics);
- the runs form two groups: there are two optima (e.g. pT3 > 10 in some runs, pT3 > 20 in others).

### Cuts that are off in the nominal selection

**Not used at the moment**: these cuts (`nominal=None` in `cut_scan`, i.e. `met` and `mjj_window`) are skipped (see
[Input](#input)). The following applies only if the skipping in `Problem` is removed.

For such a cut, the allowed threshold range is the scan range extended by 3
steps on the loose side. The variable is clipped one step beyond the loose end of the scan (`off_edge`), so that a
threshold beyond `off_edge` keeps all the events: **the cut is not applied**. That zone is shaded gray in the plots.
The nominal selection for these cuts is "off", and the L1 pull pulls them there. Because the off zone is close to the
events (3 steps), the gradient still reaches a cut that starts off, and the training can turn it on if that helps.

## Validation: best run, hard-cut Z, pruning

### Hard-cut Z

The **hard-cut Z** is the significance computed with the thresholds applied as ordinary step cuts (`x > t`: weight 0 or
1), exactly as mkShapesRDF would apply them. It is the same quantity as in `cut_scan`. The soft Z used in the training
is only an approximation of it (events near the thresholds count partly), so **all the numbers that are reported
(tables, pruning, final result) are hard-cut Z**. The soft Z is shown only in `training_history.png`.

### Train / test split

Before the training, the events are split at random (fixed seed `--seed`) into a **training** and a **test** sample
(`--test-fraction`, default 0.5). The weights of each half are divided by its fraction, so that each half represents
the full luminosity. The split is the same for all the runs.
- The **training** half is the only one used to compute the gradients (and to choose the best run, below).
- The **test** half is never used in the training. It is used only to evaluate the hard-cut Z and for the pruning.

If a threshold moved to exploit a statistical fluctuation of the training events (a few large-weight or
negative-weight MC events), the gain shows up in the training half but **not** in the test half. Comparing the train
and test numbers (`summary.txt`, `training_history.png`) is therefore the check for overfitting: they should agree
within the bootstrap uncertainty.

### 1. Best run

For each run, the final thresholds are rounded to the `cut_scan` grid:
- a threshold within half a step of nominal is set back to nominal;
- for a cut that is off in the nominal selection (none at the moment, see
  [above](#cuts-that-are-off-in-the-nominal-selection)), a threshold beyond `off_edge` means "off".

The run whose rounded thresholds give the highest hard-cut Z **on the training sample** is selected. The test sample
is not used for this choice.

(The median of the runs is not used: when the runs end in two different optima, the median can lie between them, in a
point that is not an optimum at all. For example, 3 runs with `pt3 > 10` and 3 with `pt3 > 20` give a
median of 15, which can be worse than both. The median and the spread are still reported in `thresholds.csv`
as stability information.)

### 2. Bootstrap uncertainty

The statistical uncertainty of a hard-cut Z on the test sample comes from a bootstrap. The test events are resampled
`--n-boot` times (default 200), each event weight multiplied by a Poisson(1) number, and Z is recomputed on every
replica; the uncertainty is the spread. The same replicas are used for all the selections, so the uncertainty on a
**difference** of Z between two selections correctly accounts for the events they have in common.

This is the uncertainty due to the limited number of **MC** events (not the data statistics: that is what Z itself
measures).

### 3. Pruning: dropping the changes with too little gain

Starting from the best run, on the **test** sample:

1. For every cut whose threshold differs from nominal, put that cut alone back to nominal (the others stay as they
   are) and compute `ΔZ_j = Z(current) − Z(current with cut j at nominal)` and its bootstrap uncertainty σ_j.
2. A change is worth keeping if `ΔZ_j ≥ max(min_gain × Z(current), n_sigma × σ_j)`:
   - `--min-gain` (default 0.01): it must gain at least 1% of Z;
   - `--n-sigma` (default 1): the gain must be larger than its statistical uncertainty.
3. If some changes fail, the one with the smallest ΔZ_j is reverted to nominal and step 1 is repeated, because once a
   cut is reverted, the gains of the others can change.
4. Stop when all the remaining changes pass.

What is left is a short list of changes, each with its gain on the test sample, e.g. "loosen pT2 to 12.5 GeV and pT3
to 10 GeV, keep everything else at nominal".

Note: the pruning uses the test sample to make decisions, so the final test Z is very slightly optimistic. The pruning
can only revert changes (towards nominal), so the effect is small. For a fully independent number, rerun with a
different `--seed` (different split) and check that the same changes survive.

## Outputs and how to read them

Everything is in `results/<region>/`.

| File | Content |
|---|---|
| `summary.txt` | Thresholds (nominal, best run, final), yields and Z (train, test, all events) for the three selections, every pruning iteration, and the final selection in mkShapesRDF syntax. **Start here.** |
| `thresholds.csv` | Per cut: nominal, scan range and step, median and spread of the runs, fraction of runs that changed the cut, fraction of runs that agree with the best run within one step, best-run and final thresholds, status (`unchanged` / `kept` / `reverted (gain too small)`), ΔZ of the first pruning iteration and its uncertainty. |
| `yields.csv` | S, B, S/B, S/√B, Z for nominal / best run / final, on the train / test / all events (bootstrap uncertainty of Z on test). |
| `yields_per_process.csv` | Yield of every sample, nominal vs final, and their ratio. **Check this**: it shows which backgrounds a change lets in (see [caveats](#caveats)). |
| `results.json`, `history.npz` | Everything needed to redo the plots (`--replot`). |

Plots (CMS style, in plain matplotlib: "CMS Simulation Preliminary" and "<lumi> fb⁻¹ (13.6 TeV)" above the axes,
ticks inside, Petroff colour palette; the region and run information is in the legend titles):

- **`threshold_evolution_<cut>.png`** (one per cut), in the style of `Thr_summary.png`:
  - **Top**: threshold vs epoch for all the runs, epochs going **down**. Run 0 (nominal start) is darker. The black
    dashed line is nominal and the red line is the final value after pruning.
  - **Bottom**: distribution of the final thresholds over the runs, with mean ± error and spread ± error in the legend.
  - Read it as described in [several runs](#7-several-runs).
- **`threshold_evolution_all.png`**: the top panels of all the cuts in one figure.
- **`training_history.png`**:
  - **Top**: significance vs epoch. Shown are the soft Z (train), the hard-cut Z (train) and the hard-cut Z (test),
    thin lines per run and thick lines for the median, with the nominal hard-cut Z (test) as a dashed line and k
    (dotted gray) on the right axis.
    - Soft and hard Z converge once k is large.
    - Hard-cut Z on train and test should agree; if train goes up and test does not, the training is fitting MC
      fluctuations.
  - **Bottom**: effective number of MC background events during the training, with the `--min-neff` limit.
- **`run_summary.png`**: final hard-cut Z on the test sample for every run. The best run is circled. Lines show
  nominal, best run (rounded) and final (after pruning), with bootstrap bands. Runs at very different Z mean different
  optima.
- **`pruning.png`**: ΔZ/Z (%) when each changed cut is put back to nominal (first pruning iteration), with n_sigma
  bootstrap error bars and the min-gain line. Blue: kept, gray: reverted. This plot shows which changes matter.
- **`nminus1_final.png`**: N−1 distributions (all events, background stacked as one, signal × `--signal-scale`), with
  all the other cuts at their final values. Black dashed: nominal; red: final.
- **`nminus1_evolution_run0.gif`**: the same N−1 distributions while the thresholds of run 0 move during the training
  (50 frames, epoch, k and hard-cut Z at the top). `--no-gif` skips it.
- **`soft_vs_hard_cut.png`**: the soft cut for several k (for `pt3`), and the k and learning-rate schedules.

## Options

| Option | Default | Meaning |
|---|---|---|
| `--cache` | (required) | `arrays.npz` from `cut_scan.py --cache` |
| `--cut-scan-dir` | `../ControlRegions/WZ_zh3l/2022_v12_wClaude_SR/cut_scan` | where `cut_scan.py` (cut definitions) is |
| `--region` | `all` | `1j`, `2j`, `incl` or `all` (the three, one after the other) |
| `--outdir` | `results/` | parent folder of `<region>/` |
| `--freeze` | none | comma-separated cuts kept at nominal |
| `--objective` | `asimov` | `asimov` or `s_over_sqrtb` |
| `--runs` | 20 | training runs (run 0: nominal start; others: random start + bootstrap) |
| `--epochs` | 600 | epochs per run |
| `--lr` | 0.1 | Adam learning rate (scan steps per epoch), cosine decay to lr/10 |
| `--k-start`, `--k-end` | 0.5, 50 | sharpness of the soft cuts at the start / end |
| `--k-schedule` | `cosine` | `cosine`, `linear`, `exponential` |
| `--lam` | 0.002 | L1 pull to nominal: fraction of the nominal Z one step of change must gain |
| `--min-neff`, `--neff-weight` | 30, 1 | MC statistics guard on the background (0 = off) |
| `--init-spread` | 0.5 | random start: nominal ± spread × allowed range |
| `--test-fraction` | 0.5 | fraction of events in the test sample |
| `--seed` | 1 | train/test split, starting points, bootstrap |
| `--eval-every` | 5 | hard-cut Z evaluated every N epochs (for the history plot) |
| `--min-gain` | 0.01 | pruning: minimum relative gain of a change |
| `--n-sigma` | 1 | pruning: minimum gain in units of its bootstrap uncertainty |
| `--n-boot` | 200 | bootstrap replicas |
| `--signal-scale` | 10 | signal scale in the N−1 plots |
| `--jobs` | 1 | runs trained in parallel (processes) |
| `--no-gif` | | skip the animation |
| `--lumi` | from `configuration.py` | luminosity in the CMS label (1/fb); default: `lumi` of the configuration one folder above `--cut-scan-dir` |
| `--cms-label` | `Simulation Preliminary` | text after "CMS" (the plots show MC only, hence "Simulation") |
| `--replot` | | only redo the plots from `results/<region>/` |

Things worth trying:
- **More conservative**: `--lam 0.005 --min-gain 0.05 --n-sigma 2`.
- **Stability of the result**: change `--seed` (different split, starting points and replicas); the changes that
  survive with every seed are the robust ones.
- **Keep the lepton pT thresholds as they are** (e.g. trigger, fake-rate measurement): `--freeze pt1,pt2,pt3`.

## Caveats

1. **Backgrounds that are not in the MC sum are invisible to the optimizer.** There is no fake (non-prompt) estimate
   yet, and the backgrounds with a non-prompt lepton are removed by `PromptGenLepMatch3l`. A change that lets in
   non-prompt leptons looks free here but would not be in the real analysis. Loosening `pt3`, `pt2`, `mOSll_min` or
   `Z4lveto`, or removing `lep4veto`, is exactly that kind of change. Treat such suggestions with caution until a fake
   estimate is included, and look at `yields_per_process.csv`. On the synthetic test sample, loosening pT2/pT3
   multiplied the Zγ and DY yields by 6.7 and 3.3 while improving Z.
2. **Statistics-only significance.** Loosening cuts that do not separate signal from background still increases S/√B
   (both S and B grow, and Z ∝ √(more events)). With systematic uncertainties on the background, that is no longer
   true (see the S/B discussion in `cut_scan/README.md`). Check S/B in `yields.csv`: a change that improves Z but
   lowers S/B makes the result more sensitive to background mismodelling.
3. **`dphi` is also the SR/CR boundary**: moving it changes the WZ control region too.
4. **Lepton pT thresholds have constraints outside this optimization**: trigger plateaus, the fake-rate measurement
   and the scale factors. Use `--freeze` if they cannot move.
5. **Each region is optimized separately**, and the result is a single-bin counting significance. In a shape fit the
   optimal cuts can be looser (the fit uses the shape of the discriminating variable).
6. **Cut ordering**: pT1 > pT2 > pT3 by construction, so a pT2 threshold below the pT3 threshold has no effect (same
   for pT1). This is harmless but can make the trajectories of `pt1`/`pt2` flat or erratic.
7. The final numbers are limited by the MC statistics of the private signal samples and of the backgrounds. The
   bootstrap uncertainties show how much.

## Applying the result

`summary.txt` ends with the final selection of the trained cuts in mkShapesRDF syntax, e.g.

    Alt(Lepton_pt,1,0) > 12.5
    Alt(Lepton_pt,2,0) > 10

To use it:
1. Change the corresponding cuts in `cuts.py` of the configuration (a copy folder, keeping the nominal one for
   comparison).
2. Update the nominal values in `get_cuts()` of `cut_scan.py`.
3. Rerun `cut_scan` to check the N−1 and scan plots around the new thresholds.
4. Rerun mkShapesRDF and mkPlot and compare the SR/CR plots with the nominal ones (data/MC agreement in the CR in
   particular).

## Files

- `optimize_thresholds.py`: main script (options, runs, validation, output tables).
- `softcuts.py`: events and cuts of a region (`Problem`), soft cuts, significance and gradients, k annealing, Adam,
  training of one run.
- `validation.py`: best-run selection, bootstrap, pruning.
- `plots.py`: all the plots and the animation.
