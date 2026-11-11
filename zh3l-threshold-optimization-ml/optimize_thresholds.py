#!/usr/bin/env python3
"""
Simultaneous optimization of the ZH3l selection thresholds with soft (sigmoid) cuts trained by gradient descent.

All the thresholds scanned by cut_scan.py are trained at the same time to maximize the significance (Asimov Z by
default), with the sharpness of the soft cuts annealed from soft to hard during the training, as the SoftQuantize
layer of https://github.com/ArghyaRanjanDas/smart-pixels-ml/tree/SoftQuantize. Several runs (different starting
thresholds, bootstrap resampling of the training events) are made; the best one on the training sample, rounded to
the cut_scan grid, is then pruned on an independent test sample: a threshold change is kept only if it improves the hard-cut significance
by more than --min-gain and more than its statistical uncertainty. See README.md for the details.

Input: the per-event arrays cached by cut_scan.py (--cache), so the trees are not read again.

Usage (numpy and matplotlib only; on lxplus e.g. after sourcing mkShapesRDF/start.sh, or on a laptop):
    python3 optimize_thresholds.py --cache ../ControlRegions/WZ_zh3l/2022_v12_wClaude_SR/cut_scan/arrays.npz
    python3 optimize_thresholds.py --cache arrays.npz --region incl --runs 5 --epochs 200    # quick test
    python3 optimize_thresholds.py --cache arrays.npz --freeze pt1,pt2 --jobs 8
    python3 optimize_thresholds.py --cache arrays.npz --replot                              # only redo the plots
"""

import os
import re
import sys
import csv
import json
import time
import argparse
import multiprocessing
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from softcuts import Problem, train_run, hard_significance   # noqa: E402
from validation import select_best, round_all, prune, evaluate, bootstrap_significance   # noqa: E402
import plots   # noqa: E402

DEFAULT_CUT_SCAN = os.path.join(HERE, '..', 'ControlRegions', 'WZ_zh3l', '2022_v12_wClaude_SR', 'cut_scan')


def import_cut_scan(path):
    # cut definitions (get_cuts), cache reader and helpers are taken from cut_scan.py, so both use the same cuts
    sys.path.insert(0, os.path.abspath(path))
    import cut_scan
    return cut_scan


def read_lumi(cut_scan_dir):
    # luminosity of the configuration read by cut_scan (configuration.py one folder up), for the CMS label
    try:
        with open(os.path.join(cut_scan_dir, '..', 'configuration.py')) as f:
            m = re.search(r'^lumi\s*=\s*([0-9.eE+-]+)', f.read(), re.M)
        return float(m.group(1)) if m else None
    except OSError:
        return None


###############################################################################
# Runs (parallel with fork: the events are shared through this global)
###############################################################################

_CTX = {}


def run_one(r):
    c = _CTX
    prob, cfg, tr, te = c['prob'], c['cfg'], c['train'], c['test']
    rng = np.random.default_rng(cfg['seed'] * 1000 + r + 1)
    w_tr = prob.w[tr] / (1. - cfg['test_fraction'])
    if r > 0:
        # bootstrap resampling of the training events: the spread of the runs includes the MC statistical fluctuations
        w_tr = w_tr * rng.poisson(1., size=len(w_tr))
        span = prob.theta_hi - prob.theta_lo
        theta0 = np.clip(prob.theta_ref + rng.uniform(-1., 1., size=len(span)) * cfg['init_spread'] * span,
                         prob.theta_lo, prob.theta_hi)
    else:
        # run 0: nominal start, no resampling
        theta0 = prob.theta_ref.copy()
    V, sig = prob.V[tr], prob.sig[tr]
    z0 = hard_significance(V, w_tr, sig, prob.theta_ref, cfg['objective'])
    if z0 <= 0:
        raise RuntimeError('nominal significance is 0 on the training sample: no signal events?')
    w_te = prob.w[te] / cfg['test_fraction']
    evals = {'train': (V, w_tr, sig), 'test': (prob.V[te], w_te, prob.sig[te])}
    t0 = time.time()
    h = train_run(V[sig], w_tr[sig], V[~sig], w_tr[~sig], theta0, prob.theta_ref, prob.theta_lo, prob.theta_hi,
                  cfg, z0, evals)
    h['T'] = prob.t_of(h.pop('theta'))
    print(f'  run {r:3d}: {time.time() - t0:5.1f} s, hard-cut Z train {h["zhard_train"][0]:.3f} -> '
          f'{h["zhard_train"][-1]:.3f}, test {h["zhard_test"][0]:.3f} -> {h["zhard_test"][-1]:.3f}', flush=True)
    return h


