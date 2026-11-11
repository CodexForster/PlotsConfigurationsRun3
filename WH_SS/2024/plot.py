# Group of plots

groupPlot = {}

groupPlot['top']  = {
    'nameHR' : 'ttbar and tW',
    'isSignal' : 0,
    'color': '#ffa90e',   # 400 kYellow                                                                                                                 
    'samples'  : ['top']
}


groupPlot['Fake']  = {
    'nameHR' : 'nonprompt',
    'isSignal' : 0,
    'color': '#94a4a2',    # 921 kGray + 1                                                                                                              
    'samples'  : ['Fake']
}


groupPlot['WW']  = {
    'nameHR' : 'WW',
    'isSignal' : 0,
    'color': '#3f90da', # 851 kAzure -9                                                                                                                  
    'samples'  : ['WW', 'ggWW']
}

groupPlot['DY']  = {
    'nameHR' : "DY",
    'isSignal' : 0,
    'color'    : '#832db6',    # 418 kGreen+2
    'samples'  : ['DY']
}


groupPlot['Vg']  = {
    'nameHR' : 'V#gamma',
    'isSignal' : 0,
    'color': '#e76300', 
    'samples'  : ['Zg', 'Wg']
}


groupPlot['VgS']  = {
    'nameHR' : 'V#gamma*',
    'isSignal' : 0,
    'color': '#92dadd', 
    'samples'  : ['ZgS', 'WgS', 'WZS']
}


# groupPlot['VZ']  = {
#     'nameHR' : "VZ",
#     'isSignal' : 0,
#     'color'    : '#a96b59',  
#     'samples'  : ['WZ', 'ZZ']
# }

groupPlot['WZ']  = {
    'nameHR' : "WZ",
    'isSignal' : 0,
    'color'    : '#a96b59',  
    'samples'  : ['WZ']
}

groupPlot['ZZ']  = {
    'nameHR' : "ZZ",
    'isSignal' : 0,
    'color'    : '#d2A08C',  
    'samples'  : ['ZZ']
}


groupPlot['VVV']  = {
    'nameHR' : "VVV",
    'isSignal' : 0,
    'color'    : '#717581',  
    'samples'  : ['VVV']
}


# groupPlot['ggF']  = {
#     'nameHR' : "ggF",
#     'isSignal' : 1,
#     'color'    : '#bd1f01',   # 632 kRed
#     'samples'  : ['ggH_hww']
# }

groupPlot['WHSS'] = {
    'nameHR'   : 'WHSS',
    'isSignal' : 1,
    'color'    : '#bd1f01',
    'samples'  : ['WminusH', 'WplusH']
}

# groupPlot['WminusH'] = {
#     'nameHR'   : 'W^{-}H',
#     'isSignal' : 1,
#     'color'    : '#bd1f01',
#     'samples'  : ['WminusH']
# }

# groupPlot['WplusH'] = {
#     'nameHR'   : 'W^{+}H',
#     'isSignal' : 1,
#     'color'    : '#bd1f01',
#     'samples'  : ['WplusH']
# }

# Plots

plot = {}

plot['DY']  = {  
    'nameHR'   : 'DY',
    'color'    : 418,
    'isSignal' : 0,
    'isData'   : 0, 
    'scale'    : 1.,
}


plot['top']  = {
    'nameHR'   : 'top',
    'color'    : 400,
    'isSignal' : 0,
    'isData'   : 0,
    'scale'    : 1.,
}



plot['Fake']  = {
    'nameHR'   : 'nonprompt',
    'color'    : 921,
    'isSignal' : 0,
    'isData'   : 0,
    'scale'    : 1.0,
}


plot['WW']  = {
    'nameHR'   : 'WW',
    'color'    : 851,
    'isSignal' : 0,
    'isData'   : 0,
    'scale'    : 1.0,
}

plot['ggWW']  = {
    'nameHR'   : 'ggWW',
    'color'    : 921,
    'isSignal' : 0,
    'isData'   : 0,
    'scale'    : 1.0,
}


plot['Zg']  = {
    'nameHR'   : 'Zg',
    'color'    : 857,
    'isSignal' : 0,
    'isData'   : 0,
    'scale'    : 1.0,
}

plot['Wg']  = {
    'nameHR'   : 'Wg',
    'color'    : 857,
    'isSignal' : 0,
    'isData'   : 0,
    'scale'    : 0.33,
}


plot['ZgS']  = {
    'nameHR'   : 'ZgS',
    'color'    : 858,
    'isSignal' : 0,
    'isData'   : 0,
    'scale'    : 1.0,
}

plot['WgS']  = {
    'nameHR'   : 'WgS',
    'color'    : 858,
    'isSignal' : 0,
    'isData'   : 0,
    'scale'    : 1.,
}

plot['WZS']  = {
    'nameHR'   : 'WZS',
    'color'    : 858,
    'isSignal' : 0,
    'isData'   : 0,
    'scale'    : 1.0,
}

plot['WZ']  = {
    'nameHR'   : 'WZ',
    'color'    : '#a96b59',
    'isSignal' : 0,
    'isData'   : 0,
    'scale'    : 1.0,
}


plot['ZZ']  = {
    'nameHR'   : 'ZZ',
    'color'    : 617,
    'isSignal' : 0,
    'isData'   : 0,
    'scale'    : 1.0,
}

plot['VVV']  = {
    'nameHR'   : 'VVV',
    'color'    : 617,
    'isSignal' : 0,
    'isData'   : 0,
    'scale'    : 1.0,
}


# # Higgs

# plot['ggH_hww'] = {
#     'nameHR'   : 'ggF',
#     'color'    : 632,
#     'isSignal' : 1,
#     'isData'   : 0,
#     'scale'    : 1.0,
# }


# plot['qqH_hww'] = {
#     'nameHR'   : 'VBF',
#     'color'    : 632,
#     'isSignal' : 1,
#     'isData'   : 0,
#     'scale'    : 1.0,
# }

# plot['DATA']  = { 
#     'nameHR'   : 'Data',
#     'color'    : 1 ,  
#     'isSignal' : 0,
#     'isData'   : 1 ,
#     'isBlind'  : 1
# }

# plot['WminusH'] = {
#     'nameHR'   : 'WminusH',
#     'color'    : 1,
#     'isSignal' : 1,
#     'isData'   : 0,
#     'scale'    : 1.0
# }

# plot['WHSS'] = {
#     'nameHR'   : 'WHSS',
#     'color'    : 1,
#     'isSignal' : 1,
#     'isData'   : 0,
#     'scale'    : 1.0
# }

plot['WminusH'] = {
    'nameHR'   : 'WminusH',
    'color'    : 1,
    'isSignal' : 1,
    'isData'   : 0,
    'scale'    : 1.0
}

plot['WplusH'] = {
    'nameHR'   : 'WplusH',
    'color'    : 1,
    'isSignal' : 1,
    'isData'   : 0,
    'scale'    : 1.0
}

# Legend definition
legend = {}
legend['lumi'] = 'L = 108 fb^{-1}'
legend['sqrt'] = '#sqrt{s} = 13.6 TeV'
