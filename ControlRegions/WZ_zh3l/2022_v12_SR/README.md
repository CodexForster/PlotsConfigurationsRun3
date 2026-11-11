# WZ control region for ZH(->WW) -> 3l, 2022 (pre-EE)

Final state: Z(->ll) + W(->lnu) + W(->jj), i.e. 3 leptons + jets + MET.
Control-region and signal-region plots (copy of `2022_v12_wClaude` with the SR added).
Signal: qqZH and ggZH, plotted separately, from the Z -> ll, H -> WW -> lnu qq samples
(`ZH_Zto2L_Hto2WtoLNu2Q_M125`, `GluGluZH_Zto2L_Hto2WtoLNu2Q_M125`). They are not in the central 2022 production and were
post-processed privately (same steps as the central MC) into `signalDirectory` (`samples.py`):
`/eos/user/d/dshekar/private_postprocess_zh3l_signal_samples/Summer22_130x_nAODv12_Full2022v12/MCl2loose2022v12__MCCorr2022v12JetScaling__l2tight`.
The other private ZH decays are not used: `Zto2L_Hto2Wto2L2Nu` (4l, enters the 3l SR when a lepton is lost) is left
out for now; the Z -> qq and H -> WW -> 4q ones reach 3l only with non-prompt leptons, removed by `PromptGenLepMatch3l`.
SR cuts (`zh3l_SR_incl`, `zh3l_SR_1j/2j(_met)`): same as the WZ CR with the dphi cut inverted.
Data is blinded in the SR in the plots only (`blind` in `variables.py`); the SR data histograms are still in the ROOT file.

Built from `ControlRegions/WZ/2022_v12` and `ControlRegions/WZ_zh3l/2022_v12`, with the selection, process list
and variables of the Run 2 ZH3l analysis (`PlotsConfigurations/Configurations/ZH3l/Full2018_v7`).

## Selection

- preselection: lepton pT > 25/20/15 GeV, veto on a 4th lepton with pT > 10 GeV, all m(OS ll) > 12 GeV, total charge = ±1,
  |m(OSSF) - mZ| < 25 GeV (`WH3l_ZVeto`), |m(lll) - mZ| > 20 GeV (`ZH3l_Z4lveto`), b veto, at least one jet with pT > 30 GeV
- `zh3l_WZ_CR_1j`: exactly one jet and dphi(l_W + MET, j) > pi/2
- `zh3l_WZ_CR_2j`: at least two jets and dphi(l_W + MET, jj) > pi/2
- `*_met`: same with PUPPI MET > 25 GeV; `zh3l_WZ_CR_incl`: 1j or 2j CR

The signal region is the same with the dphi cut inverted.
All `WH3l_*` / `ZH3l_*` variables come from the trees (`mkShapesRDF/processor/modules/l3KinProducer.py`).

## Backgrounds

WZ, ZZ, VVV, Zg, Zg*, WW, DY and top from MC, with three prompt leptons (Zg without prompt matching).
No non-prompt (Fake) estimate and no ttV sample (not in the 2022 v12 sample list) for the moment.
MC samples not found in the production are skipped with a warning when compiling (`samples.py`).

## Run

    cd ../../../../mkShapesRDF/
    source start.sh
    cd -

    mkShapesRDF -c 1
    mkShapesRDF -c 1 -o 0 -f . -b 1
    mkShapesRDF -o 1 -f .            # check jobs
    mkShapesRDF -o 1 -f . -r 1       # resubmit failed jobs
    mkShapesRDF -o 2 -f .            # merge

    mkPlot --onlyPlot cratio --showIntegralLegend 1 --fileFormats png