def run_all(prob, cfg, tr, te, jobs):
    _CTX.update(prob=prob, cfg=cfg, train=tr, test=te)
    runs = list(range(cfg['runs']))
    if jobs > 1:
        with multiprocessing.get_context('fork').Pool(jobs) as pool:
            hists = pool.map(run_one, runs)
    else:
        hists = [run_one(r) for r in runs]
    # stack the runs: every entry gets a leading run axis (except the evaluation epochs, the same for all the runs)
    hist = {key: np.stack([h[key] for h in hists]) for key in hists[0]}
    hist['eval_epochs'] = hists[0]['eval_epochs']
    return hist


###############################################################################
# Outputs
###############################################################################

def fmt(v):
    return f'{v:.5g}' if isinstance(v, float) else v


def write_csv(path, rows):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: fmt(v) for k, v in r.items()})


def selection_strings(prob, t):
    out = []
    for j, c in enumerate(prob.cuts):
        if prob.is_off(j, t[j]):
            continue
        expr = c['expr'] if not any(ch in c['expr'] for ch in ' ?:<>=&|') else f'({c["expr"]})'
        out.append(f'{expr} {prob.ops[j]} {t[j]:g}')
    return out


def write_outputs(prob, cfg, hist, res, outdir):
    J = len(prob.names)
    T_final = hist['T'][:, -1, :]
    first = res['prune_steps'][0] if res['prune_steps'] else None
    rows = []
    for j in range(J):
        dz = dz_err = ''
        if first and prob.names[j] in first['cuts']:
            i = first['cuts'].index(prob.names[j])
            dz, dz_err = first['dZ'][i], first['dZ_err'][i]
        t_c, t_f = res['t_best'][j], res['t_final'][j]
        rounded = [prob.round_threshold(j, t) for t in T_final[:, j]]
        if prob.is_ref(j, t_c):
            status = 'unchanged'
        else:
            status = 'kept' if not prob.is_ref(j, t_f) else 'reverted (gain too small)'
        rows.append(dict(cut=prob.names[j], op=prob.ops[j],
                         nominal=('not applied' if not prob.applied[j] else float(prob.t_ref[j])),
                         scan_range=f'{prob.scan_lo[j]:g}..{prob.scan_hi[j]:g}', step=float(prob.tau[j]),
                         runs_median=float(np.median(T_final[:, j])), runs_std=float(T_final[:, j].std()),
                         frac_runs_changed=float(np.mean([not prob.is_ref(j, t) for t in rounded])),
                         # runs that agree with the best run within one scan step (or are also "off")
                         frac_runs_agree=float(np.mean([(prob.is_off(j, t) and prob.is_off(j, t_c)) or
                                                        abs(t - t_c) <= prob.tau[j] + 1e-9 for t in rounded])),
                         best_run=('not applied' if prob.is_off(j, t_c) else t_c),
                         final=('not applied' if prob.is_off(j, t_f) else t_f),
                         status=status, dZ_test_first_iteration=dz, dZ_err=dz_err))
    write_csv(os.path.join(outdir, 'thresholds.csv'), rows)

    yrows = []
    for sel in ('nominal', 'best_run', 'final'):
        for sample in ('train', 'test', 'all'):
            e = res['yields'][sel][sample]
            yrows.append(dict(selection=sel, sample=sample, S=e['S'], B=e['B'], S_over_B=e['S_over_B'],
                              S_over_sqrtB=e['S_over_sqrtB'], Z=e['Z'],
                              Z_boot_err=(res['z_test'][sel][1] if sample == 'test' else '')))
    write_csv(os.path.join(outdir, 'yields.csv'), yrows)
    write_csv(os.path.join(outdir, 'yields_per_process.csv'),
              [dict(process=p, nominal=res['per_process']['nominal'][p], final=res['per_process']['final'][p],
                    ratio=(res['per_process']['final'][p] / res['per_process']['nominal'][p]
                           if res['per_process']['nominal'][p] else 0.)) for p in prob.proc_names])

    with open(os.path.join(outdir, 'summary.txt'), 'w') as f:
        f.write(summary_text(prob, cfg, res))
    with open(os.path.join(outdir, 'results.json'), 'w') as f:
        json.dump(dict(cfg=cfg, names=prob.names, t_best=list(res['t_best']), best_run=res['best_run'],
                       z_runs_train=list(res['z_runs_train']), t_final=list(res['t_final']),
                       prune_steps=res['prune_steps'], z_test=res['z_test'], yields=res['yields'],
                       per_process=res['per_process']), f, indent=1)
    np.savez_compressed(os.path.join(outdir, 'history.npz'), **hist)


