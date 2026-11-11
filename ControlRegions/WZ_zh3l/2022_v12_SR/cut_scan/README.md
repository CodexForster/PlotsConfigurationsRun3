# Kinematic selection study (ZH3l, 2022 v12)

`cut_scan.py` studies the impact of each cut of the ZH3l selection on the MC backgrounds (no data).
For every cut it gives the cutflow, the N-1 distribution and a scan of the background rejection vs the
cut threshold.

Samples, weights and aliases are read from the mkShapesRDF configuration in the parent folder
(`samples.py`, `aliases.py`, `configuration.py`), so yields are the same as in the mkShapesRDF plots.
Background = sum of all the MC samples of that configuration.
Cuts, nominal values and scan ranges are defined in `get_cuts()` in the script.

## Regions

All the outputs are made for three jet regions, each in its own folder `plots_<region>/`:

| Region | Jets (pT > 30 GeV, \|eta\| < 4.7) | dphi variable |
|---|---|---|
| `1j` | exactly 1 | dphi(l_W + MET, j) |
| `2j` | at least 2 | dphi(l_W + MET, jj) |
| `incl` | at least 1 (= 1j + 2j) | dphi(l_W + MET, j) for 1-jet events, dphi(l_W + MET, jj) for >= 2-jet events (as `zh3l_WZ_CR_incl` in `../cuts.py`) |

The trees are read once for all the regions: the stored variables are the same, only the jet requirement
(and the mjj cut, 2j only) changes. After the `njet` step, the yields of `incl` are the sum of `1j` and `2j`.

## Selection

Fixed in all regions: `abs(WH3l_chlll) == 1`.

| Cut | Variable | Nominal | Scan |
|---|---|---|---|
| `pt1` | pT of the leading lepton | > 25 GeV | 10-45 GeV, step 2.5 |
| `pt2` | pT of the 2nd lepton | > 20 GeV | 10-40 GeV, step 2.5 |
| `pt3` | pT of the 3rd lepton | > 15 GeV | 10-30 GeV, step 1 |
| `lep4veto` | pT of the 4th lepton (0 if none) | < 10 GeV | 5-30 GeV, step 2.5 |
| `mOSll_min` | min m(ll) over the opposite-sign pairs | > 12 GeV | 0-40 GeV, step 2 |
| `Zwindow` | `WH3l_ZVeto` = min \|m(OSSF) - mZ\| | < 25 GeV | 5-50 GeV, step 2.5 |
| `Z4lveto` | `ZH3l_Z4lveto` = \|m(lll) - mZ\| | > 20 GeV | 0-50 GeV, step 2.5 |
| `bveto` | max DeepFlavB score of the jets with pT > 20 GeV, \|eta\| < 2.5 | < 0.0583 (loose WP) | not scanned |
| `njet` | `ZH3l_njet` (jets pT > 30 GeV) | == 1 (1j), >= 2 (2j), >= 1 (incl) | not scanned |
| `dphi` | `ZH3l_dphilmetj` (1-jet events) / `ZH3l_dphilmetjj` (>= 2-jet events) | < pi/2 | 0.4-pi, step 0.2 |
| `met` | PUPPI MET | not applied | 0-100 GeV, step 5 |
| `mjj_window` | \|m(jj) - mW\| (2j only) | not applied | 10-150 GeV, step 10 |

The nominal selection is the **signal-region side** (dphi < pi/2). The WZ CR is the same with dphi > pi/2.

## Method

**Cutflow** (`cutflow.csv`, also printed): the nominal cuts are applied one after the other, in the order of
the table. After each step: weighted yield of each process, total background B, background rejection of that
step (`BR_step` = 1 - B_after / B_before) and cumulative (`BR_cumul` = 1 - B_after / B_base).

**Cutflow plots** (`cutflow.png` linear scale, `cutflow_log.png` log scale): the same yields as `cutflow.csv`,
without BR. x axis: the cut steps (cumulative, left to right, with their nominal values); y axis: weighted yield
after each step, one line per sample and the total background in black. The legend gives the final yield of each
sample. In the log version, steps where a sample has a yield <= 0 (possible with negative MC weights when few
events are left) are not drawn; the linear version shows them.

**N-1 plots** (`nminus1_<cut>.png`, `_log.png`): distribution of the variable of one cut with all the
*other* cuts at their nominal values and that cut removed. Backgrounds are stacked, the nominal threshold is
the dashed line. Under/overflow are put in the first/last bin.

**Scans** (`scan_<cut>.png/.csv`): for one cut, e.g. `pt1`, and for each threshold t of its scan
(e.g. 10, 12.5, ..., 45 GeV):

1. the cut is applied with threshold t (e.g. pT(l1) > 30 GeV)
2. all the other cuts are applied at their nominal values (cuts with "not applied" stay off)
3. the yields are computed: total background B(t) and the yield of each process (columns `N_<process>`)

and this is repeated for every threshold and for every cut. The background retention is

    BR(t) = B(t) / B(nominal)

where B(nominal) is the yield with **all** the cuts at their nominal values, the scanned cut included
(= the last line of the cutflow, the same for all the scans). So BR(t) is the background w.r.t. the
nominal selection when only the scanned cut is moved to t:

