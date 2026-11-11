# Group of plots (as in PlotsConfigurations/Configurations/ZH3l/Full2018_v7/plot.py, without Fake)
# Only the groups and samples actually defined in samples.py are kept (samples.py skips MC samples not found on disk)

groupPlot = {}

groupPlot['DY'] = {
    'nameHR'   : 'DY',
    'isSignal' : 0,
    'color'    : 616, # kMagenta
    'samples'  : ['DY']
}

groupPlot['WW'] = {
    'nameHR'   : 'WW',
    'isSignal' : 0,
    'color'    : 632, # kRed
    'samples'  : ['WW']
}

groupPlot['top'] = {
    'nameHR'   : 'top',
    'isSignal' : 0,
    'color'    : 416, # kGreen
    'samples'  : ['top']
}

groupPlot['Zg'] = {
    'nameHR'   : 'Z#gamma',
    'isSignal' : 0,
    'color'    : 859, # kAzure - 1
    'samples'  : ['Zg']
}

groupPlot['ZgS'] = {
    'nameHR'   : 'Z#gamma*',
    'isSignal' : 0,
    'color'    : 432, # kCyan
    'samples'  : ['ZgS']
}

groupPlot['ttV'] = {
    'nameHR'   : 't#bar{t}V, tZq',
    'isSignal' : 0,
    'color'    : 419, # kGreen + 3
    'samples'  : ['ttV']
}

groupPlot['VVV'] = {
    'nameHR'   : 'VVV',
    'isSignal' : 0,
    'color'    : 806, # kOrange + 6
    'samples'  : ['VVV']
}

groupPlot['ZZ'] = {
    'nameHR'   : 'ZZ',
    'isSignal' : 0,
    'color'    : 617, # kMagenta + 1
    'samples'  : ['ZZ']
}

groupPlot['WZ_EWK'] = {
    'nameHR'   : 'WZjj EWK',
    'isSignal' : 0,
    'color'    : 798, # kOrange - 2
    'samples'  : ['WZ_EWK']
}

groupPlot['WZ'] = {
    'nameHR'   : 'WZ',
    'isSignal' : 0,
    'color'    : 400, # kYellow
    'samples'  : ['WZ']
}

# NEW w.r.t. WZ/2022_v12: ZH signals, plotted separately (qq -> ZH and gg -> ZH), Z -> ll, H -> WW -> lnu qq samples
groupPlot['ZH_hww'] = {
    'nameHR'   : 'qqZH, H#rightarrowWW#rightarrowl#nuqq',
    'isSignal' : 1,
    'color'    : 632+3, # kRed + 3
    'scaleMultiplicativeOverlaid' : 10.0,
    'samples'  : ['ZH_hww']
}

groupPlot['ggZH_hww'] = {
    'nameHR'   : 'ggZH, H#rightarrowWW#rightarrowl#nuqq',
    'isSignal' : 1,
    'color'    : 881, # kViolet + 1
    'scaleMultiplicativeOverlaid' : 10.0,
    'samples'  : ['ggZH_hww']
}

# Plots

plot = {}

plot['DY']  = {'color': 616, 'isSignal': 0, 'isData': 0, 'scale': 1.0}
plot['WW']  = {'color': 632, 'isSignal': 0, 'isData': 0, 'scale': 1.0}
plot['top'] = {'color': 416, 'isSignal': 0, 'isData': 0, 'scale': 1.0}
plot['Zg']  = {'color': 859, 'isSignal': 0, 'isData': 0, 'scale': 1.0}
plot['ZgS'] = {'color': 432, 'isSignal': 0, 'isData': 0, 'scale': 1.0}
plot['ttV'] = {'color': 419, 'isSignal': 0, 'isData': 0, 'scale': 1.0}
plot['VVV'] = {'color': 806, 'isSignal': 0, 'isData': 0, 'scale': 1.0}
plot['ZZ']  = {'color': 617, 'isSignal': 0, 'isData': 0, 'scale': 1.0}
plot['WZ_EWK'] = {'color': 798, 'isSignal': 0, 'isData': 0, 'scale': 1.0}
plot['WZ']  = {'color': 400, 'isSignal': 0, 'isData': 0, 'scale': 1.0}
# NEW w.r.t. WZ/2022_v12: ZH signals
plot['ZH_hww']   = {'nameHR': 'qqZH', 'color': 632+3, 'isSignal': 1, 'isData': 0, 'scale': 1.0}
plot['ggZH_hww'] = {'nameHR': 'ggZH', 'color': 881,   'isSignal': 1, 'isData': 0, 'scale': 1.0}

# Data

plot['DATA']  = {
    'nameHR'   : 'Data',
    'color'    : 1 ,
    'isSignal' : 0,
    'isData'   : 1 ,
    'isBlind'  : 0
}

# Drop what is not defined in samples.py
plot = {k: v for k, v in plot.items() if k in samples}
for group in list(groupPlot.keys()):
    groupPlot[group]['samples'] = [s for s in groupPlot[group]['samples'] if s in samples]
    if len(groupPlot[group]['samples']) == 0:
        del groupPlot[group]

# Legend definition
legend = {}
legend['lumi'] = 'L = 8.2 fb^{-1}'
legend['sqrt'] = '#sqrt{s} = 13.6 TeV'
