cuts = {}

# Preselections - applied to all the cuts
preselections = 'Alt(Lepton_pt,0,0)>25 \
              && Alt(Lepton_pt,1,0)>20 \
              && Alt(Lepton_pt,2,0)>15 \
              && (nLepton>=3 && Alt(Lepton_pt,3,0)<10) \
              && (WH3l_mOSll[0] < 0 || WH3l_mOSll[0] > 12) \
              && (WH3l_mOSll[1] < 0 || WH3l_mOSll[1] > 12) \
              && (WH3l_mOSll[2] < 0 || WH3l_mOSll[2] > 12) \
              && abs(WH3l_chlll) == 1 \
              && bVeto \
'
            # Z mass window selection: same for WH3l and ZH3l = WH3l_ZVeto < 25
            # Zgamma veto = ZH3l_Z4lveto > 20
            #   && Alt(Lepton_pt,1,0)>10 \
            #   && (abs(Lepton_pdgId[1])==13 || Lepton_pt[1]>13) \
            #   && Alt(Lepton_pt,2,0)>10 \
            #   && noJetInHorn \

# Inclusive 
# cuts['wh3l_wz_13TeV_incl'] = 'WH3l_flagOSSF == 1 && PuppiMET_pt > 45 && WH3l_ZVeto < 20 && WH3l_mlll > 100'
#cuts['zh3l_wz_13P6TeV_incl'] = '(ZH3l_CleanJet_4DV.size()==1 && ZH3l_dphilmetj>3.14159/2) || (ZH3l_CleanJet_4DV.size()>=2 && ZH3l_dphilmetjj>3.14159/2)'
cuts['zh3l_wz_13P6TeV_incl'] = 'WH3l_ZVeto<25 && ZH3l_Z4lveto>20 && ((ZH3l_njet==1 && ZH3l_dphilmetj>3.14159/2) || (ZH3l_njet>=2 && ZH3l_dphilmetjj>3.14159/2))'

# Jet bins
cuts['zh3l_wz_13P6TeV'] = {
    'expr' : 'WH3l_ZVeto<25 && ZH3l_Z4lveto>20',
    'categories' : {
        # '0j' : 'ZH3l_njet==0',
        '1j' : '(ZH3l_njet==1) && (ZH3l_dphilmetj>3.14159/2)', # 1-jet, WZ CR
        '2j' : '(ZH3l_njet>=2) && (ZH3l_dphilmetjj>3.14159/2)' # multi-jet, WZ CR
    }
}

