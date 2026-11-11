from mkShapesRDF.lib.search_files import SearchFiles

searchFiles = SearchFiles()

redirector = ""
useXROOTD = False

# MC:   /eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer22_130x_nAODv12_Full2022v12/MCl2loose2022v12__MCCorr2022v12JetScaling__l2tight
# DATA: /eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Run2022_ReReco_nAODv12_Full2022v12/DATAl2loose2022v12__l2loose

mcProduction = 'Summer22_130x_nAODv12_Full2022v12'
mcSteps      = 'MCl2loose2022v12__MCCorr2022v12JetScaling__l2tight'
dataReco     = 'Run2022_ReReco_nAODv12_Full2022v12'
# NEW w.r.t. WZ/2022_v12: data read from the l2loose skim (DATAl2loose2022v12__l2tight not found on EOS);
# the tight lepton selection is applied offline through LepWPCut in the DATA weight
dataSteps    = 'DATAl2loose2022v12__l2loose'
# fakeSteps    = 'DATAl1loose2022EFGv12__fakeW'

##############################################
###### Tree base directory for the site ######
##############################################
treeBaseDir = '/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano'
limitFiles = -1

def makeMCDirectory(var=""):
    _treeBaseDir = treeBaseDir + ""
    if redirector != "":
        _treeBaseDir = redirector + treeBaseDir
    if var == "":
        return "/".join([_treeBaseDir, mcProduction, mcSteps])
    else:
        return "/".join([_treeBaseDir, mcProduction, mcSteps + "__" + var])


mcDirectory   = makeMCDirectory()
# fakeDirectory = os.path.join(treeBaseDir, dataReco, fakeSteps)
dataDirectory = os.path.join(treeBaseDir, dataReco, dataSteps)

samples = {}


def nanoGetSampleFiles(path, name):
    _files = searchFiles.searchFiles(path, name, redirector=redirector)
    if limitFiles != -1 and len(_files) > limitFiles:
        return [(name, _files[:limitFiles])]
    else:
        return [(name, _files)]


def CombineBaseW(samples, proc, samplelist):
    _filtFiles = list(filter(lambda k: k[0] in samplelist, samples[proc]["name"]))
    _files = list(map(lambda k: k[1], _filtFiles))
    _l = list(map(lambda k: len(k), _files))
    leastFiles = _files[_l.index(min(_l))]
    dfSmall = ROOT.RDataFrame("Runs", leastFiles)
    s = dfSmall.Sum("genEventSumw").GetValue()
    f = ROOT.TFile(leastFiles[0])
    t = f.Get("Events")
    t.GetEntry(1)
    xs = t.baseW * s

    __files = []
    for f in _files:
        __files += f
    df = ROOT.RDataFrame("Runs", __files)
    s = df.Sum("genEventSumw").GetValue()
    newbaseW = str(xs / s)
    weight = newbaseW + "/baseW"

    for iSample in samplelist:
        addSampleWeight(samples, proc, iSample, weight)


def addSampleWeight(samples, sampleName, sampleNameType, weight):
    obj = list(filter(lambda k: k[0] == sampleNameType, samples[sampleName]["name"]))[0]
    samples[sampleName]["name"] = list(
        filter(lambda k: k[0] != sampleNameType, samples[sampleName]["name"])
    )
    if len(obj) > 2:
        samples[sampleName]["name"].append(
            (obj[0], obj[1], obj[2] + "*(" + weight + ")")
        )
    else:
        samples[sampleName]["name"].append((obj[0], obj[1], "(" + weight + ")"))


# NEW w.r.t. WZ/2022_v12: helper functions getMCFiles and addMCSample, to define a sample from
# several MC datasets and skip (with a warning) the datasets not found in mcDirectory
# NEW w.r.t. 2022_v12_wClaude: optional directory argument (default: mcDirectory), used for the
# privately post-processed signal samples
def getMCFiles(names, directory=None):
    # Collect the files of several MC samples, skipping (with a warning) the ones not found in the directory
    directory = directory or mcDirectory
    files = []
    for name in names:
        _files = nanoGetSampleFiles(directory, name)
        if len(_files[0][1]) == 0:
            print(f"WARNING: no files found for {name} in {directory}, skipping it")
            continue
        files += _files
    return files


