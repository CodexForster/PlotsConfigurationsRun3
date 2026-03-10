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

---

## 5. Jet Scale Factors — Complete Reference

This section documents **all jet-related scale factors and systematic uncertainties** found across the repository. They are grouped by category; where the ZpTreweighting folder currently applies (or could apply) a given SF, that is noted explicitly.

---

### 5.1 Jet Energy Corrections Applied in Pre-Processing (`MCCorr2022v12JetScaling`)

Before any analysis is run, jets in MC already receive standard CMS Jet Energy Corrections (JEC) as part of the NanoAOD production step encoded in the `mcSteps` string. For all Run3 2022 analyses in this repository (including ZpTreweighting), the MC processing step is:

```
MCl2loose2022v12__MCCorr2022v12JetScaling__l2tight
```

The `MCCorr2022v12JetScaling` step applies:
- **JEC (Jet Energy Corrections / JES):** Factory-calibrated L1FastJet + L2Relative + L3Absolute corrections that bring simulated jet pT to the correct absolute energy scale, using the JME POG global tag (e.g. `Summer22_22Sep2023_V2_MC` for 2022).
- **JER (Jet Energy Resolution) smearing:** Stochastic smearing of MC jet pT to match the broader resolution observed in data, based on the JME POG resolution maps (e.g. `JR_Winter22Run3_V1_MC`).

These corrections are applied in-situ (inside the NanoAOD post-processing) so that `CleanJet_pt` in the analysis already reflects corrected jets. They are not an event weight but a per-jet four-vector rescaling.

**Relevant runner code:** `WW_Run3/runner.py`, `ControlRegions/DY/2022/runner.py` (the `recomputeJets` method, which applies JEC/JER and jet-veto-map masks on top of NanoAOD jets using `correctionlib` JSON files).

---

### 5.2 Jet Energy Scale (JES) Systematic Uncertainties

**What it is:** The JES uncertainty accounts for residual calibration uncertainties in the jet energy scale. It is implemented by varying all jet four-momenta (pT, and propagated to MET) simultaneously up and down according to each uncertainty source.

**How it is applied:** `suffix` shape nuisance — separate MC samples (or RDF variations) are produced with up/down-varied jets, and the analysis is re-run on those.

**JES sources in Run 3 (reduced set of 11, used in most Run3 analyses like `ControlRegions/3l/2022_v12`):**

| Source | Year tag | CMS nuisance name | Correlation |
|--------|----------|-------------------|-------------|
| `Absolute` | run-independent | `CMS_scale_j_Absolute` | fully correlated across years |
| `Absolute_2022` | 2022-specific | `CMS_scale_j_Absolute_2022` | decorrelated |
| `FlavorQCD` | run-independent | `CMS_scale_j_FlavorQCD` | fully correlated |
| `BBEC1` | run-independent | `CMS_scale_j_BBEC1` | fully correlated |
| `BBEC1_2022` | 2022-specific | `CMS_scale_j_BBEC1_2022` | decorrelated |
| `EC2` | run-independent | `CMS_scale_j_EC2` | fully correlated |
| `EC2_2022` | 2022-specific | `CMS_scale_j_EC2_2022` | decorrelated |
| `HF` | run-independent | `CMS_scale_j_HF` | fully correlated |
| `HF_2022` | 2022-specific | `CMS_scale_j_HF_2022` | decorrelated |
| `RelativeBal` | run-independent | `CMS_scale_j_RelativeBal` | fully correlated |
| `RelativeSample_2022` | 2022-specific | `CMS_scale_j_RelativeSample_2022` | decorrelated |

For older analyses (Run 2 / UL, e.g. `WH_chargeAsymmetry`, `VBF_differential`, `VBS_OS_pol`), a different grouping is used (e.g. `JESAbsolute`, `JESBBEC1`, `JESEC2`, `JESFlavorQCD`, `JESHF`, `JESRelativeBal`, `JESRelativeSample_{year}`).

**Why needed:** Different physical effects cause the jet energy scale to deviate from perfect calibration. The sources above are factorised to decorrelate run-period-specific effects from effects correlated across all data-taking periods, enabling proper combination of multiple years. JES variations also propagate to MET (through the recoil).

