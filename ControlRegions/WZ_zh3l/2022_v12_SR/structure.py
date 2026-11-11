# structure configuration for datacard

structure = {}

# keys here must match keys in samples.py
for skey in samples:
    structure[skey] = {
        # NEW w.r.t. WZ/2022_v12: ZH samples are signal
        'isSignal' : 1 if skey in ['ZH_hww', 'ggZH_hww'] else 0,
        'isData'   : 1 if skey == 'DATA' else 0,
    }