def addMCSample(name, names, weight, filesPerJob, directory=None):
    files = getMCFiles(names, directory)
    if len(files) == 0:
        print(f"WARNING: sample {name} has no input files, it will not be defined")
        return
    samples[name] = {
        'name': files,
        'weight': weight,
        'FilesPerJob': filesPerJob,
    }


################################################
############ DATA DECLARATION ##################
################################################

DataRun = [
    ['B','Run2022B-ReReco-v1'],
    ['C','Run2022C-ReReco-v1'],
    ['D','Run2022D-ReReco-v1'],
]

DataSets = ['MuonEG','SingleMuon','Muon','EGamma']

DataTrig = {
    'MuonEG'         : ' Trigger_ElMu' ,
    'SingleMuon'     : '!Trigger_ElMu && Trigger_sngMu' ,
    'Muon'           : '!Trigger_ElMu && (Trigger_sngMu || Trigger_dblMu)',
    'EGamma'         : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_dblMu && (Trigger_sngEl || Trigger_dblEl)'
}


#########################################
############ MC COMMON ##################
#########################################

# SFweight does not include btag weights
# SFweight includes the b veto scale factor (aliases.py)
mcCommonWeightNoMatch = 'XSWeight*METFilter_Common*SFweight'
mcCommonWeight        = 'XSWeight*METFilter_Common*PromptGenLepMatch3l*SFweight'

###########################################
#############  BACKGROUNDS  ###############
###########################################
# Process list as in the Run 2 ZH3l analysis (PlotsConfigurations/Configurations/ZH3l/Full2018_v7/samples.py),
# with the 2022 sample names as found in mcDirectory.
# No data-driven non-prompt estimate (Fake) for the moment.

# DY
# NEW w.r.t. WZ/2022_v12: added DYto2L-2Jets_MLL-10to50
addMCSample('DY',
            ['DYto2L-2Jets_MLL-50',
             'DYto2L-2Jets_MLL-10to50'],
            mcCommonWeight,
            2)

# Top
# NEW w.r.t. WZ/2022_v12: sample renamed 'Top' -> 'top' (as in Run 2 ZH3l) and single top (s-, t-channel, tW) added
addMCSample('top',
            ['TTTo2L2Nu',
             'ST_s-channel_plus',
             'ST_s-channel_minus',
             'ST_t-channel_top',
             'ST_t-channel_antitop',
             'ST_tW_top',
             'ST_tW_antitop'],
            mcCommonWeight,
            2)

# ttV and tZq
# NEW w.r.t. WZ/2022_v12: ttV sample (Run 2 ZH3l: TTWJetsToLNu + TTZjets), with tZq added
#   TTLL_MLL-* : ttZ/gamma* -> ll,  TTLNu : ttW,  TZQB-ZTo2L : tZq
#   (TTZ-ZtoQQ not used: Z -> qq does not give three leptons)
addMCSample('ttV',
            ['TTLL_MLL-50',
             'TTLL_MLL-4to50',
             'TTLNu',
             'TZQB-ZTo2L'],
            mcCommonWeight,
            2)

# WW
addMCSample('WW',
            ['WWTo2L2Nu'],
            mcCommonWeight,
            2)

# Zg (Gen_ZGstar_mass <= 0: real photon, no prompt matching) and ZgS (virtual photon)
# NEW w.r.t. WZ/2022_v12: Zg and ZgS samples (as in Run 2 ZH3l, where ZGToLLG was used),
# from the DYGto2LG samples binned in m(ll) and photon pT (the bins do not overlap)
ZgSamples = ['DYGto2LG-1Jets_MLL-4to50_PTG-10to100_ext1',
             'DYGto2LG-1Jets_MLL-4to50_PTG-100to200',
             'DYGto2LG-1Jets_MLL-4to50_PTG-200',
             'DYGto2LG-1Jets_MLL-50_PTG-10to100',
             'DYGto2LG-1Jets_MLL-50_PTG-100to200',
             'DYGto2LG-1Jets_MLL-50_PTG-200to400',
             'DYGto2LG-1Jets_MLL-50_PTG-400to600',
             'DYGto2LG-1Jets_MLL-50_PTG-600']

addMCSample('Zg',
            ZgSamples,
            mcCommonWeightNoMatch + '*(Gen_ZGstar_mass <= 0)',
            2)

addMCSample('ZgS',
            ZgSamples,
            mcCommonWeight + '*(Gen_ZGstar_mass > 0)',
            2)

