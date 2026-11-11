# variables
variables = {}

# 'fold' : 0 = not fold (default), 1 = fold underflow bin, 2 = fold overflow bin, 3 = fold underflow and overflow
# Dijet variables are -9999 in the 1-jet categories: they end up in the (not folded) underflow bin

variables['events'] = {
    'name'  : '1',
    'range' : (1,0,2),
    'xaxis' : 'events',
    'fold'  : 3
}

variables['nvtx'] = {
    'name'  : 'PV_npvsGood',
    'range' : (40,0,80),
    'xaxis' : 'number of vertices',
    'fold'  : 3
}

############# Leptons

variables['pt1'] = {
    'name'  : 'Lepton_pt[0]',
    'range' : (20,0,200),
    'xaxis' : 'p_{T} 1st lep [GeV]',
    'fold'  : 3
}

variables['pt2'] = {
    'name'  : 'Lepton_pt[1]',
    'range' : (20,0,140),
    'xaxis' : 'p_{T} 2nd lep [GeV]',
    'fold'  : 3
}

variables['pt3'] = {
    'name'  : 'Lepton_pt[2]',
    'range' : (20,0,100),
    'xaxis' : 'p_{T} 3rd lep [GeV]',
    'fold'  : 3
}

variables['eta1'] = {
    'name'  : 'Lepton_eta[0]',
    'range' : (25,-2.5,2.5),
    'xaxis' : '#eta 1st lep',
    'fold'  : 3
}

variables['eta2'] = {
    'name'  : 'Lepton_eta[1]',
    'range' : (25,-2.5,2.5),
    'xaxis' : '#eta 2nd lep',
    'fold'  : 3
}

variables['eta3'] = {
    'name'  : 'Lepton_eta[2]',
    'range' : (25,-2.5,2.5),
    'xaxis' : '#eta 3rd lep',
    'fold'  : 3
}

# 0 = Z(ee) W(e), 1 = Z(ee) W(mu), 2 = Z(mumu) W(e), 3 = Z(mumu) W(mu)
variables['channel'] = {
    'name'  : '2*(((abs(Lepton_pdgId[0])==13) + (abs(Lepton_pdgId[1])==13) + (abs(Lepton_pdgId[2])==13) - (abs(ZH3l_pdgid_l)==13)) == 2) + (abs(ZH3l_pdgid_l)==13)',
    'range' : (4,-0.5,3.5),
    'xaxis' : 'channel: Z(ee)e, Z(ee)#mu, Z(#mu#mu)e, Z(#mu#mu)#mu',
    'fold'  : 0
}

variables['WlepId'] = {
    'name'  : 'ZH3l_pdgid_l',
    'range' : (31,-15.5,15.5),
    'xaxis' : 'W lepton pdgId',
    'fold'  : 0
}

############# Z and W candidates

variables['mZ'] = {
    'name'  : 'ZH3l_checkmZ',
    'range' : (25,66,116),
    'xaxis' : 'm_{ll}^{Z} [GeV]',
    'fold'  : 3
}

variables['ptZ'] = {
    'name'  : 'ZH3l_pTZ',
    'range' : (20,0,400),
    'xaxis' : 'p_{T}^{Z} [GeV]',
    'fold'  : 3
}

variables['mlll'] = {
    'name'  : 'WH3l_mlll',
    'range' : (30,100,400),
    'xaxis' : 'm_{lll} [GeV]',
    'fold'  : 3
}

variables['ptlll'] = {
    'name'  : 'WH3l_ptlll',
    'range' : (20,0,300),
    'xaxis' : 'p_{T}^{lll} [GeV]',
    'fold'  : 3
}

variables['puppimet'] = {
    'name'  : 'PuppiMET_pt',
    'range' : (20,0,200),
    'xaxis' : 'PUPPI MET p_{T} [GeV]',
    'fold'  : 3
}

variables['mTlmet'] = {
    'name'  : 'ZH3l_mTlmet',
    'range' : (20,0,200),
    'xaxis' : 'm_{T}(l_{W}, MET) [GeV]',
    'fold'  : 3
}

############# Jets

variables['njet'] = {
    'name'  : 'ZH3l_njet',
    'range' : (6,0,6),
    'xaxis' : 'Number of jets (p_{T} > 30 GeV)',
    'fold'  : 2
}

variables['jetpt1'] = {
    'name'  : 'CleanJet_pt[0]',
    'range' : (20,30,230),
    'xaxis' : 'p_{T} 1st jet [GeV]',
    'fold'  : 2
}

variables['jeteta1'] = {
    'name'  : 'CleanJet_eta[0]',
    'range' : (30,-4.7,4.7),
    'xaxis' : '#eta 1st jet',
    'fold'  : 0
}

variables['jetpt2'] = {
    'name'  : 'Alt(CleanJet_pt, 1, -9999) - 9999.9*(ZH3l_njet < 2)',
    'range' : (20,30,230),
    'xaxis' : 'p_{T} 2nd jet [GeV]',
    'fold'  : 2
}

variables['jeteta2'] = {
    'name'  : 'Alt(CleanJet_eta, 1, -9999) - 9999.9*(ZH3l_njet < 2)',
    'range' : (30,-4.7,4.7),
    'xaxis' : '#eta 2nd jet',
    'fold'  : 0
}

variables['mjj'] = {
    'name'  : 'ZH3l_dmjjmW + 80.4',
    'range' : (25,0,500),
    'xaxis' : 'm_{jj} [GeV]',
    'fold'  : 2
}

############# ZH3l discriminating variables

variables['dphilmetj'] = {
    'name'  : 'ZH3l_dphilmetj',
    'range' : (16,0,3.14159),
    'xaxis' : '#Delta#phi(l_{W}+MET, j)',
    'fold'  : 0
}

variables['dphilmetjj'] = {
    'name'  : 'ZH3l_dphilmetjj',
    'range' : (16,0,3.14159),
    'xaxis' : '#Delta#phi(l_{W}+MET, jj)',
    'fold'  : 0
}

variables['pTlmetj'] = {
    'name'  : 'ZH3l_pTlmetj',
    'range' : (20,0,400),
    'xaxis' : 'p_{T}(l_{W}+MET+j) [GeV]',
    'fold'  : 2
}

variables['pTlmetjj'] = {
    'name'  : 'ZH3l_pTlmetjj',
    'range' : (20,0,400),
    'xaxis' : 'p_{T}(l_{W}+MET+jj) [GeV]',
    'fold'  : 2
}

variables['mTlmetj'] = {
    'name'  : 'ZH3l_mTlmetj',
    'range' : (20,0,400),
    'xaxis' : 'm_{T}(l_{W}+MET+j) [GeV]',
    'fold'  : 2
}

variables['mTlmetjj'] = {
    'name'  : 'ZH3l_mTlmetjj',
    'range' : (16,50,450),
    'xaxis' : 'm_{T}(l_{W}+MET+jj) [GeV]',
    'fold'  : 2
}

# NEW w.r.t. WZ/2022_v12: data blinded in the signal region (all variables, all SR categories).
# Only mkPlot uses this: histo_DATA is still filled in the SR in the mkShapes ROOT file.
# Do not use mkPlot --plotFancy (it looks up variable['blind'][cutName] also for the CR cuts).
SRcuts = ['zh3l_SR_incl', 'zh3l_SR_1j', 'zh3l_SR_2j', 'zh3l_SR_1j_met', 'zh3l_SR_2j_met']
for var in variables:
    variables[var]['blind'] = {cut: 'full' for cut in SRcuts}
