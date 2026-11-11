#!/usr/bin/env python3
"""
Kinematic selection study for ZH(->WW) -> 3l (Z->ll, W->lnu, W->jj), 2022 v12.

For every cut of the ZH3l selection it produces:
  - a cutflow table (yields per process, cumulative and per-step background rejection)
  - an N-1 plot: distribution of the cut variable with all the *other* cuts applied, nominal threshold marked
  - a scan: background retention (BR) as a function of the cut threshold, with all the other cuts at their
    nominal values
If signal samples are defined in SIGNAL, signal efficiency (SE), S/B, S/sqrt(B) and Asimov significance are added
to the cutflow and to the scans, and the signal is overlaid in the N-1 plots.

BR and SE in the scans are relative to the nominal selection (all cuts nominal, scanned cut included):
BR(y) = B(y) / B(nominal), SE(y) = S(y) / S(nominal), where B(y) is the yield with all the other cuts nominal
and the scanned cut at threshold y. BR = SE = 1 at the nominal threshold, > 1 for looser thresholds.
In the scan plots BR is on the left y axis and SE on the secondary (right) y axis.
(The cutflow table still uses the rejection 1 - B_after / B_before, see cutflow().)
Background = sum of all the MC samples of the configuration.

Samples, weights and aliases are taken from the mkShapesRDF configuration in the parent folder
(samples.py, aliases.py, configuration.py), so the weights are the same as in the plots.
The signal samples are defined below (SIGNAL). They use the same names as the signal samples of samples.py
(ZH_hww, ggZH_hww), which replaces them: otherwise they would be counted as background.

How it works: each sample is read once, a loose base selection is applied, and the per-event weight and all
the cut variables are stored (optionally cached to a .npz file). Everything else is computed from these arrays.

Usage (on lxplus, after sourcing mkShapesRDF/start.sh):
    python3 cut_scan.py --max-files 3              # quick test on a few files per sample
    python3 cut_scan.py --cache arrays.npz         # full run, regions 1j, 2j and incl, arrays saved
    python3 cut_scan.py --from-cache arrays.npz    # only redo tables and plots
    python3 cut_scan.py --region incl --from-cache arrays.npz   # one region only
"""

import os
import re
import sys
import csv
import argparse
from collections import OrderedDict

import numpy as np


###############################################################################
# Signal samples (optional)
###############################################################################
# Without signal, only the background retention (BR) is shown.
# If signal samples are added, signal efficiency (SE), S/B, S/sqrt(B) and Asimov significance
# are also shown.
# NEW w.r.t. 2022_v12_wClaude: Z -> ll, H -> WW -> lnu qq signal, the same samples as ../samples.py (same keys, so
# they are taken as signal and not as background). They are privately post-processed and read from
# signalDirectory (defined in ../samples.py), not from mcDirectory.
SIGNAL = OrderedDict([('ZH_hww', ['ZH_Zto2L_Hto2WtoLNu2Q_M125']), ('ggZH_hww', ['GluGluZH_Zto2L_Hto2WtoLNu2Q_M125'])])


###############################################################################
# Cuts
###############################################################################
# Each cut: name, per-event scalar expression, operator ('>' : keep if var > thr, '<' : keep if var < thr),
# nominal threshold (None = cut not applied in the nominal selection), scan values, histogram range, axis label.
# The order is the order of the cutflow.

PI = 3.14159

REGIONS = ['1j', '2j', 'incl']