# WZ (low-mass gamma* part removed, as in Run 2)
# NEW w.r.t. WZ/2022_v12: '*gstarHigh' added to the weight (alias defined in aliases.py), to avoid overlap with ZgS
addMCSample('WZ',
            ['WZTo3LNu'],
            mcCommonWeight + '*gstarHigh',
            2)

# WZ + 2 jets, electroweak production
# NEW w.r.t. WZ/2022_v12 (not in Run 2 ZH3l): can contribute in the 2-jet CR
#   WZJJ_QCD not used: overlaps with WZTo3LNu;  WZJJ_Interference not used
addMCSample('WZ_EWK',
            ['WZJJ_EWK'],
            mcCommonWeight,
            2)

# ZZ (qq -> ZZ inclusive + gg -> ZZ)
# NEW w.r.t. WZ/2022_v12: ZZ sample (as in Run 2 ZH3l, which used ZZTo4L + ZZTo2L2Nu + ZZTo2L2Q + ggZZ)
#   ZZJJTo4L_QCD not used: overlaps with the inclusive ZZ sample
addMCSample('ZZ',
            ['ZZ',
             'GluGluToZZTo2e2mu',
             'GluGluToZZTo2e2tau',
             'GluGluToZZTo2mu2tau',
             'GluGluToZZTo4e',
             'GluGluToZZTo4mu',
             'GluGluToZZTo4tau'],
            mcCommonWeight,
            2)

# VVV
# NEW w.r.t. WZ/2022_v12: VVV sample (as in Run 2 ZH3l)
addMCSample('VVV',
            ['ZZZ',
             'WZZ',
             'WWZ',
             'WWW'],
            mcCommonWeight,
            2)

###########################################
#############   SIGNALS  ##################
###########################################
# NEW w.r.t. WZ/2022_v12: ZH(->WW) signal, plotted separately (qq -> ZH and gg -> ZH), from a private
# post-processing of the 2022 signal samples (same steps as mcDirectory)
#   Zto2L_Hto2WtoLNu2Q : Z -> ll, H -> WW -> lnu qq, the ZH3l topology (3l + 2q + MET)
#   Not used:
#   - Zto2L_Hto2Wto2L2Nu (4l): enters the 3l SR when one lepton is lost; left out for now
#   - Z -> qq samples and Zto2L_Hto2Wto4Q: they reach 3l only with non-prompt leptons,
#     which are removed by PromptGenLepMatch3l in mcCommonWeight
#   The central ZH_Hto2Wto2L2Nu_M125 / GluGluZH_Hto2Wto2L2Nu_M125 (Z inclusive) are not used either:
#   they overlap with the private Zto2L_Hto2Wto2L2Nu samples
signalDirectory = '/eos/user/d/dshekar/private_postprocess_zh3l_signal_samples/Summer22_130x_nAODv12_Full2022v12/MCl2loose2022v12__MCCorr2022v12JetScaling__l2tight'

addMCSample('ZH_hww',
            ['ZH_Zto2L_Hto2WtoLNu2Q_M125'],
            mcCommonWeight,
            2,
            directory=signalDirectory)

addMCSample('ggZH_hww',
            ['GluGluZH_Zto2L_Hto2WtoLNu2Q_M125'],
            mcCommonWeight,
            2,
            directory=signalDirectory)

###########################################
################## DATA ###################
###########################################

samples['DATA'] = {
    'name': [],
    'weight': 'LepWPCut*METFilter_DATA',
    'weights': [],
    'isData': ['all'],
    'FilesPerJob': 15
}

for _, sd in DataRun:
  for pd in DataSets:
    datatag = pd + '_' + sd

    if (pd == "SingleMuon" and _ in ["D"]) or (pd == "Muon" and _ == "B"):
        continue
    files = nanoGetSampleFiles(dataDirectory, datatag)

    print(datatag)

    # NEW w.r.t. WZ/2022_v12: skip (with a warning) datasets not found in dataDirectory,
    # otherwise mkShapesRDF stops with "the sample proc you specified has no files".
    # If a whole run is missing, lumi in configuration.py has to be changed accordingly.
    if len(files[0][1]) == 0:
        print(f"WARNING: no files found for {datatag} in {dataDirectory}, skipping it")
        continue

    samples['DATA']['name'].extend(files)
    addSampleWeight(samples, 'DATA', datatag, DataTrig[pd])
