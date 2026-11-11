cuts = {}

# WZ control regions for ZH(->WW) -> 3l (Z->ll, W->lnu, W->jj)
# Same definitions as the Run 2 ZH3l analysis (PlotsConfigurations/Configurations/ZH3l/Full2018_v7/cuts.py):
# the signal region requires dphi(l+MET, jj) < pi/2 (dphi(l+MET, j) < pi/2 in the 1-jet bin), the WZ CR inverts it.
# NEW w.r.t. WZ/2022_v12: the signal region is also defined (bottom of the file).
#
# Variables used below (mkShapesRDF):
#
#   Lepton_pt       = pT of the leptons in the Lepton collection, ordered in pT (index 0 = leading).
#                     Alt(Lepton_pt, i, 0) returns 0 if there is no i-th lepton, so
#                     Alt(Lepton_pt,3,0) < 10 vetoes a 4th lepton with pT > 10 GeV
#   PuppiMET_pt     = PUPPI missing transverse momentum (nanoAOD)
#   bVeto           = alias (aliases.py): no CleanJet with pT > 20 GeV, |eta| < 2.5 passing the DeepFlavB loose WP
#
#   From mkShapesRDF/processor/modules/l3KinProducer.py, computed with the three leading leptons
#   (massless 4-vectors, mZ = 91.1876 GeV, MET = PUPPI MET). They are only filled when the event has
#   >= 3 leptons with |sum of charges| <= 1, otherwise they get default values (-9999 or 9999):
#
#   WH3l_mOSll[3]   = m(ll) of the pairs (0,1), (0,2), (1,2) if opposite-sign (any flavour), -9999 otherwise.
#                     "< 0 || > 12" removes low-mass resonances (J/psi, Upsilon) and low-mass gamma*
#   WH3l_chlll      = sum over the 3 leptons of sign(pdgId) = -(total charge): |WH3l_chlll| == 1 rejects +++ / ---
#   WH3l_ZVeto      = min |m(OSSF) - mZ| over the opposite-sign same-flavour (OSSF) pairs, 9999 if no OSSF pair.
#                     "< 25" requires a Z candidate in the window 66 < m(ll) < 116 GeV
#   ZH3l_Z4lveto    = |m(lll) - mZ|, filled only if there is an OSSF pair (else -9999).
#                     "> 20" removes Z -> ll + FSR photon conversion (Z -> 4l / Zgamma) events
#   ZH3l_njet       = number of CleanJets with pT > 30 GeV and |eta| < 4.7
#   ZH3l_dphilmetj  = |dphi(l_W + MET, leading jet)|            (filled if ZH3l_njet >= 1, else -9999)
#   ZH3l_dphilmetjj = |dphi(l_W + MET, leading jet + 2nd jet)|  (filled if ZH3l_njet >= 2, else -9999)
#   where the Z leptons are the OSSF pair closest to mZ and l_W is the remaining lepton

# Preselections - applied to all the cuts
preselections = 'Alt(Lepton_pt,0,0)>25 \
              && Alt(Lepton_pt,1,0)>20 \
              && Alt(Lepton_pt,2,0)>15 \
              && Alt(Lepton_pt,3,0)<10 \
              && abs(WH3l_chlll) == 1 \
              && (WH3l_mOSll[0] < 0 || WH3l_mOSll[0] > 12) \
              && (WH3l_mOSll[1] < 0 || WH3l_mOSll[1] > 12) \
              && (WH3l_mOSll[2] < 0 || WH3l_mOSll[2] > 12) \
              && WH3l_ZVeto < 25 \
              && ZH3l_Z4lveto > 20 \
              && bVeto \
              && ZH3l_njet >= 1 \
'
# Optional: veto jets in the noisy 2.5 < |eta| < 3.0 region, append "&& noJetInHorn" to compare

WZ_1j = 'ZH3l_njet == 1 && ZH3l_dphilmetj > 3.14159/2'
WZ_2j = 'ZH3l_njet >= 2 && ZH3l_dphilmetjj > 3.14159/2'

# WZ CR, inclusive in jets (1j + 2j CRs)
cuts['zh3l_WZ_CR_incl'] = f'({WZ_1j}) || ({WZ_2j})'

# WZ CR in jet bins, without and with a MET cut (as in Run 2)
cuts['zh3l_WZ_CR'] = {
    'expr' : '1',
    'categories' : {
        '1j'     : WZ_1j,
        '2j'     : WZ_2j,
        '1j_met' : WZ_1j + ' && PuppiMET_pt > 25',
        '2j_met' : WZ_2j + ' && PuppiMET_pt > 25',
    }
}

# NEW w.r.t. WZ/2022_v12: signal region, WZ CR with the dphi cut inverted (Run 2: zh3l_SR_1j/2j(_met))
SR_1j = 'ZH3l_njet == 1 && ZH3l_dphilmetj < 3.14159/2'
SR_2j = 'ZH3l_njet >= 2 && ZH3l_dphilmetjj < 3.14159/2'

cuts['zh3l_SR_incl'] = f'({SR_1j}) || ({SR_2j})'

cuts['zh3l_SR'] = {
    'expr' : '1',
    'categories' : {
        '1j'     : SR_1j,
        '2j'     : SR_2j,
        '1j_met' : SR_1j + ' && PuppiMET_pt > 25',
        '2j_met' : SR_2j + ' && PuppiMET_pt > 25',
    }
}