def summary_text(prob, cfg, res):
    L = [f'Region {cfg["region"]}, objective {cfg["objective"]}, {cfg["runs"]} runs x {cfg["epochs"]} epochs',
         f'Best run on the training sample: run {res["best_run"]} (hard-cut Z of the rounded thresholds, train: '
         + ', '.join(f'{z:.3f}' for z in res['z_runs_train']) + ')', '']
    L.append(f'{"cut":<12}{"nominal":>14}{"best run":>14}{"final":>14}')
    for j in range(len(prob.names)):
        def s(t):
            return 'off' if prob.is_off(j, t) else f'{prob.ops[j]} {t:g}'
        L.append(f'{prob.names[j]:<12}{s(prob.t_ref[j]):>14}{s(res["t_best"][j]):>14}{s(res["t_final"][j]):>14}')
    L.append('')
    L.append(f'{"selection":<11}{"sample":<7}{"S":>9}{"B":>10}{"S/B":>9}{"S/sqrtB":>9}{"Z":>8}{"+-":>7}')
    for sel in ('nominal', 'best_run', 'final'):
        for sample in ('train', 'test', 'all'):
            e = res['yields'][sel][sample]
            err = f'{res["z_test"][sel][1]:.3f}' if sample == 'test' else ''
            L.append(f'{sel:<11}{sample:<7}{e["S"]:>9.3f}{e["B"]:>10.2f}{e["S_over_B"]:>9.4f}{e["S_over_sqrtB"]:>9.3f}'
                     f'{e["Z"]:>8.3f}{err:>7}')
    L.append('')
    L.append('Pruning (test sample): dZ = Z(current) - Z(current with the cut at nominal)')
    for k, st in enumerate(res['prune_steps']):
        L.append(f'  iteration {k}: Z = {st["Z"]:.3f} +- {st["Z_err"]:.3f}')
        for c, t, dz, e, req in zip(st['cuts'], st['thresholds'], st['dZ'], st['dZ_err'], st['required']):
            L.append(f'    {c:<12} {t:>8g}  dZ = {dz:+.4f} +- {e:.4f}  (required {req:.4f})')
        if st['reverted']:
            L.append(f'    -> {st["reverted"]} reverted to nominal')
    if not res['prune_steps']:
        L.append('  no threshold changed w.r.t. nominal')
    L.append('')
    L.append('Final selection of the trained cuts (mkShapesRDF syntax; fixed and frozen cuts not listed):')
    for s in selection_strings(prob, res['t_final']):
        L.append(f'  {s}')
    return '\n'.join(L) + '\n'