def get_cuts(region):
    # Jet regions: 1j = exactly 1 jet, 2j = at least 2 jets, incl = at least 1 jet (1j + 2j).
    # dphi(l_W + MET, j) is used for 1-jet events and dphi(l_W + MET, jj) for events with >= 2 jets
    # (as in zh3l_WZ_CR_incl in ../cuts.py). With this definition the stored variables are the same for all the
    # regions: the trees are read once and only the njet requirement (and the mjj cut, 2j only) changes.
    dphi_var = 'ZH3l_njet == 1 ? ZH3l_dphilmetj : ZH3l_dphilmetjj'
    dphi_lab = {'1j': '#Delta#phi(l_{W}+MET, j)',
                '2j': '#Delta#phi(l_{W}+MET, jj)',
                'incl': '#Delta#phi(l_{W}+MET, j) (1j) or #Delta#phi(l_{W}+MET, jj) (2j)'}[region]
    njet_expr = {'1j': 'ZH3l_njet == 1', '2j': 'ZH3l_njet >= 2', 'incl': 'ZH3l_njet >= 1'}[region]

    cuts = [
        dict(name='pt1', expr='Alt(Lepton_pt,0,0)', op='>', nominal=25.,
             scan=np.arange(10., 45.1, 2.5), hrange=(0., 150., 30), label='p_{T}(l_{1}) [GeV]'),
        dict(name='pt2', expr='Alt(Lepton_pt,1,0)', op='>', nominal=20.,
             scan=np.arange(10., 40.1, 2.5), hrange=(0., 120., 24), label='p_{T}(l_{2}) [GeV]'),
        dict(name='pt3', expr='Alt(Lepton_pt,2,0)', op='>', nominal=15.,
             scan=np.arange(10., 30.1, 1.), hrange=(0., 100., 25), label='p_{T}(l_{3}) [GeV]'),
        dict(name='lep4veto', expr='Alt(Lepton_pt,3,0)', op='<', nominal=10.,
             scan=np.arange(5., 30.1, 2.5), hrange=(0., 50., 25), label='p_{T}(l_{4}) [GeV] (0 if no 4th lepton)'),
        dict(name='mOSll_min', expr='WH3l_mOSll[WH3l_mOSll > 0].size() > 0 ? Min(WH3l_mOSll[WH3l_mOSll > 0]) : 999.',
             op='>', nominal=12., scan=np.arange(0., 40.1, 2.), hrange=(0., 150., 30), label='min m(OS ll) [GeV]'),
        dict(name='Zwindow', expr='WH3l_ZVeto', op='<', nominal=25.,
             scan=np.arange(5., 50.1, 2.5), hrange=(0., 50., 25), label='min |m(OSSF) - m_{Z}| [GeV]'),
        dict(name='Z4lveto', expr='ZH3l_Z4lveto', op='>', nominal=20.,
             scan=np.arange(0., 50.1, 2.5), hrange=(0., 200., 40), label='|m(lll) - m_{Z}| [GeV]'),
        # b veto: highest DeepFlavB score among CleanJets with pT > 20 GeV, |eta| < 2.5 (-1 if none).
        # The veto keeps events with max score < WP. Fixed at the loose WP (0.0583, same as bVeto in aliases.py),
        # not scanned. To scan the WPs instead, replace op/fixed with:
        #   op='<', nominal=0.0583, scan=np.array([0.0583, 0.3086, 0.7183, 0.8111, 0.9512, 1.01]),
        #   scan_labels=['L', 'M', 'T', 'XT', 'XXT', 'none'],
        dict(name='bveto', expr='Sum(CleanJet_pt > 20. && abs(CleanJet_eta) < 2.5) > 0 ? '
                                'Max(Take(Jet_btagDeepFlavB, CleanJet_jetIdx)[CleanJet_pt > 20. && abs(CleanJet_eta) < 2.5]) : -1.',
             op='fixed', fixed='bveto < 0.0583',
             hrange=(-0.05, 1.05, 22), label='max DeepFlavB score (jets p_{T} > 20 GeV)'),
        # region: jet multiplicity (not scanned)
        dict(name='njet', expr='ZH3l_njet', op='fixed', fixed=njet_expr,
             hrange=(0., 6., 6), label='N_{jet} (p_{T} > 30 GeV)'),
        dict(name='dphi', expr=dphi_var, op='<', nominal=PI / 2,
             scan=np.round(np.arange(0.4, PI + 0.01, 0.2), 2), hrange=(0., PI, 16), label=dphi_lab),
        dict(name='met', expr='PuppiMET_pt', op='>', nominal=None,
             scan=np.arange(0., 100.1, 5.), hrange=(0., 200., 40), label='PUPPI MET [GeV]'),
    ]
    if region == '2j':
        cuts.append(
            dict(name='mjj_window', expr='abs(ZH3l_dmjjmW)', op='<', nominal=None,
                 scan=np.arange(10., 150.1, 10.), hrange=(0., 300., 30), label='|m_{jj} - m_{W}| [GeV]'))
    return cuts


# Fixed requirements, not scanned, applied everywhere
FIXED = 'abs(WH3l_chlll) == 1'