- BR = 1 at the nominal threshold;
- BR < 1 for thresholds tighter than nominal (less background than nominal);
- BR > 1 for thresholds looser than nominal (e.g. BR = 1.3: 30% more background than nominal).

For cuts not applied in the nominal selection (`met`, `mjj_window`), B(nominal) is the yield without that cut,
so BR starts from 1 at the loosest threshold.

BR counts all the MC, WZ included. In the WZ CR the goal is to keep WZ and reject the rest, so also look at
the per-process yields in the csv.

Expected features:
- Leptons are ordered in pT, so pT(l1) > pT(l2) > pT(l3): with pT(l2) > 20 GeV applied, every event already has
  pT(l1) > 20 GeV and the `pt1` scan is flat below 20 GeV (at the BR > 1 of the 20 GeV point).
  Same for `pt2` below the `pt3` threshold.
- `bveto` and `njet` are fixed requirements: they are applied everywhere and appear in the cutflow and in the
  N-1 plots, but are not scanned. To scan the b-veto WPs again, see the comment above `bveto` in `get_cuts()`.

**Signal**: `SIGNAL` in the script holds the signal samples. With signal, the cutflow gets the signal efficiency
(`SE_step`, `SE_cumul`), S/B, S/sqrt(B) and the Asimov significance; the scans get the signal efficiency
SE(t) = S(t) / S(nominal) (1 at nominal, > 1 for thresholds looser than nominal), drawn on the secondary (right)
y axis of the top panel, with the same range as the BR axis, plus S/sqrt(B) and the Asimov significance in the
bottom panel, with S/B on its secondary (right) y axis (column `S_over_B` in `scan_*.csv`); the signal is overlaid (scaled) in the N-1 plots.
NB: the cutflow table still uses the background *rejection* `BR_step` / `BR_cumul` = 1 - B_after / B_before.

Signal samples (NEW w.r.t. 2022_v12_wClaude): `ZH_Zto2L_Hto2WtoLNu2Q_M125` and `GluGluZH_Zto2L_Hto2WtoLNu2Q_M125`
(Z -> ll, H -> WW -> lnu qq), with the same keys as in `../samples.py` (`ZH_hww`, `ggZH_hww`), so they are not counted
as background. They are privately post-processed and read from `signalDirectory` (defined in `../samples.py`).

## How it is computed, and running time

Reading the trees is the slow part; the scans themselves are not:

- Each process is read **once**, in one RDataFrame event loop (datasets of a process with the same weight are
  merged; Zg and ZgS read the same files twice since their weights differ). ROOT implicit multithreading is
  used inside each event loop (`--threads`, default: all cores).
- A loose base selection is applied while reading (`BASE` in the script, looser than every scan point):
  `pT(l3) > 10 GeV && abs(WH3l_chlll) == 1 && WH3l_ZVeto < 50`.
- For the events passing it, the weight and the value of every cut variable are stored (`AsNumpy`).
- The cutflow, the N-1 plots and all the scan points are then computed from these stored values with numpy.
  This gives exactly the same result as running the selection again for every threshold, but it needs no extra
  event loop: the ~150 scan points take seconds.

The running time is therefore set by the number of files: the processes are read one after the other, and the
time per process is printed. DY and top (many files) dominate. Before a full run:

- check the time with `--max-files` (see below) and extrapolate;
- run the full job in a way that survives the end of the lxplus session, e.g. inside `tmux`/`screen`, or
  `nohup python3 cut_scan.py --cache arrays.npz > log.txt 2>&1 &`;
- always use `--cache`, so that the trees are read only once.

## Run (lxplus)

Load the mkShapesRDF environment (ROOT, mkShapesRDF modules), then go to this folder:

    cd ../../../../../mkShapesRDF/ && source start.sh && cd -

1. **Quick test**, a few files per sample (minutes). Checks that everything runs and gives the time per file;
   the yields are not meaningful (wrong normalization) since only part of each sample is read:

       python3 cut_scan.py --max-files 3

2. **Full run** over all the files. Produces all the outputs for the three regions (`plots_1j/`, `plots_2j/`,
   `plots_incl/`) and saves the per-event arrays to `arrays.npz`:

       python3 cut_scan.py --cache arrays.npz

3. **Redo only tables and plots** from the saved arrays, without reading the trees (seconds). Use it after
   changing scan ranges, nominal values, the order of the cutflow or the plot style. Adding a new cut,
   changing a cut *expression*, the `BASE` selection or the samples needs a new full run (the cache only
   contains the variables of the existing cuts). One cache serves all the regions:

       python3 cut_scan.py --from-cache arrays.npz

4. **Only one region**: add `--region 1j`, `--region 2j` or `--region incl` to any of the commands above
   (default: `--region all`), e.g.

       python3 cut_scan.py --region incl --from-cache arrays.npz

Caches made before the 1j/2j/incl update (e.g. `arrays_2j.npz`) stored region-specific dphi values and are
refused by the script: read the trees again with `--cache`.

Other options: `--outdir` (parent folder of the `plots_<region>/` folders, default: this folder), `--threads`,
`--signal-scale` (signal scale in the N-1 plots), `--config-dir` (default: the parent folder).

## Caveats

- No non-prompt (Fake) background in the configuration.
- b-tagging SFs are not applied (as in the configuration).
- Jet pT threshold is not scanned: the dphi and njet variables in the trees are computed with 30 GeV jets.
