# Minimal set of nuisances for control region plots

# Definitions of groups of samples
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