# Loose base selection applied when reading the trees: must be looser than every scan point
BASE = 'Alt(Lepton_pt,2,0) > 10. && abs(WH3l_chlll) == 1 && WH3l_ZVeto < 50.'


###############################################################################
# Configuration loading (same files as mkShapesRDF)
###############################################################################

def load_config(config_dir):
    import ROOT
    g = {'__name__': 'cut_scan_cfg'}
    exec('import os, glob, ROOT\nfrom collections import OrderedDict', g, g)
    cwd = os.getcwd()
    os.chdir(config_dir)
    try:
        try:
            exec(compile(open('samples.py').read(), os.path.abspath('samples.py'), 'exec'), g, g)
        except RuntimeError as e:
            # samples.py stops if no DATA file is found: not needed here (MC only)
            print(f'NOTE: {e} -- continuing, DATA is not used here')
        exec(compile(open('aliases.py').read(), os.path.abspath('aliases.py'), 'exec'), g, g)
        conf = open('configuration.py').read()
    finally:
        os.chdir(cwd)
    lumi = float(re.search(r'^lumi\s*=\s*([0-9.eE+-]+)', conf, re.M).group(1))
    return g, lumi


def build_sample_list(g, max_files):
    """Return OrderedDict proc -> list of (files, weight_expr), and the set of signal procs."""
    samples = g['samples']
    procs = OrderedDict()
    for proc, s in samples.items():
        if proc in ('DATA', 'Fake') or s.get('isData'):
            continue
        procs[proc] = []
        for entry in s['name']:
            files = entry[1][:max_files] if max_files > 0 else entry[1]
            w = s['weight'] + (f'*({entry[2]})' if len(entry) > 2 else '')
            if files:
                procs[proc].append((files, w))

    signal = set()
    for proc, names in SIGNAL.items():
        procs[proc] = []
        for name in names:
            # NEW w.r.t. 2022_v12_wClaude: signal files from signalDirectory (../samples.py) if defined
            entry = g['nanoGetSampleFiles'](g.get('signalDirectory', g['mcDirectory']), name)[0]
            files = entry[1][:max_files] if max_files > 0 else entry[1]
            if not files:
                print(f'WARNING: no files for signal sample {name}, skipping it')
                continue
            procs[proc].append((files, g['mcCommonWeight']))
        if procs[proc]:
            signal.add(proc)
        else:
            del procs[proc]

    # merge the datasets of a process that have the same weight: one event loop instead of one per dataset
    for proc, parts in procs.items():
        merged = OrderedDict()
        for files, w in parts:
            merged.setdefault(w, []).extend(files)
        procs[proc] = [(files, w) for w, files in merged.items()]
    return procs, signal


def alias_applies(alias, proc, bkg_procs, signal):
    if 'samples' not in alias:
        return True
    if proc in alias['samples']:
        return True
    # signal samples get the aliases defined for all the MC backgrounds (SFweight, LepWPSF, ...)
    return proc in signal and set(bkg_procs).issubset(set(alias['samples']))


###############################################################################
# Reading the trees
###############################################################################

def load_mkshapes_headers():
    # Helper functions used in the aliases and cuts (Alt, LogVec, ...) are declared in mkShapesRDF/include/headers.hh,
    # which mkShapesRDF loads before defining the aliases: load it here too
    import ROOT
    import mkShapesRDF
    headers = os.path.join(os.path.dirname(os.path.abspath(mkShapesRDF.__file__)), 'include', 'headers.hh')
    if not os.path.isfile(headers) and os.environ.get('STARTPATH'):
        # STARTPATH = .../mkShapesRDF/start.sh, set by start.sh
        headers = os.path.join(os.path.dirname(os.environ['STARTPATH']), 'mkShapesRDF', 'include', 'headers.hh')
    if not os.path.isfile(headers):
        sys.exit(f'ERROR: {headers} not found: source mkShapesRDF/start.sh first')
    if not ROOT.gInterpreter.Declare(f'#include "{headers}"'):
        sys.exit(f'ERROR: could not load {headers}')
    print(f'Loaded {headers}')


