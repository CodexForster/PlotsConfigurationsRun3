cuts = {}

# Preselections - applied to all the cuts
# preselections = 'nLepton > 1 \
# && Lepton_pt[0]>15 \
# && Lepton_pt[1]>15 \
# && abs(Lepton_eta[0])<2.5 \
# && abs(Lepton_eta[1])<2.5 \
# && noJetInHorn \
# && bVeto'

# cuts['os_2l_ee_cf_incl'] = '(nLepton == 2 && Lepton_pdgId[0]*Lepton_pdgId[1]==-11*11 && abs(mll-91.2) < 15)'

# cuts['ss_2l_ee_cf_incl'] = '(nLepton == 2 && Lepton_pdgId[0]*Lepton_pdgId[1]==11*11 && abs(mll-91.2) < 15)'

# cuts['os_2l_ee_cf'] = {
#     'expr' : '(nLepton == 2 && Lepton_pdgId[0]*Lepton_pdgId[1]==-11*11 && abs(mll-91.2) < 15)',
#     'categories' : {
#         '0j' : 'zeroJet',
#         '1j' : 'oneJet && Alt(CleanJet_pt,1,0)<30',
#         '2j' : 'multiJet',
#     }
# }

# cuts['ss_2l_ee_cf'] = {
#     'expr' : '(nLepton == 2 && Lepton_pdgId[0]*Lepton_pdgId[1]==11*11 && abs(mll-91.2) < 15)',
#     'categories' : {
#         '0j' : 'zeroJet',
#         '1j' : 'oneJet && Alt(CleanJet_pt,1,0)<30',
#         '2j' : 'multiJet',
#     }
# }


preselections = 'nLepton > 1 \
&& Lepton_pt[0]>25 \
&& Lepton_pt[1]>20 \
&& bVeto \
&& noJetInHorn \
&& PuppiMET_pt > 30 \
&& mll > 12 \
&& Alt(Lepton_pt,2,0)<10 '


#emu SR
cuts['ss_2l_em_sr'] = '(Lepton_pdgId[0]*Lepton_pdgId[1]==11*13) && abs(Lepton_eta[0] - Lepton_eta[1])<2.0'

cuts['ss_2l_mm_sr'] = '(Lepton_pdgId[0]*Lepton_pdgId[1]==13*13) && abs(Lepton_eta[0] - Lepton_eta[1])<2.0 && abs(mll-91.2)>15'

cuts['ss_2l_ee_sr'] = '(Lepton_pdgId[0]*Lepton_pdgId[1]==11*11) && abs(Lepton_eta[0] - Lepton_eta[1])<2.0 && abs(mll-91.2)>15'

cuts['ss_2l_mm_sr_wOmllCut'] = '(Lepton_pdgId[0]*Lepton_pdgId[1]==13*13) && abs(Lepton_eta[0] - Lepton_eta[1])<2.0'

cuts['ss_2l_mm_sr_wOmllCut'] = '(Lepton_pdgId[0]*Lepton_pdgId[1]==11*11) && abs(Lepton_eta[0] - Lepton_eta[1])<2.0'

cuts['ss_2l_em'] = {
    'expr' : '(Lepton_pdgId[0]*Lepton_pdgId[1] == 11*13) && abs(Lepton_eta[0] - Lepton_eta[1])<2.0',
    'categories' : {
        '0j' : 'zeroJet',
        '1j' : 'oneJet && Alt(CleanJet_pt,1,0)<30.',
        '2j' : 'multiJet && mjj<100 && Alt(CleanJet_pt, 0, 0) > 30.',
    }
}

cuts['ss_2l_mm'] = {
    'expr' : '(Lepton_pdgId[0]*Lepton_pdgId[1] == 13*13) && abs(Lepton_eta[0] - Lepton_eta[1])<2.0 && abs(mll-91.2)>15',
    'categories' : {
        '0j' : 'zeroJet',
        '1j' : 'oneJet && Alt(CleanJet_pt,1,0)<30',
        '2j' : 'multiJet && mjj<100 && Alt(CleanJet_pt, 0, 0) > 30.',
    }
}

cuts['ss_2l_ee'] = {
    'expr' : '(Lepton_pdgId[0]*Lepton_pdgId[1] == 11*11) && abs(Lepton_eta[0] - Lepton_eta[1])<2.0 && abs(mll-91.2)>15',
    'categories' : {
        '0j' : 'zeroJet',
        '1j' : 'oneJet && Alt(CleanJet_pt,1,0)<30',
        '2j' : 'multiJet && mjj<100 && Alt(CleanJet_pt, 0, 0) > 30.',
    }
}

cuts['ss_2l_mm_wOmllCut'] = {
    'expr' : '(Lepton_pdgId[0]*Lepton_pdgId[1]==13*13) && abs(Lepton_eta[0] - Lepton_eta[1])<2.0',
    'categories' : {
        '0j' : 'zeroJet',
        '1j' : 'oneJet && Alt(CleanJet_pt,1,0)<30',
        '2j' : 'multiJet && mjj<100 && Alt(CleanJet_pt, 0, 0) > 30.',
    }
}

cuts['ss_2l_ee_wOmllCut'] = {
    'expr' : '(Lepton_pdgId[0]*Lepton_pdgId[1]==11*11) && abs(Lepton_eta[0] - Lepton_eta[1])<2.0',
    'categories' : {
        '0j' : 'zeroJet',
        '1j' : 'oneJet && Alt(CleanJet_pt,1,0)<30',
        '2j' : 'multiJet && mjj<100 && Alt(CleanJet_pt, 0, 0) > 30.',
    }
}

# cuts['ss_2l_ee_incl'] = '(Lepton_pdgId[0]*Lepton_pdgId[1]==11*11)'

# cuts['os_2l_ee_incl'] = '(Lepton_pdgId[0]*Lepton_pdgId[1]==-11*11)'

# cuts['ss_2l_ee'] = {
#     'expr' : '(Lepton_pdgId[0]*Lepton_pdgId[1] == 11*11)',
#     'categories' : {
#         '0j' : 'zeroJet',
#         '1j' : 'oneJet && Alt(CleanJet_pt,1,0)<30',
#         '2j' : 'multiJet',
#     }
# }

# cuts['os_2l_ee'] = {
#     'expr' : '(Lepton_pdgId[0]*Lepton_pdgId[1] == -11*11)',
#     'categories' : {
#         '0j' : 'zeroJet',
#         '1j' : 'oneJet && Alt(CleanJet_pt,1,0)<30',
#         '2j' : 'multiJet',
#     }
# }

# cuts['os_2l_ee'] = {
#     'expr' : 'nLepton == 2 && (Lepton_pdgId[0]*Lepton_pdgId[1] == -11*11) && abs(mll-91.2) < 15',
#     'categories' : {
#         '0j' : 'zeroJet',
#         '1j' : 'oneJet && Alt(CleanJet_pt,1,0)<30',
#         '2j' : 'multiJet && mjj<100',
#     }
# }

# cuts['val_2l_ee'] = {
#     'expr' : 'nLepton == 2 && (Lepton_pdgId[0]*Lepton_pdgId[1] == 11*11) && Lepton_pt[0]>25 && Lepton_pt[1]>20',
#     'categories' : {
#         '0j' : 'zeroJet',
#         '1j' : 'oneJet && Alt(CleanJet_pt,1,0)<30',
#         '2j' : 'multiJet && mjj<100',
#     }
# }