###############################################################################
# Main
###############################################################################

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--cache', required=True, help='arrays.npz made by cut_scan.py --cache')
    ap.add_argument('--cut-scan-dir', default=DEFAULT_CUT_SCAN, help='folder of cut_scan.py (cut definitions)')
    ap.add_argument('--region', choices=['1j', '2j', 'incl', 'all'], default='all')
    ap.add_argument('--outdir', default=os.path.join(HERE, 'results'), help='parent folder of the <region> folders')
    ap.add_argument('--freeze', default='', help='comma-separated cuts kept at their nominal value (not trained)')
    ap.add_argument('--objective', choices=['asimov', 's_over_sqrtb'], default='asimov')
    ap.add_argument('--runs', type=int, default=20, help='number of training runs')
    ap.add_argument('--epochs', type=int, default=600)
    ap.add_argument('--lr', type=float, default=0.1, help='Adam learning rate, in scan steps per epoch')
    ap.add_argument('--k-start', type=float, default=0.5, help='sharpness of the soft cuts at the start')
    ap.add_argument('--k-end', type=float, default=50., help='sharpness of the soft cuts at the end')
    ap.add_argument('--k-schedule', choices=['cosine', 'linear', 'exponential'], default='cosine')
    ap.add_argument('--lam', type=float, default=0.002,
                    help='L1 pull to nominal: fraction of the nominal Z that one scan step of change must gain')
    ap.add_argument('--min-neff', type=float, default=30.,
                    help='minimum effective number of MC background events (0 = no constraint)')
    ap.add_argument('--neff-weight', type=float, default=1., help='weight of the min-neff penalty')
    ap.add_argument('--init-spread', type=float, default=0.5,
                    help='runs > 0 start at nominal + uniform(-1, 1) x spread x threshold range')
    ap.add_argument('--test-fraction', type=float, default=0.5, help='fraction of the events used as test sample')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--eval-every', type=int, default=5, help='hard-cut Z evaluated every N epochs')
    ap.add_argument('--min-gain', type=float, default=0.01, help='pruning: minimum relative gain in Z of a change')
    ap.add_argument('--n-sigma', type=float, default=1., help='pruning: minimum gain in units of its stat. uncertainty')
    ap.add_argument('--n-boot', type=int, default=200, help='bootstrap replicas for the uncertainties')
    ap.add_argument('--signal-scale', type=float, default=10., help='signal scale factor in the N-1 plots')
    ap.add_argument('--jobs', type=int, default=1, help='runs trained in parallel')
    ap.add_argument('--no-gif', action='store_true', help='do not make the N-1 animation')
    ap.add_argument('--lumi', type=float, default=None,
                    help='luminosity in the CMS label, in 1/fb (default: lumi of configuration.py next to cut_scan)')
    ap.add_argument('--cms-label', default='Simulation Preliminary',
                    help='text after "CMS" in the plots (MC only: Simulation ...)')
    ap.add_argument('--replot', action='store_true', help='only redo the plots from results/<region>/')
    args = ap.parse_args()

    if not 0. < args.test_fraction < 1.:
        sys.exit('ERROR: --test-fraction must be in (0, 1)')

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    cs = import_cut_scan(args.cut_scan_dir)
    lumi = args.lumi if args.lumi is not None else read_lumi(args.cut_scan_dir)
    plots.set_style(plt, lumi, args.cms_label)
    data, signal = cs.load_cache(args.cache)
    if not signal:
        sys.exit('ERROR: no signal samples in the cache: rerun cut_scan.py --cache with SIGNAL defined')
    freeze = [c for c in args.freeze.split(',') if c]
    regions = ['1j', '2j', 'incl'] if args.region == 'all' else [args.region]

    for region in regions:
        print(f'\n==================== REGION {region} ====================')
        outdir = os.path.join(args.outdir, region)
        os.makedirs(outdir, exist_ok=True)
        prob = Problem(data, signal, cs.get_cuts(region), cs.pass_cut, freeze)
        if not prob.names:
            sys.exit('ERROR: no cut left to train')
        print(f'Trained cuts: {prob.names}; fixed/frozen: {[c["name"] for c in prob.fixed]}; '
              f'skipped (not in the nominal selection): {[c["name"] for c in prob.skipped]}')
        print(f'{len(prob.w)} events ({prob.sig.sum()} signal) after the fixed cuts and the loosest thresholds')

        if args.replot:
            with open(os.path.join(outdir, 'results.json')) as f:
                res = json.load(f)
            cfg = res['cfg']
            hist = dict(np.load(os.path.join(outdir, 'history.npz')))
            res['t_best'], res['t_final'] = np.array(res['t_best']), np.array(res['t_final'])
        else:
            cfg = {k: v for k, v in vars(args).items() if k not in ('cache', 'outdir', 'jobs', 'replot', 'no_gif')}
            cfg['region'] = region
            # fixed train/test split (same for all the runs): the test sample is never used in the training
            is_test = np.random.default_rng(args.seed).random(len(prob.w)) < args.test_fraction
            tr, te = np.where(~is_test)[0], np.where(is_test)[0]
            print(f'{len(tr)} training / {len(te)} test events; {args.runs} runs x {args.epochs} epochs')
            hist = run_all(prob, cfg, tr, te, args.jobs)
            res = validate(prob, cfg, hist, tr, te)
            write_outputs(prob, cfg, hist, res, outdir)
            print(summary_text(prob, cfg, res))

        z_test = {k: tuple(v) for k, v in res['z_test'].items()}
        plots.plot_threshold_evolution(prob, hist['T'], res['t_final'], outdir, plt, cs.tex2mpl, region)
        plots.plot_training_history(hist, z_test['nominal'][0], cfg, outdir, plt, region)
        plots.plot_soft_vs_hard(prob, cfg, outdir, plt, cs.tex2mpl)
        plots.plot_pruning(res['prune_steps'], cfg['min_gain'], cfg['n_sigma'], outdir, plt, region)
        plots.plot_run_summary(hist, z_test, res['best_run'], outdir, plt, region)
        plots.plot_nminus1_final(prob, res['t_final'], args.signal_scale, outdir, plt, cs.tex2mpl, region)
        if not args.no_gif:
            path = plots.make_gif(prob, hist['T'][0], hist, 0, args.signal_scale, outdir, plt, cs.tex2mpl, region)
            print(f'Saved {path}')
        print(f'Outputs for region {region} in {outdir}')