def read_arrays(g, lumi, procs, signal, cuts, nthreads):
    import ROOT
    ROOT.gROOT.SetBatch(True)
    if nthreads != 1:
        ROOT.EnableImplicitMT(nthreads)
    load_mkshapes_headers()
    aliases = g['aliases']
    bkg_procs = [p for p in procs if p not in signal]

    import time
    columns = ['w'] + [f'cv_{c["name"]}' for c in cuts]
    out = OrderedDict()
    t_start = time.time()
    for proc, parts in procs.items():
        arrays = {col: [] for col in columns}
        t_proc = time.time()
        for files, wexpr in parts:
            print(f'Reading {proc}: {len(files)} files, weight = {wexpr}', flush=True)
            df = ROOT.RDataFrame('Events', files)
            cols = set(str(c) for c in df.GetColumnNames())
            for name, alias in aliases.items():
                if not alias_applies(alias, proc, bkg_procs, signal):
                    continue
                if name in cols or 'expr' not in alias:
                    continue
                for line in alias.get('linesToAdd', []):
                    ROOT.gInterpreter.Declare(line)
                df = df.Define(name, alias['expr'])
                cols.add(name)
            df = df.Filter(BASE)
            df = df.Define('w', f'{lumi} * ({wexpr})')
            for c in cuts:
                df = df.Define(f'cv_{c["name"]}', f'(double)({c["expr"]})')
            res = df.AsNumpy(columns)
            for col in columns:
                arrays[col].append(res[col].astype(np.float64))
        out[proc] = {col: np.concatenate(arrays[col]) if arrays[col] else np.zeros(0) for col in columns}
        print(f'  {proc}: {len(out[proc]["w"])} events after base selection, sum w = {out[proc]["w"].sum():.3f}, '
              f'{time.time() - t_proc:.0f} s (total {time.time() - t_start:.0f} s)', flush=True)
    return out


# Version of the cache content: caches made before the 1j/2j/incl update stored region-specific dphi values
CACHE_LAYOUT = 'v2'


def save_cache(path, data, signal):
    flat = {}
    for proc, arr in data.items():
        for col, v in arr.items():
            flat[f'{proc}::{col}'] = v
    flat['__signal__'] = np.array(sorted(signal))
    flat['__layout__'] = np.array(CACHE_LAYOUT)
    np.savez_compressed(path, **flat)
    print(f'Arrays saved to {path}')


def load_cache(path):
    f = np.load(path, allow_pickle=False)
    if '__layout__' not in f.files or str(f['__layout__']) != CACHE_LAYOUT:
        sys.exit(f'ERROR: {path} was made with an older version of this script (region-specific variables): '
                 f'read the trees again with --cache')
    data = OrderedDict()
    for key in f.files:
        if key in ('__signal__', '__layout__'):
            continue
        proc, col = key.split('::')
        data.setdefault(proc, {})[col] = f[key]
    return data, set(f['__signal__'].tolist())


###############################################################################
# Selection logic
###############################################################################

def pass_cut(arr, cut, thr=None):
    v = arr[f'cv_{cut["name"]}']
    if cut['op'] == 'fixed':
        return fixed_mask(arr, cut)
    if thr is None:
        thr = cut['nominal']
    if thr is None:
        return np.ones(len(v), dtype=bool)
    return v > thr if cut['op'] == '>' else v < thr


def fixed_mask(arr, cut):
    v = arr[f'cv_{cut["name"]}']
    m = re.match(r'\s*\w+\s*(>=|==|>|<|<=)\s*([0-9.]+)', cut['fixed'])
    op, val = m.group(1), float(m.group(2))
    return {'>=': v >= val, '==': v == val, '>': v > val, '<': v < val, '<=': v <= val}[op]


def mask_all(arr, cuts, skip=None):
    m = np.ones(len(arr['w']), dtype=bool)
    for c in cuts:
        if c['name'] == skip:
            continue
        m &= pass_cut(arr, c)
    return m


def asimov(s, b):
    if b <= 0 or s <= 0:
        return 0.
    return np.sqrt(2. * ((s + b) * np.log(1. + s / b) - s))


def s_over_sqrtb(s, b):
    return s / np.sqrt(b) if b > 0 else 0.


def s_over_b(s, b):
    return s / b if b > 0 else 0.


###############################################################################
# Outputs
###############################################################################