**Example configuration:** `ControlRegions/3l/2022_v12/nuisances.py`, `HWW/ggH_SF/2022/nuisances.py`

**Status in ZpTreweighting:** JES is mentioned in a comment in `aliases.py` (`# using Alt(CleanJet_pt, n, 0) instead of Sum(CleanJet_pt >= 30) because jet pt ordering is not strictly followed in JES-varied samples`), but JES nuisances are **not currently added** to `ZpTreweighting/nuisances.py`. Since ZpTreweighting uses the 0-jet category as signal region, JES primarily shifts the jet multiplicity rather than the key observables, but it should be considered for the background subtraction.

---

### 5.3 Jet Energy Resolution (JER) Systematic Uncertainty

**What it is:** The JER uncertainty accounts for the fact that the MC jet pT smearing (applied to match the broader data resolution) may not be perfectly calibrated. It is implemented by varying the smearing amount up and down.

**How it is applied:** `suffix` shape nuisance — up/down-varied jet collections are used.

**Run3 approach (split by η regions):**

In `ControlRegions/WZ/2022EE_v12`, `WH_SS/2022EE`, `ControlRegions/DY/2022/nuisances_ALL.py`, and related files, JER is split into 6 η-region nuisances to allow decorrelation:

```python
jer_syst = ["JER_0", "JER_1", "JER_2", "JER_3", "JER_4", "JER_5"]
# CMS names: CMS_res_JER_0_j, ..., CMS_res_JER_5_j
```

**Run3 simplified approach (single JER, used in HWW/3l/ZpTreweighting-adjacent analyses):**

```python
nuisances['JER'] = {
    'name': 'CMS_res_j_2022',
    'kind': 'suffix', 'type': 'shape',
    'mapUp': 'jerup', 'mapDown': 'jerdo',
    'folderUp': makeMCDirectory('jerup_suffix'),
    'folderDown': makeMCDirectory('jerdo_suffix'),
}
```

**Run 2 approach:** Single `JER` nuisance, e.g. `CMS_res_j_2016`, `CMS_res_j_2017`, `CMS_res_j_2018`.

**Why needed:** MC jets are narrower than data jets because the simulation does not fully reproduce detector noise and pile-up contributions to jet energy. JER smearing corrects this but introduces an uncertainty from the measurement of the resolution in data.

**Example configuration:** `ControlRegions/3l/2022_v12/nuisances.py`, `HWW/ggH_SF/2022/nuisances.py`

**Status in ZpTreweighting:** **Not currently in `nuisances.py`.** Should be added for the background samples (see §5.9).

---

### 5.4 Unclustered Energy / MET Scale (`CMS_scale_met`)

**What it is:** Jet energy corrections are propagated to MET, but energy from soft particles not clustered into jets ("unclustered energy") introduces an additional MET uncertainty. It is implemented by varying `PuppiMET_pt` up and down by shifting unclustered energy.

**How it is applied:** `suffix` shape nuisance:

```python
nuisances['MET'] = {
    'name': 'CMS_scale_met_2022',
    'kind': 'suffix', 'type': 'shape',
    'mapUp': 'unclustEnup', 'mapDown': 'unclustEndo',
    'folderUp': makeMCDirectory('unclustEnup_suffix'),
    'folderDown': makeMCDirectory('unclustEndo_suffix'),
}
```

**Why needed:** MET is sensitive to all particles in the event. Soft unclustered energy (particles below the jet threshold) is not corrected by JES/JER and has its own calibration uncertainty.

**Example configuration:** `ControlRegions/3l/2022_v12/nuisances.py`, `HWW/ggH_SF/2022/nuisances.py`

**Status in ZpTreweighting:** **Not currently in `nuisances.py`.** The ZpTreweighting analysis does not make a hard cut on MET, so its impact on `ptll` is small, but it should in principle be included for completeness.

---

### 5.5 Jet Veto Map (`jetvetomaps`)