def validate(prob, cfg, hist, tr, te):
    obj = cfg['objective']
    V_tr, w_tr, s_tr = prob.V[tr], prob.w[tr] / (1. - cfg['test_fraction']), prob.sig[tr]
    V_te, w_te, s_te = prob.V[te], prob.w[te] / cfg['test_fraction'], prob.sig[te]
    # best run on the training sample (test sample not used), then pruning on the test sample
    t_best, best_run, z_runs_train = select_best(prob, hist['T'][:, -1, :], V_tr, w_tr, s_tr, obj)
    t_final, steps = prune(prob, V_te, w_te, s_te, t_best, cfg['min_gain'], cfg['n_sigma'], cfg['n_boot'],
                           cfg['seed'], obj)
    sels = {'nominal': prob.t_ref, 'best_run': t_best, 'final': t_final}
    samples = {'train': (V_tr, w_tr, s_tr), 'test': (V_te, w_te, s_te), 'all': (prob.V, prob.w, prob.sig)}
    yields = {s: {n: evaluate(*samples[n], prob.theta_of(t), obj) for n in samples} for s, t in sels.items()}
    zb = bootstrap_significance(V_te, w_te, s_te, [prob.theta_of(t) for t in sels.values()], cfg['n_boot'],
                                cfg['seed'], obj)
    z_test = {s: (yields[s]['test']['Z'], float(zb[:, i].std())) for i, s in enumerate(sels)}
    per_process = {}
    for s in ('nominal', 'final'):
        m = (prob.V > prob.theta_of(sels[s])).all(axis=1)
        per_process[s] = {p: float(prob.w[m & (prob.proc == i)].sum()) for i, p in enumerate(prob.proc_names)}
    return dict(t_best=t_best, best_run=best_run, z_runs_train=z_runs_train, t_final=t_final, prune_steps=steps,
                yields=yields, z_test=z_test, per_process=per_process)


if __name__ == '__main__':
    main()