def cutflow(data, signal, cuts, outdir):
    procs = list(data.keys())
    bkg = [p for p in procs if p not in signal]
    masks = {p: np.ones(len(data[p]['w']), dtype=bool) for p in procs}
    rows = []
    steps = [('base', None)] + [(c['name'], c) for c in cuts if c['op'] == 'fixed' or c['nominal'] is not None]
    prev_s = prev_b = None
    first_s = first_b = None
    for name, c in steps:
        if c is not None:
            for p in procs:
                masks[p] &= pass_cut(data[p], c)
        y = {p: data[p]['w'][masks[p]].sum() for p in procs}
        s = sum(y[p] for p in signal)
        b = sum(y[p] for p in bkg)
        if first_s is None:
            first_s, first_b = s, b
        row = OrderedDict(step=name)
        row.update({p: y[p] for p in procs})
        row['S'] = s
        row['B'] = b
        row['SE_step'] = s / prev_s if prev_s else 1.
        row['BR_step'] = 1. - b / prev_b if prev_b else 0.
        row['SE_cumul'] = s / first_s if first_s else 0.
        row['BR_cumul'] = 1. - b / first_b if first_b else 0.
        row['S/B'] = s_over_b(s, b)
        row['S/sqrtB'] = s_over_sqrtb(s, b)
        row['Z_Asimov'] = asimov(s, b)
        rows.append(row)
        prev_s, prev_b = s, b

    # without signal, keep only the background columns
    if not signal:
        for r in rows:
            for k in ('S', 'SE_step', 'SE_cumul', 'S/B', 'S/sqrtB', 'Z_Asimov'):
                del r[k]

    path = os.path.join(outdir, 'cutflow.csv')
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f'{v:.5g}' if isinstance(v, float) else v) for k, v in r.items()})

    # print
    print('\nCUTFLOW (weighted yields)')
    if signal:
        head = f'{"step":<12}' + ''.join(f'{p:>10}' for p in procs) + f'{"S":>10}{"B":>10}{"SEstep":>8}{"BRstep":>8}{"SEcum":>8}{"BRcum":>8}{"S/B":>8}{"S/sqB":>8}{"Z_A":>8}'
    else:
        head = f'{"step":<12}' + ''.join(f'{p:>10}' for p in procs) + f'{"B":>10}{"BRstep":>8}{"BRcum":>8}'
    print(head)
    for r in rows:
        line = f'{r["step"]:<12}' + ''.join(f'{r[p]:>10.2f}' for p in procs)
        if signal:
            line += f'{r["S"]:>10.3f}{r["B"]:>10.2f}{r["SE_step"]:>8.3f}{r["BR_step"]:>8.3f}{r["SE_cumul"]:>8.3f}{r["BR_cumul"]:>8.3f}{r["S/B"]:>8.4f}{r["S/sqrtB"]:>8.3f}{r["Z_Asimov"]:>8.3f}'
        else:
            line += f'{r["B"]:>10.2f}{r["BR_step"]:>8.3f}{r["BR_cumul"]:>8.3f}'
        print(line)
    print(f'Saved {path}')
    return rows, steps


def step_label(name, c):
    # x-axis label of a cutflow step, e.g. "pt3 > 15" or "njet: ZH3l_njet >= 2"
    if c is None:
        return 'base'
    if c['op'] == 'fixed':
        return f'{name}\n{c["fixed"].replace(name, "").strip()}' if c['fixed'].startswith(name) else f'{name}\n{c["fixed"]}'
    return f'{name}\n{c["op"]} {c["nominal"]:g}'