**What it is:** A 2D map in (η, φ) that flags jets reconstructed in regions of the CMS detector with known hot cells, dead channels, or other noise sources during specific run ranges. Jets falling in a vetoed region are removed from the jet collection before analysis.

**How it is applied:** Not an event weight; it is a boolean mask on jets applied inside the `recomputeJets` function in the runner scripts. The map is read from a `correctionlib` JSON file:

```python
pathToJson = ".../jetvetomaps/Run2022/jetvetomaps.json"
globalTag  = "Summer22_23Sep2023_RunCD_V1"    # for 2022 pre-EE
globalTag  = "Summer22EE_23Sep2023_RunEFG_V1" # for 2022 post-EE
```

A jet is vetoed if it falls in a masked (η, φ) cell (evaluated via `getJetMask` C++ function in the runner).

**Why needed:** Detector problems in certain η–φ regions during specific run periods cause fake jets with anomalously high pT or energy fractions. These must be removed to avoid biasing jet-based observables.

**Example configuration:** `WW_Run3/runner.py`, `ControlRegions/DY/2022/runner.py`, `LeptonID/2022/runner.py`

**Status in ZpTreweighting:** The jet veto map is applied at the NanoAOD processing level (`MCCorr2022v12JetScaling`) so it is already accounted for in the sample files used by ZpTreweighting. No additional alias or nuisance is needed in the analysis configuration.

---

### 5.6 Jet Horn Veto (`noJetInHorn`)

**What it is:** An additional selection removing events with jets in the "horn" region of the CMS calorimeter (2.6 < |η| < 3.1, 30 < pT < 50 GeV) where the ECAL endcap meets the HF calorimeter, causing anomalous jet reconstruction in certain run periods.

**How it is applied:** Boolean alias in `aliases.py`, applied as part of preselection or as a selection category:

```python
aliases['noJetInHorn'] = {
    'expr': 'Sum(CleanJet_pt > 30 && CleanJet_pt < 50 && abs(CleanJet_eta) > 2.6 && abs(CleanJet_eta) < 3.1) == 0',
}
```

**Why needed:** The calorimeter transition region has large jet energy resolution and a high fake-jet rate. Requiring no jet in this region makes the analysis more stable against instrumental effects.

**Example configuration:** Defined in `ZpTreweighting/aliases.py`; applied in `WH_SS/2023/aliases.py`, `ControlRegions/SS/2022_v12/aliases.py`.

**Status in ZpTreweighting:** The alias is defined in `aliases.py` but not applied in the preselection (replaced by `zeroJet`). A comment in `cuts.py` states "noJetInHorn replaced by zeroJet".

---

### 5.7 B-Tagging Scale Factors

B-tagging SFs correct the per-jet probability to pass a b-tagging discriminant threshold, accounting for differences between data and MC b-tag efficiencies and mistag rates. There are two main approaches used in this repository:

#### 5.7.1 Shape Reweighting (`btagSF_deepjet_shape`) — Run 2 / WW\_Run3

Used in `WW_Run3`, `WH_chargeAsymmetry` (UL), `ControlRegions/WZ`, older HWW analyses, and VBS/VBF (Run2) analyses. The per-jet NanoAOD branch `Jet_btagSF_{algo}_shape` contains a weight that reweights the full b-discriminant shape in MC to match data. The event-level SF is the product of all per-jet weights:

```python
bVetoSF = TMath::Exp(Sum(LogVec(
    (CleanJet_pt>20 && |eta|<2.5) * Jet_btagSF_{algo}_shape[jetIdx]
  + 1*(CleanJet_pt<20 || |eta|>2.5)
)))
bReqSF  = TMath::Exp(Sum(LogVec(
    (CleanJet_pt>30 && |eta|<2.5) * Jet_btagSF_{algo}_shape[jetIdx]
  + 1*(CleanJet_pt<30 || |eta|>2.5)
)))
btagSF  = (bVeto || (topcr && zeroJet))*bVetoSF + (topcr && !zeroJet)*bReqSF
```

