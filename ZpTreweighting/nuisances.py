print(treeBaseDir)
def makeMCDirectory(var=''):
    _treeBaseDir = treeBaseDir + ''
    if useXROOTD:
        _treeBaseDir = redirector + treeBaseDir
    if var== '':
        return '/'.join([_treeBaseDir, mcProduction, mcSteps])
    else:
        return '/'.join([_treeBaseDir, mcProduction, mcSteps + '__' + var])


# merge cuts
_mergedCuts = []
for cut in list(cuts.keys()):
    __cutExpr = ''
    if type(cuts[cut]) == dict:
        __cutExpr = cuts[cut]['expr']
        for cat in list(cuts[cut]['categories'].keys()):
            _mergedCuts.append(cut + '_' + cat)
    elif type(cuts[cut]) == str:
        _mergedCuts.append(cut)


# Dfinitions of groups of samples
mc = [skey for skey in samples if skey not in ('DATA')]

nuisances = {}


################################ EXPERIMENTAL UNCERTAINTIES  #################################

#### Luminosity

# https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun3
nuisances['lumi_2022'] = {
    'name'    : 'lumi_2022',
    'type'    : 'lnN',
    'samples' : dict((skey, '1.014') for skey in mc)
}

### MC statistical uncertainty
autoStats = True
if autoStats:
    ## Use the following if you want to apply the automatic combine MC stat nuisances.
    nuisances['stat'] = {
        'type': 'auto',
        'maxPoiss': '10',
        'includeSignal': '0',
        #  nuisance ['maxPoiss'] =  Number of threshold events for Poisson modelling
        #  nuisance ['includeSignal'] =  Include MC stat nuisances on signal processes (1=True, 0=False)
        'samples': {}
    }

#### Pileup reweighting uncertainty
# The puWeight is computed by comparing the observed (data) pileup profile to the simulated one.
# A ±4.6% variation of the total inelastic pp cross-section (69.2 mb) is used to derive Up/Down
# variations of the pileup distribution, propagating to a ±5% normalization uncertainty.
# Reference: https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun3
nuisances['PU'] = {
    'name'    : 'CMS_pileup_2022',
    'type'    : 'lnN',
    'samples' : dict((skey, '1.05') for skey in mc),
}

##### Trigger Scale Factor uncertainty
# TriggerSFWeight_2l is the data/MC trigger efficiency ratio for the dilepton trigger paths.
# The Up/Down variations, TriggerSFWeight_2l_u and TriggerSFWeight_2l_d, shift the trigger SF
# by its uncertainty. The ratio to the central value isolates the shape effect of the trigger SF.
# Reference: mkShapesRDF/processor/modules/TrigMaker.py
trig_syst = ['TriggerSFWeight_2l_u/TriggerSFWeight_2l', 'TriggerSFWeight_2l_d/TriggerSFWeight_2l']

nuisances['trigg'] = {
    'name'    : 'CMS_eff_hwwtrigger_2022',
    'kind'    : 'weight',
    'type'    : 'shape',
    'samples' : dict((skey, trig_syst) for skey in mc)
}

##### Electron Efficiency uncertainty
# LepSF2l__ele_eleWP__Up/Down encodes the variation of the product of electron ID+isolation SFs
# for both leptons simultaneously. The SF is derived from tag-and-probe measurements in Z->ee.
# Reference: mkShapesRDF/processor/modules/formulasToAdd_MC_Full2022v12.py
nuisances['eff_e'] = {
    'name'    : 'CMS_eff_e_2022',
    'kind'    : 'weight',
    'type'    : 'shape',
    'samples' : dict((skey, ['SFweightEleUp', 'SFweightEleDown']) for skey in mc),
}

##### Muon Efficiency uncertainty
# LepSF2l__mu_muWP__Up/Down encodes the variation of the product of muon ID+isolation SFs.
# The SF is derived from tag-and-probe measurements in Z->mumu.
# Reference: mkShapesRDF/processor/modules/formulasToAdd_MC_Full2022v12.py
nuisances['eff_m'] = {
    'name'    : 'CMS_eff_m_2022',
    'kind'    : 'weight',
    'type'    : 'shape',
    'samples' : dict((skey, ['SFweightMuUp', 'SFweightMuDown']) for skey in mc),
}

##### Parton Shower (ISR and FSR) uncertainties
# PSWeight stores four event weights: [ISR_down, FSR_down, ISR_up, FSR_up].
# These vary the amount of initial-state and final-state radiation, which affects the
# Z pT spectrum and the jet multiplicity, and are especially important for DY and top samples.
# Reference: https://cms-pdmv-prod.web.cern.ch/mcm/
nuisances['PS_ISR'] = {
    'name'    : 'ps_isr',
    'kind'    : 'weight',
    'type'    : 'shape',
    'samples' : dict((skey, ['PSWeight[2]', 'PSWeight[0]']) for skey in mc),
    'AsLnN'   : '0',
}

nuisances['PS_FSR'] = {
    'name'    : 'ps_fsr',
    'kind'    : 'weight',
    'type'    : 'shape',
    'samples' : dict((skey, ['PSWeight[3]', 'PSWeight[1]']) for skey in mc),
    'AsLnN'   : '0',
}

##### QCD Renormalisation/Factorisation scale uncertainties
# LHEScaleWeight stores 8 or 9 weights corresponding to variations of the renormalisation
# and factorisation scales (muR, muF) by factors of 0.5 and 2. The envelope of all variations
# (indices 0 and nLHEScaleWeight-1) is used to represent the QCD scale uncertainty.
# This is particularly important for DY (Z pT shape) and top backgrounds.
nuisances['QCDscale_DY'] = {
    'name'    : 'QCDscale_DY',
    'skipCMS' : 1,
    'kind'    : 'weight',
    'type'    : 'shape',
    'samples' : {'DY' : ['Alt(LHEScaleWeight,0, 1.)', 'Alt(LHEScaleWeight,nLHEScaleWeight-1,1)']}
}

nuisances['QCDscale_top'] = {
    'name'    : 'QCDscale_ttbar',
    'kind'    : 'weight',
    'type'    : 'shape',
    'samples' : {'top' : ['Alt(LHEScaleWeight,0, 1.)', 'Alt(LHEScaleWeight,nLHEScaleWeight-1,1)']}
}