def plot_cutflow(rows, steps, data, signal, outdir, plt, region=''):
    # yield of each sample after each cut of the nominal selection:
    # cutflow.png (linear scale) and cutflow_log.png (log scale, yields <= 0 not drawn)
    procs = list(data.keys())
    bkg = [p for p in procs if p not in signal]
    x = np.arange(len(rows))
    for log in (False, True):
        mask = (lambda y: np.where(y > 0, y, np.nan)) if log else (lambda y: y)
        fig, ax = plt.subplots(figsize=(max(8, 0.9 * len(rows) + 3), 5.5))
        # samples ordered by their final yield, largest first in the legend
        for p in sorted(bkg, key=lambda p: -rows[-1][p]):
            y = np.array([r[p] for r in rows], dtype=float)
            ax.plot(x, mask(y), 'o-', markersize=4, label=f'{p} ({rows[-1][p]:.2f})')
        for p in signal:
            y = np.array([r[p] for r in rows], dtype=float)
            ax.plot(x, mask(y), 'o--', linewidth=2, label=f'{p} ({rows[-1][p]:.3f})')
        b = np.array([r['B'] for r in rows], dtype=float)
        ax.plot(x, mask(b), 'ks-', linewidth=2.5, label=f'total background ({rows[-1]["B"]:.2f})')
        if log:
            ax.set_yscale('log')
        else:
            ax.axhline(0., color='gray', linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels([step_label(n, c) for n, c in steps], fontsize=8)
        ax.set_xlabel('cut (applied cumulatively, left to right)')
        ax.set_ylabel('weighted yield')
        ax.set_title(f'Cutflow, region {region}, nominal selection (yield after the cut; legend: final yield)', fontsize=10)
        ax.grid(alpha=0.3, which='both')
        ax.legend(fontsize=7, ncol=2, loc='lower left' if log else 'upper right')
        fig.tight_layout()
        name = 'cutflow_log.png' if log else 'cutflow.png'
        fig.savefig(os.path.join(outdir, name))
        plt.close(fig)
        print(f'Saved {name}')


def tex2mpl(label):
    # minimal ROOT-latex to matplotlib conversion
    l = label.replace('#Delta', r'\Delta').replace('#phi', r'\phi').replace('#', '\\')
    return f'${l}$'.replace(' ', r'\ ') if ('_' in l or '^' in l or '\\' in l) else label


def plot_nminus1(data, signal, cut, cuts, outdir, signal_scale, plt, region=''):
    procs = list(data.keys())
    bkg = [p for p in procs if p not in signal]
    lo, hi, nb = cut['hrange']
    edges = np.linspace(lo, hi, nb + 1)

    fig, ax = plt.subplots(figsize=(7, 5))
    vals, ws, labs = [], [], []
    for p in sorted(bkg, key=lambda p: data[p]['w'][mask_all(data[p], cuts, skip=cut['name'])].sum()):
        m = mask_all(data[p], cuts, skip=cut['name'])
        vals.append(np.clip(data[p][f'cv_{cut["name"]}'][m], lo, hi - 1e-9))
        ws.append(data[p]['w'][m])
        labs.append(f'{p} ({ws[-1].sum():.1f})')
    if vals:
        ax.hist(vals, bins=edges, weights=ws, stacked=True, histtype='stepfilled', label=labs, alpha=0.85)
    for p in signal:
        m = mask_all(data[p], cuts, skip=cut['name'])
        v = np.clip(data[p][f'cv_{cut["name"]}'][m], lo, hi - 1e-9)
        w = data[p]['w'][m]
        ax.hist(v, bins=edges, weights=w * signal_scale, histtype='step', linewidth=2,
                label=f'{p} x{signal_scale:g} ({w.sum():.2f})')
    if cut['op'] != 'fixed' and cut['nominal'] is not None:
        ax.axvline(cut['nominal'], color='k', linestyle='--', label=f'nominal ({cut["op"]} {cut["nominal"]:g})')
    elif cut['op'] == 'fixed':
        m = re.match(r'\s*\w+\s*(>=|==|>|<|<=)\s*([0-9.]+)', cut['fixed'])
        ax.axvline(float(m.group(2)), color='k', linestyle='--', label=f'fixed ({m.group(1)} {m.group(2)})')
    ax.set_xlabel(tex2mpl(cut['label']))
    ax.set_ylabel('Events / bin')
    ax.set_title(f'N-1, region {region}: all cuts except {cut["name"]} (under/overflow in edge bins)', fontsize=10)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, f'nminus1_{cut["name"]}.png'))
    ax.set_yscale('log')
    ax.set_ylim(bottom=1e-3)
    fig.savefig(os.path.join(outdir, f'nminus1_{cut["name"]}_log.png'))
    plt.close(fig)


