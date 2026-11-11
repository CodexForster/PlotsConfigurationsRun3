_mergedCuts = []
for cut in list(cuts.keys()):
    __cutExpr = ''
    if type(cuts[cut]) == dict:
        __cutExpr = cuts[cut]['expr']
        for cat in list(cuts[cut]['categories'].keys()):
            _mergedCuts.append(cut + '_' + cat)
    elif type(cuts[cut]) == str:
        _mergedCuts.append(cut)

cuts2j = _mergedCuts

variables = {}


variables['tree'] = {
    'tree' : {
        'event' : 'event',
####### detajj
        'detajj' : 'detajj',
        'detajj_absolute_up' : 'detajj_jesRegroed_Absoluteup',
        'detajj_absolute_down' : 'detajj_jesRegroed_Absolutedo',
        'detajj_relativebal_up' : 'detajj_jesRegroed_RelativeBalup',
        'detajj_relativebal_down' : 'detajj_jesRegroed_RelativeBaldo',
####### dphill
        'dphill' : 'dphill',
        'dphill_absolute_up' : 'dphill_jesRegroed_Absoluteup',
        'dphill_absolute_down' : 'dphill_jesRegroed_Absolutedo',
        'dphill_relativebal_up' : 'dphill_jesRegroed_RelativeBalup',
        'dphill_relativebal_down' : 'dphill_jesRegroed_RelativeBaldo',
####### drll
        'drll' : 'drll',
        'drll_absolute_up' : 'drll_jesRegroed_Absoluteup',
        'drll_absolute_down' : 'drll_jesRegroed_Absolutedo',
        'drll_relativebal_up' : 'drll_jesRegroed_RelativeBalup',
        'drll_relativebal_down' : 'drll_jesRegroed_RelativeBaldo',
####### mjj
        'mjj' : 'mjj',
        'mjj_absolute_up' : 'mjj_jesRegroed_Absoluteup',
        'mjj_absolute_down' : 'mjj_jesRegroed_Absolutedo',
        'mjj_relativebal_up' : 'mjj_jesRegroed_RelativeBalup',
        'mjj_relativebal_down' : 'mjj_jesRegroed_RelativeBaldo',
####### ht
        'ht' : 'ht',
        'ht_absolute_up' : 'ht_jesRegroed_Absoluteup',
        'ht_absolute_down' : 'ht_jesRegroed_Absolutedo',
        'ht_relativebal_up' : 'ht_jesRegroed_RelativeBalup',
        'ht_relativebal_down' : 'ht_jesRegroed_RelativeBaldo',
####### mth
        'mth' : 'mth',
        'mth_absolute_up' : 'mth_jesRegroed_Absoluteup',
        'mth_absolute_down' : 'mth_jesRegroed_Absolutedo',
        'mth_relativebal_up' : 'mth_jesRegroed_RelativeBalup',
        'mth_relativebal_down' : 'mth_jesRegroed_RelativeBaldo',
####### mll
        'mll' : 'mll',
        'mll_absolute_up' : 'mll_jesRegroed_Absoluteup',
        'mll_absolute_down' : 'mll_jesRegroed_Absolutedo',
        'mll_relativebal_up' : 'mll_jesRegroed_RelativeBalup',
        'mll_relativebal_down' : 'mll_jesRegroed_RelativeBaldo',
####### puppimet
        'puppimet' : 'PuppiMET_pt',
        'puppimet_absolute_up' : 'PuppiMET_pt_jesRegroed_Absoluteup',
        'puppimet_absolute_down' : 'PuppiMET_pt_jesRegroed_Absolutedo',
        'puppimet_relativebal_up' : 'PuppiMET_pt_jesRegroed_RelativeBalup',
        'puppimet_relativebal_down' : 'PuppiMET_pt_jesRegroed_RelativeBaldo',
####### eta1
        'eta1' : 'Lepton_eta[0]',
####### eta2
        'eta2' : 'Lepton_eta[1]',
####### pt1
        'pt1' : 'Lepton_pt[0]',   
####### pt2
        'pt2' : 'Lepton_pt[1]',   
####### jeteta1
        'jeteta1' : 'Alt(CleanJet_eta, 0, -99)',
        'jeteta1_absolute_up' : 'Alt(CleanJet_eta_jesRegroed_Absoluteup, 0, -99)',
        'jeteta1_absolute_down' : 'Alt(CleanJet_eta_jesRegroed_Absolutedo, 0, -99)',
        'jeteta1_relativebal_up' : 'Alt(CleanJet_eta_jesRegroed_RelativeBalup, 0, -99)',
        'jeteta1_relativebal_down' : 'Alt(CleanJet_eta_jesRegroed_RelativeBaldo, 0, -99)',
####### jeteta2
        'jeteta2' : 'Alt(CleanJet_eta, 1, -99)',
        'jeteta2_absolute_up' : 'Alt(CleanJet_eta_jesRegroed_Absoluteup, 1, -99)',
        'jeteta2_absolute_down' : 'Alt(CleanJet_eta_jesRegroed_Absolutedo, 1, -99)',
        'jeteta2_relativebal_up' : 'Alt(CleanJet_eta_jesRegroed_RelativeBalup, 1, -99)',
        'jeteta2_relativebal_down' : 'Alt(CleanJet_eta_jesRegroed_RelativeBaldo, 1, -99)',
####### jetpt1
        'jetpt1' : 'Alt(CleanJet_pt, 0, -99)',
        'jetpt1_absolute_up' : 'Alt(CleanJet_pt_jesRegroed_Absoluteup, 0, -99)',
        'jetpt1_absolute_down' : 'Alt(CleanJet_pt_jesRegroed_Absolutedo, 0, -99)',
        'jetpt1_relativebal_up' : 'Alt(CleanJet_pt_jesRegroed_RelativeBalup, 0, -99)',
        'jetpt1_relativebal_down' : 'Alt(CleanJet_pt_jesRegroed_RelativeBaldo, 0, -99)',
####### jetpt2
        'jetpt2' : 'Alt(CleanJet_pt, 1, -99)',
        'jetpt2_absolute_up' : 'Alt(CleanJet_pt_jesRegroed_Absoluteup, 1, -99)',
        'jetpt2_absolute_down' : 'Alt(CleanJet_pt_jesRegroed_Absolutedo, 1, -99)',
        'jetpt2_relativebal_up' : 'Alt(CleanJet_pt_jesRegroed_RelativeBalup, 1, -99)',
        'jetpt2_relativebal_down' : 'Alt(CleanJet_pt_jesRegroed_RelativeBaldo, 1, -99)',
####### dphillmet
        'dphillmet' : 'dphillmet',
        'dphillmet_absolute_up' : 'dphillmet_jesRegroed_Absoluteup',
        'dphillmet_absolute_down' : 'dphillmet_jesRegroed_Absolutedo',
        'dphillmet_relativebal_up' : 'dphillmet_jesRegroed_RelativeBalup',
        'dphillmet_relativebal_down' : 'dphillmet_jesRegroed_RelativeBaldo',
####### ptll
        'ptll' : 'ptll',
        'ptll_absolute_up' : 'ptll_jesRegroed_Absoluteup',
        'ptll_absolute_down' : 'ptll_jesRegroed_Absolutedo',
        'ptll_relativebal_up' : 'ptll_jesRegroed_RelativeBalup',
        'ptll_relativebal_down' : 'ptll_jesRegroed_RelativeBaldo',
####### Ctot
        'Ctot' : 'log((abs(2*Lepton_eta[0]-CleanJet_eta[0]-CleanJet_eta[1])+abs(2*Lepton_eta[1]-CleanJet_eta[0]-CleanJet_eta[1]))/detajj)',
        'Ctot_absolute_up' : 'log((abs(2*Lepton_eta[0]-CleanJet_eta_jesRegroed_Absoluteup[0]-CleanJet_eta_jesRegroed_Absoluteup[1])+abs(2*Lepton_eta[1]-CleanJet_eta_jesRegroed_Absoluteup[0]-CleanJet_eta_jesRegroed_Absoluteup[1]))/detajj_jesRegroed_Absoluteup)',
        'Ctot_absolute_down' : 'log((abs(2*Lepton_eta[0]-CleanJet_eta_jesRegroed_Absolutedo[0]-CleanJet_eta_jesRegroed_Absolutedo[1])+abs(2*Lepton_eta[1]-CleanJet_eta_jesRegroed_Absolutedo[0]-CleanJet_eta_jesRegroed_Absolutedo[1]))/detajj_jesRegroed_Absolutedo)',
        'Ctot_relativebal_up' : 'log((abs(2*Lepton_eta[0]-CleanJet_eta_jesRegroed_RelativeBalup[0]-CleanJet_eta_jesRegroed_RelativeBalup[1])+abs(2*Lepton_eta[1]-CleanJet_eta_jesRegroed_RelativeBalup[0]-CleanJet_eta_jesRegroed_RelativeBalup[1]))/detajj_jesRegroed_RelativeBalup)',
        'Ctot_relativebal_down' : 'log((abs(2*Lepton_eta[0]-CleanJet_eta_jesRegroed_RelativeBaldo[0]-CleanJet_eta_jesRegroed_RelativeBaldo[1])+abs(2*Lepton_eta[1]-CleanJet_eta_jesRegroed_RelativeBaldo[0]-CleanJet_eta_jesRegroed_RelativeBaldo[1]))/detajj_jesRegroed_RelativeBaldo)',
######## mlj11
        'mlj11' : 'm_lj[0]',
######## mlj12
        'mlj12' : 'm_lj[1]',
######## mlj21
        'mlj21' : 'm_lj[2]',
######## mlj22
        'mlj22' : 'm_lj[3]',
####### mtw2
        'mtw2' : 'mtw2',
        'mtw2_absolute_up' : 'mtw2_jesRegroed_Absoluteup',
        'mtw2_absolute_down' : 'mtw2_jesRegroed_Absolutedo',
        'mtw2_relativebal_up' : 'mtw2_jesRegroed_RelativeBalup',
        'mtw2_relativebal_down' : 'mtw2_jesRegroed_RelativeBaldo',
######### weights
        'PS_ISR_d' : 'PSWeight[2]',
        'PS_ISR_u' : 'PSWeight[0]',
        'PS_FSR_d' : 'PSWeight[3]',
        'PS_FSR_u' : 'PSWeight[1]',
        'btagSF_bc_unc_up' : 'btagSFbc_up_correlated/btagSFbc',
        'btagSF_bc_unc_down' : 'btagSFbc_down_correlated/btagSFbc',
    },
    'cuts' : ['hww_sr'],
    'blind' : dict([(cut, 'full') for cut in cuts2j if 'hww_sr' in cut])
}