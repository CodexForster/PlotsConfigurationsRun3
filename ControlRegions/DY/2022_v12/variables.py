# variables
variables = {}

variables['events'] = {
    'name'  : '1',      
    'range' : (1,0,2),  
    'xaxis' : 'events', 
    'fold'  : 3
}

variables['nvtx'] = {     
    'name'  : 'PV_npvsGood',      
    'range' : (100, 0, 100),  
    'xaxis' : 'number of vertices', 
    'fold'  : 3
}

variables['mll'] = {
    'name': 'mll',    
    'range' : (50,0,200), 
    'xaxis' : 'm_{ll} [GeV]',
    'fold' : 0
}

variables['ptll']  = {  
    'name': 'ptll',     
    'range' : (40,0,200),   
    'xaxis' : 'p_{T}^{ll} [GeV]',
    'fold' : 0
}

variables['drll']  = {
    'name': 'drll',
    'range' : (50, 0,5),
    'xaxis' : '#Delta R_{ll}',
    'fold' : 0
}

variables['dphill']  = {
    'name': 'dphill',
    'range' : (50,0,5),
    'xaxis' : '#Delta #phi_{ll}',
    'fold' : 0
}

variables['pt1']  = { 
    'name': 'Lepton_pt[0]',     
    'range' : (40,0,200),
    'xaxis' : 'p_{T} 1st lep',
    'fold'  : 3                         
}

variables['pt2']  = {
    'name': 'Lepton_pt[1]',     
    'range' : (40,0,160),   
    'xaxis' : 'p_{T} 2nd lep',
    'fold'  : 3                         
}

variables['eta1']  = {
    'name': 'Lepton_eta[0]',     
    'range' : (50,-2.5,2.5),   
    'xaxis' : '#eta 1st lep',
    'fold'  : 3                         
}

variables['eta2']  = {
    'name': 'Lepton_eta[1]',     
    'range' : (50,-2.5,2.5),   
    'xaxis' : '#eta 2nd lep',
    'fold'  : 3                         
}

                        
# B Tag
variables['jetdeepb']  = {
    'name': 'Alt(Take(Jet_btagDeepFlavB, CleanJet_jetIdx), 0, -99)',
    'range' : (40,-1,1),
    'xaxis' : 'B tagger 1st jet (DeepB)',
    'fold' : 2
}

variables['jetParT']  = {
    'name': 'Alt(Take(Jet_btagRobustParTAK4B, CleanJet_jetIdx), 0, -99)',
    'range' : (40,-1,1),
    'xaxis' : 'B tagger 1st jet (RobustParT AK4B)',
    'fold' : 2
}

variables['jetPNetB']  = {
    'name': 'Alt(Take(Jet_btagPNetB, CleanJet_jetIdx), 0, -99)',
    'range' : (40,-1,1),
    'xaxis' : 'B tagger 1st jet (ParticleNet B)',
    'fold' : 2
}


# MET
variables['trkMet']  = { 
    'name': 'TkMET_pt',
    'range' : (20,0,200),
    'xaxis' : 'trk met [GeV]',
    'fold' : 3
}

variables['puppimet']  = {
    'name': 'PuppiMET_pt',
    'range' : (20,0,200),
    'xaxis' : 'Puppi MET p_{T} [GeV]',
    'fold' : 3
}

############# New Jet processing
variables['njet']  = {
    'name': 'Sum(CleanJet_pt>30)',
    'range' : (5,0,5),
    'xaxis' : 'Number of jets',
    'fold' : 2
}

variables['jetpt1']  = {
    'name': 'Alt(CleanJet_pt, 0, -99) - 9999.9*(CleanJet_pt[0]<30)',
    'range' : (40,0,200),
    'xaxis' : 'p_{T} 1st jet',
    'fold' : 0
}

variables['jetpt2']  = {
    'name': 'Alt(CleanJet_pt, 1, -99)  - 9999.9*(CleanJet_pt[1]<30)',
    'range' : (40,0,200),
    'xaxis' : 'p_{T} 2nd jet',
    'fold' : 0
}

variables['jeteta1']  = {
    'name': 'Alt(CleanJet_eta, 0, -99) - 9999.9*(CleanJet_pt[0]<30)',
    'range' : (30,-4.7,4.7),
    'xaxis' : '#eta 1st jet',
    'fold' : 0
}

variables['jeteta1_fine_binning']  = {
    'name': 'Alt(CleanJet_eta, 0, -99) - 9999.9*(CleanJet_pt[0]<30)',
    'range' : (94,-4.7,4.7),
    'xaxis' : '#eta 1st jet',
    'fold' : 0
}

variables['jeteta2']  = {
    'name': 'Alt(CleanJet_eta, 1, -99) - 9999.9*(CleanJet_pt[1]<30)',
    'range' : (30,-4.7,4.7),
    'xaxis' : '#eta 2nd jet',
    'fold' : 0
}

variables['jeteta2_fine_binning']  = {
    'name': 'Alt(CleanJet_eta, 1, -99) - 9999.9*(CleanJet_pt[1]<30)',
    'range' : (94,-4.7,4.7),
    'xaxis' : '#eta 2nd jet',
    'fold' : 0
}