Systematic variations use up/down-shifted versions: `btagSF_deepjet_shape_up_{source}` / `btagSF_deepjet_shape_down_{source}` for sources `jes, lf, hf, lfstats1, lfstats2, hfstats1, hfstats2, cferr1, cferr2` (currently commented out in most Run3 analyses and replaced by the fixed-WP approach below).

**Algorithms and SF branch names:**
- DeepJet / DeepFlavB: `Jet_btagSF_deepjet_shape`
- ParticleNet (PNetB): `Jet_btagSF_particleNet_shape` (NanoAOD branch uses `partNet` prefix: `Jet_btagSF_partNet_shape`)
- RobustParTAK4B: `Jet_btagSF_robustParticleTransformer_shape` (NanoAOD branch uses `partTransformer` prefix: `Jet_btagSF_partTransformer_shape`)

#### 5.7.2 Fixed-WP Efficiency × SF Method (`btagSFbc`, `btagSFlight`) — Run3 standard

Used in `HWW` (2022, 2022EE, 2023, 2023BPix), `ControlRegions/3l` (2022\_v12, 2022EE\_v12, 2023\_v12, 2023BPix\_v12, 2024\_v15), `ControlRegions/WZ`, and related Run3 analyses. This method explicitly computes efficiency-weighted event-level SFs using correctionlib POG JSON files, split by jet flavour:

- **`btagSFbc`** — covers b-jets and c-jets (heavy flavour), evaluated using `btagSF{bc}_{shift}(...)` (defined by `evaluate_btagSFbc.cc` macro).
- **`btagSFlight`** — covers light-flavour jets (udsg), evaluated using `btagSF{light}_{shift}(...)` (defined by `evaluate_btagSFlight.cc` macro).

The aliases loop over shifts:
```python
for flavour in ['bc', 'light']:
    for shift in ['central', 'up_uncorrelated', 'down_uncorrelated', 'up_correlated', 'down_correlated']:
        aliases[f'btagSF{flavour}_{shift}'] = { ... }
```

The combined SF weight is:
```python
SFweight = SFweight2l * LepWPCut * LepWPSF * btagSFbc * btagSFlight
```

**Available taggers and WPs** (from `aliases.py` dictionaries):

| Tagger | Code name | Loose WP (2022) | Medium WP (2022) | Tight WP (2022) |
|--------|-----------|-----------------|------------------|-----------------|
| DeepJet / DeepFlavB | `deepjet` | 0.0583 | 0.3086 | 0.7183 |
| ParticleNet (PNetB) | `particleNet` | 0.0470 | 0.2450 | 0.6734 |
| RobustParTAK4B | `robustParticleTransformer` | 0.0849 | 0.4319 | 0.8482 |

**Systematic nuisances for fixed-WP approach** (in nuisances.py):

```python
for flavour in ['bc', 'light']:
    for corr in ['uncorrelated', 'correlated']:
        # correlated: same across years (e.g. CMS_btagSFbc_correlated)
        # uncorrelated: year-specific (e.g. CMS_btagSFbc_2022, CMS_btagSFlight_2022)
        nuisances[f'btagSF{flavour}{corr}'] = {
            'name': f'CMS_btagSF{flavour}_{corr}',   # or CMS_btagSF{flavour}_{year}
            'kind': 'weight', 'type': 'shape',
            'samples': { skey: [f'btagSF{flavour}_up_{corr}/btagSF{flavour}',
                                 f'btagSF{flavour}_down_{corr}/btagSF{flavour}'] for skey in mc }
        }
```

This yields 4 nuisance parameters per epoch:
- `CMS_btagSFbc_correlated` — b/c-jet SF uncertainty correlated across all years
- `CMS_btagSFbc_2022` — b/c-jet SF uncertainty decorrelated per year (Run3 2022)
- `CMS_btagSFlight_correlated` — light-jet SF uncertainty correlated across all years
- `CMS_btagSFlight_2022` — light-jet SF uncertainty decorrelated per year (Run3 2022)