def scan_cut(data, signal, cut, cuts, outdir, plt, region=''):
    procs = list(data.keys())
    bkg = [p for p in procs if p not in signal]
    # events passing all the other cuts at nominal: the scanned cut is then applied at each threshold y
    base = {p: mask_all(data[p], cuts, skip=cut['name']) for p in procs}
    # reference: all the cuts at nominal, scanned cut included -> BR(y) = B(y) / B(nominal), SE(y) = S(y) / S(nominal)
    nom = {p: mask_all(data[p], cuts) for p in procs}
    s0 = sum(data[p]['w'][nom[p]].sum() for p in signal)
    b0 = sum(data[p]['w'][nom[p]].sum() for p in bkg)

    rows = []
    for i, thr in enumerate(cut['scan']):
        y = {p: data[p]['w'][base[p] & pass_cut(data[p], cut, thr)].sum() for p in procs}
        s = sum(y[p] for p in signal)
        b = sum(y[p] for p in bkg)
        row = OrderedDict(threshold=float(thr))
        if 'scan_labels' in cut:
            row['label'] = cut['scan_labels'][i]
        if signal:
            row.update(S=s, B=b, SE=s / s0 if s0 else 0., BR=b / b0 if b0 else 0.,
                       S_over_B=s_over_b(s, b), S_over_sqrtB=s_over_sqrtb(s, b), Z_Asimov=asimov(s, b))
        else:
            row.update(B=b, BR=b / b0 if b0 else 0.)
        row.update({f'N_{p}': y[p] for p in procs})
        rows.append(row)

    path = os.path.join(outdir, f'scan_{cut["name"]}.csv')
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f'{v:.5g}' if isinstance(v, float) else v) for k, v in r.items()})

    x = np.arange(len(rows)) if 'scan_labels' in cut else np.array([r['threshold'] for r in rows])
    if signal:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
        # BR on the left y axis, SE on the secondary (right) y axis
        ax1.plot(x, [r['BR'] for r in rows], 's-', color='C1', label='BR = B(y) / B(nominal)')
        ax1.set_ylabel('BR = B(y) / B(nominal)', color='C1')
        ax1.tick_params(axis='y', colors='C1')
        ax1r = ax1.twinx()
        ax1r.plot(x, [r['SE'] for r in rows], 'o-', color='C0', label='SE = S(y) / S(nominal)')
        ax1r.set_ylabel('SE = S(y) / S(nominal)', color='C0')
        ax1r.tick_params(axis='y', colors='C0')
        # same range on both y axes, so that BR and SE can be compared directly (1 = nominal on both)
        ylo = min(ax1.get_ylim()[0], ax1r.get_ylim()[0])
        yhi = max(ax1.get_ylim()[1], ax1r.get_ylim()[1])
        ax1.set_ylim(ylo, yhi)
        ax1r.set_ylim(ylo, yhi)
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax1r.get_legend_handles_labels()
        # nominal yields in the legend box (drawn on the right axis, so that it is on top of both curves)
        ax1r.legend(h1 + h2, l1 + l2, fontsize=8, title_fontsize=8, framealpha=0.9,
                    title=f'B(nominal) = {b0:.2f}, S(nominal) = {s0:.3f} (weighted events)')
        ax2.plot(x, [r['S_over_sqrtB'] for r in rows], 'o-', label='S/sqrt(B)')
        ax2.plot(x, [r['Z_Asimov'] for r in rows], 's--', label='Asimov Z')
        ax2.set_ylabel('significance')
        ax2.grid(alpha=0.3)
        # S/B on the secondary (right) y axis of the bottom panel (much smaller than the significances)
        ax2r = ax2.twinx()
        ax2r.plot(x, [r['S_over_B'] for r in rows], '^:', color='C2', label='S/B')
        ax2r.set_ylabel('S/B', color='C2')
        ax2r.tick_params(axis='y', colors='C2')
        h1, l1 = ax2.get_legend_handles_labels()
        h2, l2 = ax2r.get_legend_handles_labels()
        ax2r.legend(h1 + h2, l1 + l2, fontsize=8, framealpha=0.9)
        axes = (ax1, ax2)
        title = f'Scan of {cut["name"]}, region {region} (all other cuts nominal; S(nominal)={s0:.3f}, B(nominal)={b0:.2f})'
    else:
        fig, ax1 = plt.subplots(figsize=(7, 4.5))
        ax1.plot(x, [r['BR'] for r in rows], 's-', color='C1', label='BR = B(y) / B(nominal)')
        ax1.set_ylabel('BR = B(y) / B(nominal)')
        # nominal yield in the legend box
        ax1.legend(fontsize=8, title_fontsize=8, framealpha=0.9, title=f'B(nominal) = {b0:.2f} (weighted events)')
        ax2 = ax1
        axes = (ax1,)
        title = f'Scan of {cut["name"]}, region {region} (all other cuts nominal; B(nominal)={b0:.2f})'
    # BR > 1 for thresholds looser than nominal (more background than nominal), BR = 1 at the nominal threshold
    ax1.axhline(1., color='gray', linewidth=0.8)
    ax1.grid(alpha=0.3)
    if cut['nominal'] is not None:
        xn = list(cut['scan']).index(cut['nominal']) if 'scan_labels' in cut else cut['nominal']
        for ax in axes:
            ax.axvline(xn, color='k', linestyle='--', alpha=0.6)
    if 'scan_labels' in cut:
        ax2.set_xticks(x)
        ax2.set_xticklabels(cut['scan_labels'])
    ax2.set_xlabel(f'{tex2mpl(cut["label"])}  cut: keep {cut["op"]} threshold')
    ax1.set_title(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, f'scan_{cut["name"]}.png'))
    plt.close(fig)
    print(f'Saved scan_{cut["name"]}.csv/.png')


