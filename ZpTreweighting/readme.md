In order to produce the 2D histograms looking at gen_pTll vs pTll, an example runline(s) from the ZpTreweighting/ folder are as follows:
'''
root
.x twoDhists.cc(2022, "DY", "DeepFlavB", "loose")
'''
The arguments (2022, "DY", "DeepFlavB", "loose") are the default ones, so those could be omitted.

---

# Scale Factors and Sample Weights in ZpTreweighting

This section documents all scale factors and sample weights used in this configuration, their definitions, how they are calculated, and why they are needed. All weights and scale factors are computed by the [mkShapesRDF Run3 framework](https://github.com/latinos/mkShapesRDF/tree/Run3).

---

## 1. Sample Weights

### 1.1 `baseW` — Base Cross-Section Weight
**Definition:**
```
baseW = xs [pb] * 1000 / genEventSumw
```
where `xs` is the sample's inclusive production cross-section (in pb) and `genEventSumw` is the sum of all generator event weights (`genWeight`) summed over the entire sample.

**Why needed:** Normalises each simulated MC sample to 1 fb⁻¹ of integrated luminosity, so that MC and data can be compared on an absolute scale. All MC samples are produced with a finite number of events; `baseW` rescales the event count to match what would be observed in data for a given luminosity.

**Source:** [`mkShapesRDF/processor/modules/BaseW.py`](https://github.com/latinos/mkShapesRDF/blob/Run3/mkShapesRDF/processor/modules/BaseW.py)

---

### 1.2 `genWeight` — Generator Event Weight
**Definition:** Per-event weight produced by the matrix element generator (e.g. MadGraph, Powheg). Encodes the sign and relative weight of each generated phase-space point, including the effect of negative-weight events from NLO calculations.

**Why needed:** NLO generators can produce events with negative weights (counter-events). Ignoring `genWeight` would double-count or mis-normalise NLO samples. It must be included in any NLO sample.

---

### 1.3 `XSWeight` — Cross-Section × Generator Weight
**Definition:**
```python
XSWeight = baseW * genWeight    # for NLO samples (genWeight present)
XSWeight = baseW                # for LO samples
```
**Why needed:** This is the fundamental per-event normalisation weight that converts MC event counts to a physical cross-section prediction. It is multiplied into every MC event before any other weight.

**Source:** [`mkShapesRDF/processor/modules/formulasToAdd_MC_Full2022v12.py`](https://github.com/latinos/mkShapesRDF/blob/Run3/mkShapesRDF/processor/modules/formulasToAdd_MC_Full2022v12.py)

---

### 1.4 `METFilter_Common` — MET Filters (MC and Data)
**Definition:** Boolean product of several data-quality flags:
```
METFilter_Common = Flag_goodVertices
                 * Flag_globalSuperTightHalo2016Filter
                 * Flag_EcalDeadCellTriggerPrimitiveFilter
                 * Flag_BadPFMuonFilter
                 * Flag_BadPFMuonDzFilter
                 * Flag_hfNoisyHitsFilter
                 * Flag_ecalBadCalibFilter
```
Each flag removes events with known detector artefacts or noise:
- `Flag_goodVertices`: requires at least one good reconstructed primary vertex.
- `Flag_globalSuperTightHalo2016Filter`: removes beam-halo backgrounds from the LHC machine.
- `Flag_EcalDeadCellTriggerPrimitiveFilter`: removes events where energy is lost in dead ECAL cells, causing fake MET.
- `Flag_BadPFMuonFilter` / `Flag_BadPFMuonDzFilter`: removes events with badly reconstructed muons that fake MET.
- `Flag_hfNoisyHitsFilter`: removes noise in the forward hadronic calorimeter (HF).
- `Flag_ecalBadCalibFilter`: removes events with ECAL channels with bad calibration.

**`METFilter_DATA`** additionally applies `Flag_eeBadScFilter` (removes noise in the ECAL endcap super-clusters), which is only safe to apply to data.

**Why needed:** Without MET filters, many events with instrumental detector noise or non-collision backgrounds would contaminate the sample, producing fake MET and corrupting event-level observables.

**Source:** [`mkShapesRDF/processor/modules/formulasToAdd_MC_Full2022v12.py`](https://github.com/latinos/mkShapesRDF/blob/Run3/mkShapesRDF/processor/modules/formulasToAdd_MC_Full2022v12.py)

---

### 1.5 `puWeight` — Pileup Reweighting Weight
**Definition:** Per-event weight that corrects for the mismatch between the simulated pileup distribution and the observed distribution in data. It is computed as the ratio of the data pileup profile (derived from the measured instantaneous luminosity and a total inelastic cross-section of 69.2 mb) to the MC pileup profile (`Pileup_nTrueInt`), with optional ±4.6% cross-section variations for systematic uncertainties.

**Why needed:** MC samples are produced with a fixed assumed pileup scenario. If the actual data pileup (average number of additional pp collisions per bunch crossing, ~30–40 in Run 3) differs from the simulation, observables such as jet multiplicity, missing transverse energy, and lepton isolation are incorrectly modelled. `puWeight` corrects this event-by-event.

**Source:** [`mkShapesRDF/processor/data/PUWeight_cfg.py`](https://github.com/latinos/mkShapesRDF/blob/Run3/mkShapesRDF/processor/data/PUWeight_cfg.py)

---

### 1.6 `SFweight2l` — Combined 2-Lepton Scale Factor Weight
**Definition:**
```
SFweight2l = puWeight
           * (HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL
              || HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL
              || HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ
              || HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8
              || HLT_IsoMu24
              || HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL
              || HLT_Ele35_WPTight_Gsf)
           * TriggerSFWeight_2l
           * Lepton_RecoSF[0] * Lepton_RecoSF[1]
```
The full list of trigger paths is defined in
[`mkShapesRDF/processor/modules/formulasToAdd_MC_Full2022v12.py`](https://github.com/latinos/mkShapesRDF/blob/Run3/mkShapesRDF/processor/modules/formulasToAdd_MC_Full2022v12.py).

Components:
- **`puWeight`**: see §1.5.
- **Trigger bits** (logical OR of all paths above): applies the actual online trigger decision to MC, ensuring only MC events that would have fired the trigger in data are kept.
- **`TriggerSFWeight_2l`**: data/MC ratio of trigger efficiencies for the dilepton event (see §2.1).
- **`Lepton_RecoSF[0/1]`**: per-lepton reconstruction scale factor, correcting for differences in track-to-GSF-electron or tracker-muon reconstruction efficiency between data and MC (see §2.3).

**Why needed:** Combines all event-level corrections that depend on having exactly two reconstructed leptons. Applied to all MC samples.

**Source:** [`mkShapesRDF/processor/modules/formulasToAdd_MC_Full2022v12.py`](https://github.com/latinos/mkShapesRDF/blob/Run3/mkShapesRDF/processor/modules/formulasToAdd_MC_Full2022v12.py)

---

### 1.7 `LepWPCut` — Lepton Working-Point Selection Cut
**Definition:**
```python
LepWPCut = LepCut2l__ele_cutBased_LooseID_tthMVA_Run3__mu_cut_TightID_pfIsoTight_HWW_tthmva_67
```
A boolean flag (0 or 1) requiring both reconstructed leptons to pass the analysis-specific tight identification and isolation working points:
- **Electrons:** `cutBased_LooseID_tthMVA_Run3` — cut-based Loose ID combined with the ttH MVA (Run 3 version).
- **Muons:** `cut_TightID_pfIsoTight_HWW_tthmva_67` — cut-based Tight ID with PF tight isolation and HWW-specific ttH MVA score > 0.67.

**Why needed:** The standard NanoAOD lepton selection (`l2loose`) is intentionally loose; this cut enforces the tighter analysis-specific selection and is applied to both data and MC to ensure a consistent selection. Its application to data replaces the need to reprocess the data.

---

### 1.8 `LepWPSF` — Lepton Working-Point Scale Factor
**Definition:**
```python
LepWPSF = LepSF2l__ele_cutBased_LooseID_tthMVA_Run3__mu_cut_TightID_pfIsoTight_HWW_tthmva_67
        = (Lepton_tightElectron_eleWP_IdIsoSF[0]
           * Lepton_tightElectron_eleWP_IdIsoSF[1]
           * Lepton_tightMuon_muWP_IdIsoSF[0]
           * Lepton_tightMuon_muWP_IdIsoSF[1])
```
Product of per-lepton ID+isolation scale factors for both leptons. Each `Lepton_tightXxx_YYY_IdIsoSF` is itself a product of individual ID and isolation SFs derived from tag-and-probe measurements in Z→ll events (see §2.2).

**Why needed:** The probability for a real lepton to pass the tight WP differs between data and MC (MC typically overestimates the lepton ID efficiency). `LepWPSF` corrects for this mismatch event-by-event. Applied only to MC.

---

### 1.9 `PromptGenLepMatch2l` — Generator-Level Prompt Lepton Matching
**Definition:**
```python
PromptGenLepMatch2l = Alt(Lepton_promptgenmatched, 0, 0) * Alt(Lepton_promptgenmatched, 1, 0)
```
A boolean flag (0 or 1) requiring both reconstructed leptons to be matched to a prompt generator-level lepton (i.e. a lepton not originating from hadron decay). `Lepton_promptgenmatched` is set by [`mkShapesRDF/processor/modules/GenLeptonMatchProducer.py`](https://github.com/latinos/mkShapesRDF/blob/Run3/mkShapesRDF/processor/modules/GenLeptonMatchProducer.py).

**Why needed:** Without this requirement, reconstructed leptons in MC that are fakes (from non-prompt sources such as heavy-flavour decays, conversions, or jets) would be treated the same as real signal leptons. This contaminates MC predictions with contributions that are instead modelled by the data-driven fake background estimation. Applied only to MC.

---

### 1.10 `SFweight` — Total Scale Factor Weight
**Definition:**
```python
SFweight = SFweight2l * LepWPCut * LepWPSF
```
The master per-event weight for MC simulation, combining pileup, trigger, lepton reconstruction, and lepton ID/isolation corrections. Applied only to MC.

---

### 1.11 `mcCommonWeight` — Complete MC Event Weight
**Definition:**
```python
mcCommonWeight = XSWeight * METFilter_Common * PromptGenLepMatch2l * SFweight
```
This is the weight string applied to the `weight` field of all MC samples in `samples.py`. It encodes the full chain of corrections:
`(cross-section normalisation) × (data-quality filters) × (prompt-lepton requirement) × (pileup + trigger + lepton corrections)`.

---

### 1.12 `DY_LO_ZpTrw` — Drell-Yan Z pT Reweighting
**Definition:**
```python
DY_LO_ZpTrw = (norm_factor * fit_func(gen_Zpt)) * (zeroJet) * (ptll < 50)
             + 1 * (zeroJet) * (ptll >= 50)
```
where `fit_func` is a parameterised function (error-function + polynomial) fitted to the ratio of (background-subtracted data) / (DY MC) as a function of `ptll` in the Z peak region, derived by `extract_Zptrw.py`.

**Why needed:** LO Drell-Yan Monte Carlo generators (e.g. `DYJetsToLL_M-50-LO`) do not include higher-order resummation effects (Sudakov logarithms) that dominate the Z boson pT spectrum at low pT (≲ 30 GeV). This causes the LO Z pT distribution to be harder than observed in data. The reweighting corrects the LO MC spectrum to match data, which is particularly important for analyses relying on the Z pT distribution as a control or background process.

Applied only to the `DY` sample, and only in the 0-jet category (`zeroJet`) and for `ptll < 50 GeV` where the resummation effects are largest.

---

## 2. Scale Factors (Component Detail)

### 2.1 Trigger Scale Factor (`TriggerSFWeight_2l`)
**Definition:** Per-event data/MC ratio of the probability for the event to fire at least one of the dilepton or single-lepton HLT trigger paths:
```
TriggerSFWeight_2l = P(trigger | data) / P(trigger | MC)
```
This is computed event-by-event using per-leg trigger efficiencies measured in data and MC (from tag-and-probe in Z→ll), combined following the standard OR-of-triggers formula:
```
P(at least one HLT fires) = 1 − ∏ᵢ [1 − ε_leg1(i) × ε_leg2(i)]
```
Uncertainty variations `TriggerSFWeight_2l_u` and `TriggerSFWeight_2l_d` propagate measurement uncertainties on the per-leg efficiencies.

**Source:** [`mkShapesRDF/processor/modules/TrigMaker.py`](https://github.com/latinos/mkShapesRDF/blob/Run3/mkShapesRDF/processor/modules/TrigMaker.py), [`mkShapesRDF/processor/data/TrigMaker_cfg.py`](https://github.com/latinos/mkShapesRDF/blob/Run3/mkShapesRDF/processor/data/TrigMaker_cfg.py)

---

### 2.2 Lepton ID+Isolation Scale Factor (`Lepton_tightXxx_YYY_IdIsoSF`)
**Definition:** Per-lepton data/MC ratio of the probability for a reconstructed lepton to pass the analysis tight WP:
```
IdIsoSF = ε_ID+iso(data) / ε_ID+iso(MC)
```
Measured with tag-and-probe in Z→ee (electrons) and Z→μμ (muons), binned in lepton pT and η. The product over both leptons gives `LepWPSF`.

Up/Down variations (`LepSF2l__ele_eleWP__Up/Down`, `LepSF2l__mu_muWP__Up/Down`) shift all lepton SFs coherently by their uncertainty (typically 0.5–2% per lepton).

**Source:** [`mkShapesRDF/processor/data/LeptonSel_cfg.py`](https://github.com/latinos/mkShapesRDF/blob/Run3/mkShapesRDF/processor/data/LeptonSel_cfg.py), [`mkShapesRDF/processor/data/scale_factor/`](https://github.com/latinos/mkShapesRDF/tree/Run3/mkShapesRDF/processor/data/scale_factor)

---

### 2.3 Lepton Reconstruction Scale Factor (`Lepton_RecoSF`)
**Definition:** Per-lepton data/MC ratio for the probability to reconstruct a lepton from a generator-level particle (i.e. track reconstruction, GSF electron building, or global muon fit). Applied inside `SFweight2l`.

**Why separate from IdIsoSF:** The reconstruction step (converting detector hits to a lepton candidate) is factored from the identification step (applying analysis cuts to the candidate) because they have different dependencies on pT and η.

---

### 2.4 B-Tagging Scale Factor (`bVetoSF`, `bReqSF`)
**Definition:**
```python
bVetoSF = TMath::Exp(Sum(LogVec(
    (CleanJet_pt>20 && |eta|<2.5) * Jet_btagSF_deepjet_shape[jetIdx]
  + 1 * (CleanJet_pt<20 || |eta|>2.5)
)))
```
The product of per-jet b-tagging scale factors for all jets in the event, implemented as an exponentiated sum of logarithms for numerical stability. The `btagSF_deepjet_shape` is a per-jet reweighting derived by the CMS BTV POG to make the b-tagging discriminant distribution in MC match data.

**Note:** b-tagging SFs are currently commented out in `aliases.py` for ZpTreweighting. This is consistent with the DY control-region configuration (`ControlRegions/DY/2022_v12/aliases.py`), which also omits them, since the analysis operates in the 0-jet signal region where b-tagged jets are vetoed and the jet multiplicity is low enough that b-tagging SFs have a minimal effect.

**Source:** [`mkShapesRDF/processor/data/scale_factors_BTV/`](https://github.com/latinos/mkShapesRDF/tree/Run3/mkShapesRDF/processor/data/scale_factors_BTV)

---

## 3. Nuisances (Systematic Uncertainties)

| Key | Name | Type | Samples | Description |
|-----|------|------|---------|-------------|
| `lumi_2022` | `lumi_2022` | lnN 1.014 | all MC | ±1.4% uncertainty on the 2022 (pre-EE) integrated luminosity of 8.17 fb⁻¹. Reference: [CMS Lumi TWiki](https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun3). |
| `stat` | auto | auto | all MC | Automatic bin-by-bin MC statistical uncertainties (Poisson or Gaussian depending on bin content). |
| `PU` | `CMS_pileup_2022` | lnN 1.05 | all MC | ±5% normalisation from uncertainty in the pileup reweighting, driven by the ±4.6% uncertainty on the total inelastic pp cross-section (69.2 mb). |
| `trigg` | `CMS_eff_hwwtrigger_2022` | shape | all MC | Uncertainty on `TriggerSFWeight_2l`, obtained by varying the per-leg trigger efficiencies within their measurement uncertainties. Affects normalisation and shape of all MC processes. |
| `eff_e` | `CMS_eff_e_2022` | shape | all MC | Uncertainty on the electron ID+isolation SF (`LepWPSF` electron component), computed from tag-and-probe uncertainties in Z→ee. Uses `SFweightEleUp/Down` aliases. |
| `eff_m` | `CMS_eff_m_2022` | shape | all MC | Uncertainty on the muon ID+isolation SF (`LepWPSF` muon component), computed from tag-and-probe uncertainties in Z→μμ. Uses `SFweightMuUp/Down` aliases. |
| `PS_ISR` | `ps_isr` | shape | all MC | Parton shower ISR variation: `PSWeight[2]` (up) and `PSWeight[0]` (down). Affects the Z pT and jet multiplicity spectra, especially relevant for DY. |
| `PS_FSR` | `ps_fsr` | shape | all MC | Parton shower FSR variation: `PSWeight[3]` (up) and `PSWeight[1]` (down). Affects lepton isolation and jet activity from QED/QCD radiation. |
| `QCDscale_DY` | `QCDscale_DY` | shape | DY | Envelope of renormalisation/factorisation scale variations (`LHEScaleWeight[0]` and `LHEScaleWeight[nLHEScaleWeight-1]`) for the Drell-Yan sample. Directly affects the Z pT shape and therefore the derived reweighting. |
| `QCDscale_top` | `QCDscale_ttbar` | shape | top | Same QCD scale envelope for top-quark background samples, affecting the background subtraction from data. |

---

## 4. Complete Weight Chain Summary

For a MC event, the full event weight is:
```
w_event = XSWeight
        × METFilter_Common
        × PromptGenLepMatch2l
        × SFweight
        × DY_LO_ZpTrw           (DY sample only)
        × lumi                   (= configuration.py lumi, applied externally)
```
where
```
XSWeight           = baseW × genWeight
SFweight           = SFweight2l × LepWPCut × LepWPSF
SFweight2l         = puWeight × HLT_OR × TriggerSFWeight_2l × Lepton_RecoSF[0] × Lepton_RecoSF[1]
LepWPSF            = LepSF2l__ele_eleWP__mu_muWP
DY_LO_ZpTrw        = norm × f(gen_Zpt) × (zeroJet) × (ptll<50) + 1×(zeroJet)×(ptll≥50)
```

For data events:
```
w_event = LepWPCut × METFilter_DATA × DataTrig[primaryDataset]
```