**Source:** [`mkShapesRDF/processor/data/scale_factors_BTV/`](https://github.com/latinos/mkShapesRDF/tree/Run3/mkShapesRDF/processor/data/scale_factors_BTV), `ControlRegions/3l/2022_v12/macros/evaluate_btagSFbc.cc`, `evaluate_btagSFlight.cc`

**Status in ZpTreweighting:** The b-tagging SF aliases (`bVetoSF`, `bReqSF`, `btagSF`) are **commented out** in `aliases.py`, and the b-tagging nuisances are **not in `nuisances.py`**. This is consistent with the DY control region configuration. For the 0-jet category used in ZpTreweighting, the effect is small, but if b-enriched categories or a full Run3 HWW-style analysis is performed with this configuration, the fixed-WP `btagSFbc`/`btagSFlight` approach should be adopted.

---

### 5.8 Jet Pileup ID Scale Factor (`jetPUID`, `Jet_PUIDSF`)

**What it is:** A weight that corrects the efficiency of the CMS Pileup Jet ID (PUID) discriminant, which distinguishes genuine hard-scatter jets from fake jets created by pileup collisions. The SF is:

```
Jet_PUIDSF = ε_PUJET(data) / ε_PUJET(MC)
```

**How it is applied:** Event-level weight, computed as the product of per-jet PUIDSF:

```python
# Alias (WH_chargeAsymmetry and VBF-type analyses):
aliases['Jet_PUIDSF'] = {
    'expr': 'TMath::Exp(Sum((Jet_jetId>=2)*LogVec(Jet_PUIDSF_loose)))',
    'samples': mc
}
# Variations:
aliases['Jet_PUIDSF_up']   = { 'expr': 'TMath::Exp(Sum((Jet_jetId>=2)*LogVec(Jet_PUIDSF_loose_up)))', ... }
aliases['Jet_PUIDSF_down'] = { 'expr': 'TMath::Exp(Sum((Jet_jetId>=2)*LogVec(Jet_PUIDSF_loose_down)))', ... }

# Nuisance:
puid_syst = ['Jet_PUIDSF_up/Jet_PUIDSF', 'Jet_PUIDSF_down/Jet_PUIDSF']
nuisances['jetPUID'] = {
    'name': 'CMS_PUID_{year}',
    'kind': 'weight', 'type': 'shape',
    'samples': dict((skey, puid_syst) for skey in mc)
}
```

**Why needed:** Pileup jets have different shower and track characteristics from hard-scatter jets. PUJET ID suppresses them, but the efficiency differs between data and MC, requiring a correction. This is most important in analyses with many jets or VBF-like topologies.

**Run3 status:** In the Run3 framework (`NanoAODv12`), the Pileup Jet ID is not typically applied in the 0-jet / low-jet-multiplicity regime. It appears primarily in VBF, VBS, and WH analyses where forward jet identification is critical.

**Example configuration:** `VBF_differential/Full2017_v9/nuisances.py`, `VBS_OS_pol/Full2016noHIPM_v9/nuisances.py`, `WH_chargeAsymmetry/UL/Full2017_v9/WH3l/aliases.py`

**Status in ZpTreweighting:** **Not needed.** ZpTreweighting uses the 0-jet category and does not require PUJET ID.

---

### 5.9 Summary Table: All Jet Scale Factors

| Scale Factor | Key in nuisances | CMS name | Kind | Type | Applied to | Status in ZpTreweighting |
|-------------|-----------------|----------|------|------|------------|--------------------------|
| **JES** (total, single source) | `JES` | `CMS_scale_j_2022` | suffix | shape | all MC jets | ❌ Not in nuisances.py |
| **JES** (split, 11 sources) | `Absolute`, `Absolute_2022`, `FlavorQCD`, `BBEC1`, `BBEC1_2022`, `EC2`, `EC2_2022`, `HF`, `HF_2022`, `RelativeBal`, `RelativeSample_2022` | `CMS_scale_j_{source}` | suffix | shape | all MC jets | ❌ Not in nuisances.py |
| **JER** (single) | `JER` | `CMS_res_j_2022` | suffix | shape | all MC jets | ❌ Not in nuisances.py |
| **JER** (split, 6 η bins) | `JER_0`–`JER_5` | `CMS_res_JER_{n}_j` | suffix | shape | all MC jets | ❌ Not in nuisances.py |
| **MET unclustered energy** | `MET` | `CMS_scale_met_2022` | suffix | shape | all MC | ❌ Not in nuisances.py |
| **Jet veto map** | — (mask, not a weight) | — | mask | — | data+MC jets | ✅ Applied in pre-processing |
| **Jet horn veto** | — (selection cut) | — | cut | — | all | ⚠️ Defined but replaced by zeroJet |
| **b-tag SF (shape, deepjet)** | `bVetoSF`, `bReqSF`, `btagSF` | — (deprecated in Run3) | weight | shape | all MC jets | ❌ Commented out |
| **b-tag SF (fixed-WP, bc)** | `btagSFbc` | `CMS_btagSFbc_correlated` / `CMS_btagSFbc_2022` | weight | — | all MC jets | ❌ Not implemented |
| **b-tag SF (fixed-WP, light)** | `btagSFlight` | `CMS_btagSFlight_correlated` / `CMS_btagSFlight_2022` | weight | — | all MC jets | ❌ Not implemented |
| **b-tag SF bc nuisance (corr.)** | `btagSFbccorrelated` | `CMS_btagSFbc_correlated` | weight | shape | all MC | ❌ Not in nuisances.py |
| **b-tag SF bc nuisance (uncorr.)** | `btagSFbcuncorrelated` | `CMS_btagSFbc_2022` | weight | shape | all MC | ❌ Not in nuisances.py |
| **b-tag SF light nuisance (corr.)** | `btagSFlightcorrelated` | `CMS_btagSFlight_correlated` | weight | shape | all MC | ❌ Not in nuisances.py |
| **b-tag SF light nuisance (uncorr.)** | `btagSFlightuncorrelated` | `CMS_btagSFlight_2022` | weight | shape | all MC | ❌ Not in nuisances.py |
| **Pileup Jet ID SF** | `jetPUID` | `CMS_PUID_{year}` | weight | shape | MC jets (pT<50) | ➖ Not needed for 0-jet ZpTrw |

**Legend:** ✅ Applied, ❌ Not applied (but potentially relevant), ⚠️ Partially applied, ➖ Not applicable

---

### 5.10 Recommendation for ZpTreweighting

Given that ZpTreweighting is focused on deriving the Z pT reweighting function using the 0-jet category, the most relevant jet SFs to add are:

1. **JER** (`CMS_res_j_2022`): The JER affects the efficiency of the 0-jet veto (`zeroJet = Alt(CleanJet_pt, 0, 0) < 30`) by smearing jets near the 30 GeV threshold. This is directly relevant.
2. **JES** (at least the total or the 11-source split): JES shifts change the jet pT threshold, affecting the 0-jet efficiency similarly to JER.
3. **MET unclustered energy** (`CMS_scale_met_2022`): Less critical for ZpTreweighting (no MET cut), but propagates to pTll via the hadronic recoil in some variables.
4. **b-tag SF (fixed-WP)**: Relevant only if b-enriched control regions are used for background subtraction (currently not). Can remain commented out.

Example nuisances to add to `ZpTreweighting/nuisances.py` (following `HWW/ggH_SF/2022/nuisances.py`):
```python
nuisances['JER'] = {
    'name': 'CMS_res_j_2022', 'skipCMS': 1,
    'kind': 'suffix', 'type': 'shape',
    'mapUp': 'jerup', 'mapDown': 'jerdo',
    'samples': dict((skey, ['1', '1']) for skey in mc),
    'folderUp': makeMCDirectory('jerup_suffix'),
    'folderDown': makeMCDirectory('jerdo_suffix'),
    'AsLnN': '0'
}
nuisances['JES'] = {
    'name': 'CMS_scale_j_2022', 'skipCMS': 1,
    'kind': 'suffix', 'type': 'shape',
    'mapUp': 'jesTotalup', 'mapDown': 'jesTotaldo',
    'samples': dict((skey, ['1', '1']) for skey in mc),
    'folderUp': makeMCDirectory('jesTotalup_suffix'),
    'folderDown': makeMCDirectory('jesTotaldo_suffix'),
    'AsLnN': '0'
}
```