###############################################################################
# Main
###############################################################################

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--config-dir', default=os.path.dirname(here), help='mkShapesRDF configuration folder')
    ap.add_argument('--region', choices=REGIONS + ['all'], default='all',
                    help='1j: exactly 1 jet, 2j: >= 2 jets, incl: >= 1 jet (1j + 2j), all: the three of them (default)')
    ap.add_argument('--outdir', default=None, help='parent folder of the plots_<region> folders (default: cut_scan/)')
    ap.add_argument('--max-files', type=int, default=-1, help='files per sample (-1 = all)')
    ap.add_argument('--threads', type=int, default=0, help='ROOT implicit MT threads (0 = all cores)')
    ap.add_argument('--cache', default=None, help='save the per-event arrays to this .npz file')
    ap.add_argument('--from-cache', default=None, help='read the arrays from this .npz file instead of the trees')
    ap.add_argument('--signal-scale', type=float, default=10., help='signal scale factor in the N-1 plots')
    args = ap.parse_args()

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    regions = REGIONS if args.region == 'all' else [args.region]
    outbase = args.outdir or here

    if args.from_cache:
        data, signal = load_cache(args.from_cache)
    else:
        g, lumi = load_config(args.config_dir)
        procs, signal = build_sample_list(g, args.max_files)
        print(f'lumi = {lumi} /fb, backgrounds = {[p for p in procs if p not in signal]}, signal = {sorted(signal)}')
        # the 2j cut list contains all the variables (incl. mjj): one read serves all the regions
        data = read_arrays(g, lumi, procs, signal, get_cuts('2j'), args.threads)
        if args.cache:
            save_cache(args.cache, data, signal)

    if not signal:
        print('No signal samples: only background yields and background rejection are shown')

    # negative MC weights (NLO samples): can give negative bins in the N-1 plots when few events are left
    print('\nNEGATIVE WEIGHTS after base selection')
    print(f'{"process":<10}{"events":>10}{"frac w<0":>10}{"sum w":>12}{"sum w<0":>12}')
    for p, arr in data.items():
        w = arr['w']
        if len(w) == 0:
            continue
        print(f'{p:<10}{len(w):>10}{(w < 0).mean():>10.3f}{w.sum():>12.3f}{w[w < 0].sum():>12.3f}')

    for region in regions:
        print(f'\n==================== REGION {region} ====================')
        cuts = get_cuts(region)
        outdir = os.path.join(outbase, f'plots_{region}')
        os.makedirs(outdir, exist_ok=True)
        rows, steps = cutflow(data, signal, cuts, outdir)
        plot_cutflow(rows, steps, data, signal, outdir, plt, region)
        for c in cuts:
            plot_nminus1(data, signal, c, cuts, outdir, args.signal_scale, plt, region)
            if c['op'] != 'fixed':
                scan_cut(data, signal, c, cuts, outdir, plt, region)
        print(f'Outputs for region {region} in {outdir}')


if __name__ == '__main__':
    main()
