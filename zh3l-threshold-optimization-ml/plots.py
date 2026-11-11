"""
Plots of optimize_thresholds.py. The threshold-evolution plots follow Thr_summary.png of
https://github.com/ArghyaRanjanDas/smart-pixels-ml/tree/SoftQuantize (threshold vs epoch for all the runs, epochs
going down, and the distribution of the final values of the runs below).

CMS style in plain matplotlib (no mplhep needed): set_style() is called once by optimize_thresholds.py, before any plot.
"""

import os
import numpy as np
from matplotlib.ticker import MaxNLocator
from matplotlib.transforms import blended_transform_factory

from softcuts import k_schedule, lr_schedule

# CMS label: "CMS <extra>" above the left corner, "<lumi> fb-1 (13.6 TeV)" above the right corner (set by set_style)
CMS = dict(extra='Simulation Preliminary', lumi=None, com=13.6)

# Petroff 10-colour palette, recommended by CMS (C0, C1, ... in the plots below)
PETROFF10 = ['#3f90da', '#ffa90e', '#bd1f01', '#94a4a2', '#832db6', '#a96b59', '#e76300', '#b9ac70', '#717581',
             '#92dadd']
TRAJ = '#3f90da'     # trajectories of the runs
FINAL = '#e42536'    # final threshold (after pruning)
NOMINAL = 'k'        # nominal threshold (dashed)


def set_style(plt, lumi=None, extra=None):
    if lumi is not None:
        CMS['lumi'] = lumi
    if extra is not None:
        CMS['extra'] = extra
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['TeX Gyre Heros', 'Helvetica', 'Arial', 'Liberation Sans', 'Nimbus Sans', 'DejaVu Sans'],
        'mathtext.default': 'regular',
        'font.size': 12, 'axes.labelsize': 14, 'xtick.labelsize': 12, 'ytick.labelsize': 12, 'legend.fontsize': 10,
        'legend.title_fontsize': 10, 'legend.frameon': False,
        'axes.linewidth': 1.2, 'axes.grid': False, 'axes.prop_cycle': plt.cycler(color=PETROFF10),
        'xaxis.labellocation': 'right', 'yaxis.labellocation': 'top',
        'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
        'xtick.minor.visible': True, 'ytick.minor.visible': True,
        'xtick.major.size': 8, 'ytick.major.size': 8, 'xtick.minor.size': 4, 'ytick.minor.size': 4,
        'xtick.major.width': 1.1, 'ytick.major.width': 1.1, 'xtick.minor.width': 1., 'ytick.minor.width': 1.,
    })


def cms_label(ax, ax_right=None, info=None, size=16, fig=None):
    """
    CMS label above the axes: 'CMS' (bold) and CMS['extra'] (italic) on the left of ax, the luminosity and energy on
    the right of ax_right (default: ax). info: optional text in between (centred in the figure if fig is given).
    """
    ax_right = ax if ax_right is None else ax_right
    t = ax.text(0., 1.015, 'CMS', transform=ax.transAxes, ha='left', va='baseline', fontsize=size, fontweight='bold')
    ax.annotate(f' {CMS["extra"]}', xy=(1., 0.), xycoords=t, ha='left', va='bottom', fontsize=0.8 * size,
                fontstyle='italic')
    right = f'({CMS["com"]:g} TeV)' if CMS['lumi'] is None else f'{CMS["lumi"]:.1f} fb$^{{-1}}$ ({CMS["com"]:g} TeV)'
    ax_right.text(1., 1.015, right, transform=ax_right.transAxes, ha='right', va='baseline', fontsize=0.8 * size)
    if info:
        tr = blended_transform_factory(fig.transFigure, ax.transAxes) if fig is not None else ax.transAxes
        # not part of the layout: it would count as part of ax and squeeze it in tight_layout
        ax.text(0.5, 1.015, info, transform=tr, ha='center', va='baseline', fontsize=0.7 * size).set_in_layout(False)


def _small(ax, size=9):
    # smaller fonts for the panels of the grid figures
    ax.tick_params(labelsize=size)
    ax.xaxis.label.set_size(size + 1)
    ax.yaxis.label.set_size(size + 1)


def _label(prob, j, tex2mpl):
    return tex2mpl(prob.cuts[j]['label'])


def _shade_off(ax, prob, j):
    # range of thresholds where a cut that is not applied in the nominal selection is "off"
    if prob.applied[j]:
        return
    lo, hi = (prob.t_lo[j], prob.off_edge[j]) if prob.sign[j] > 0 else (prob.off_edge[j], prob.t_hi[j])
    ax.axvspan(lo, hi, color='gray', alpha=0.15, label='cut not applied')


def _ref_line(ax, prob, j):
    if prob.applied[j]:
        ax.axvline(prob.t_ref[j], color=NOMINAL, linestyle='--', linewidth=1.4, label=f'nominal ({prob.t_ref[j]:g})')


def _final_line(ax, prob, j, t_final):
    lab = 'final: not applied' if prob.is_off(j, t_final[j]) else f'final ({t_final[j]:g})'
    ax.axvline(t_final[j], color=FINAL, linewidth=2., label=lab)


def plot_threshold_evolution(prob, T, t_final, outdir, plt, tex2mpl, region):
    """One figure per cut: trajectories of all the runs (top) and distribution of their final values (bottom)."""
    R, E1, J = T.shape
    epochs = np.arange(E1)
    for j in range(J):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 9), sharex=True, gridspec_kw=dict(height_ratios=[2.3, 1]))
        for r in range(R):
            ax1.plot(T[r, :, j], epochs, color=TRAJ, alpha=0.9 if r == 0 else 0.4, linewidth=2.2 if r == 0 else 1.,
                     label='run 0 (nominal start, no resampling)' if r == 0 else ('other runs' if r == 1 else None))
        _shade_off(ax1, prob, j)
        _ref_line(ax1, prob, j)
        _final_line(ax1, prob, j, t_final)
        ax1.invert_yaxis()
        ax1.set_ylabel('Epoch')
        ax1.legend(loc='lower right', title=f'{prob.names[j]}, region {region}, {R} runs', alignment='left')
        cms_label(ax1)

        final = T[:, -1, j]
        bins = np.arange(prob.t_lo[j] - 0.25 * prob.tau[j], prob.t_hi[j] + 0.5 * prob.tau[j], 0.5 * prob.tau[j])
        mu, sd = final.mean(), final.std(ddof=1) if R > 1 else 0.
        lab = (rf'final values: $\mu = \mathbf{{{mu:.3g}}} \pm {sd / np.sqrt(R):.2g}$, '
               rf'$\sigma = {sd:.2g} \pm {sd / np.sqrt(2 * max(R - 1, 1)):.2g}$')
        ax2.hist(final, bins=bins, color=TRAJ, alpha=0.6, edgecolor='k', label=lab)
        _shade_off(ax2, prob, j)
        _ref_line(ax2, prob, j)
        _final_line(ax2, prob, j, t_final)
        ax2.set_ylabel('Runs')
        ax2.set_xlabel(f'{_label(prob, j, tex2mpl)}  (cut: keep {prob.ops[j]} threshold)')
        ax2.set_ylim(0., 1.45 * ax2.get_ylim()[1])   # room for the legend
        ax2.legend(fontsize=9, loc='upper right')
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, f'threshold_evolution_{prob.names[j]}.png'), dpi=120)
        plt.close(fig)

    # overview: all the cuts in one figure
    ncol = 4
    nrow = int(np.ceil(J / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4 * ncol, 3.8 * nrow), squeeze=False)
    for j in range(J):
        ax = axes[j // ncol][j % ncol]
        for r in range(R):
            ax.plot(T[r, :, j], epochs, color=TRAJ, alpha=0.9 if r == 0 else 0.35, linewidth=1.6 if r == 0 else 0.8)
        _shade_off(ax, prob, j)
        _ref_line(ax, prob, j)
        _final_line(ax, prob, j, t_final)
        ax.invert_yaxis()
        ax.set_xlabel(_label(prob, j, tex2mpl))
        if j % ncol == 0:
            ax.set_ylabel('Epoch')
        _small(ax)
        ax.legend(fontsize=7, loc='lower right', title=prob.names[j], title_fontsize=8, alignment='left')
    for j in range(J, nrow * ncol):
        axes[j // ncol][j % ncol].axis('off')
    cms_label(axes[0][0], axes[0][ncol - 1], info=f'Threshold evolution, region {region}, {R} runs', size=14, fig=fig)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, 'threshold_evolution_all.png'), dpi=110)
    plt.close(fig)


def plot_training_history(hist, z_nom_test, cfg, outdir, plt, region):
    """Significance vs epoch (soft on train, hard on train and test) and the effective MC statistics."""
    zsoft, ev = hist['zsoft'], hist['eval_epochs']
    R, E = zsoft.shape
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 9), sharex=True, gridspec_kw=dict(height_ratios=[2, 1]))
    for key, color, lab, xs in (('zsoft', 'C0', 'soft Z (train)', np.arange(E)),
                                ('zhard_train', 'C1', 'hard-cut Z (train)', ev),
                                ('zhard_test', 'C2', 'hard-cut Z (test)', ev)):
        for r in range(R):
            ax1.plot(xs, hist[key][r], color=color, alpha=0.15, linewidth=0.8)
        ax1.plot(xs, np.median(hist[key], axis=0), color=color, linewidth=2.2, label=f'{lab}, median of runs')
    ax1.axhline(z_nom_test, color=NOMINAL, linestyle='--',
                label=f'nominal selection, hard-cut Z (test) = {z_nom_test:.3f}')
    ax1.set_ylabel(f'Significance ({cfg["objective"]})')
    ax1.legend(loc='lower right', title=f'Region {region}, {R} runs', alignment='left')
    ax1.tick_params(which='both', right=False)
    ax1r = ax1.twinx()
    ax1r.plot(np.arange(E), hist['k'][0], color='gray', linestyle=':', linewidth=1.5)
    ax1r.set_ylabel('Sharpness k (gray dotted)', color='gray')
    ax1r.tick_params(axis='y', which='both', colors='gray', direction='in')
    ax1r.minorticks_on()
    cms_label(ax1)

    for r in range(R):
        ax2.plot(np.arange(E), hist['neff'][r], color='C4', alpha=0.25, linewidth=0.8)
    ax2.plot(np.arange(E), np.median(hist['neff'], axis=0), color='C4', linewidth=2,
             label='effective MC background events (soft, train), median')
    if cfg['min_neff'] > 0:
        ax2.axhline(cfg['min_neff'], color=FINAL, linestyle='--', label=f'min-neff = {cfg["min_neff"]:g}')
    ax2.set_yscale('log')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel(r'$N_{eff}(B)$')
    ax2.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, 'training_history.png'), dpi=120)
    plt.close(fig)


def plot_soft_vs_hard(prob, cfg, outdir, plt, tex2mpl, cut_name='pt3'):
    """Soft cut for several k (as SoftQuant.png of smart-pixels-ml) and the k and learning-rate schedules."""
    j = prob.names.index(cut_name) if cut_name in prob.names else 0
    t = prob.t_ref[j] if prob.applied[j] else 0.5 * (prob.scan_lo[j] + prob.scan_hi[j])
    lo, hi = prob.cuts[j]['hrange'][:2]
    x = np.linspace(lo, hi, 2000)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    hard = (prob.sign[j] * (x - t) > 0).astype(float)
    ax1.plot(x, hard, color='k', linewidth=2.5, label='hard cut')
    ks = sorted(set([cfg['k_start'], 2., 10., cfg['k_end']]))
    for i, k in enumerate(ks):
        p = 0.5 * (1. + np.tanh(0.5 * k * prob.sign[j] * (x - t) / prob.tau[j]))   # sigmoid, no overflow
        ax1.plot(x, p, color=f'C{i}', linewidth=1.8, label=f'soft cut, k = {k:g}')
    ax1.axvline(t, color='gray', linestyle=':', label=f'threshold ({t:g})')
    ax1.set_xlim(max(lo, t - 12 * prob.tau[j]), min(hi, t + 12 * prob.tau[j]))
    ax1.set_ylim(-0.02, 1.35)   # room for the legend
    ax1.set_xlabel(_label(prob, j, tex2mpl))
    ax1.set_ylabel('Event weight factor p')
    ax1.legend(loc='upper left', ncol=2, title=f'{prob.names[j]} {prob.ops[j]} {t:g}, scale tau = {prob.tau[j]:g}',
               alignment='left')

    E = cfg['epochs']
    ep = np.arange(E)
    ax2.plot(ep, [k_schedule(e, E, cfg['k_start'], cfg['k_end'], cfg['k_schedule']) for e in ep], color='C0',
             label=f'sharpness k ({cfg["k_schedule"]})')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('k', color='C0')
    ax2.tick_params(which='both', right=False)
    ax2r = ax2.twinx()
    ax2r.plot(ep, [lr_schedule(e, E, cfg['lr']) for e in ep], color='C1', label='learning rate')
    ax2r.set_ylabel('Learning rate [scan steps / epoch]', color='C1')
    ax2r.tick_params(axis='y', which='both', direction='in')
    ax2r.minorticks_on()
    h1, l1 = ax2.get_legend_handles_labels()
    h2, l2 = ax2r.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, loc='center right', title='Annealing and learning rate', alignment='left')
    cms_label(ax1, ax2r)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, 'soft_vs_hard_cut.png'), dpi=120)
    plt.close(fig)


def plot_pruning(steps, min_gain, n_sigma, outdir, plt, region):
    """Gain of each threshold change (first pruning iteration) and the decision."""
    fig, ax = plt.subplots(figsize=(9, 2.4 + 0.5 * max(len(steps[0]['cuts']) if steps else 1, 1)))
    if not steps:
        ax.text(0.5, 0.5, 'no threshold changed w.r.t. nominal: nothing to prune', ha='center', va='center')
        ax.axis('off')
    else:
        s0 = steps[0]
        reverted = {s['reverted'] for s in steps if s['reverted']}
        kept_color, reverted_color = 'C0', 'C3'
        y = np.arange(len(s0['cuts']))
        rel = 100. * np.array(s0['dZ']) / s0['Z']
        err = 100. * n_sigma * np.array(s0['dZ_err']) / s0['Z']
        colors = [reverted_color if c in reverted else kept_color for c in s0['cuts']]
        ax.barh(y, rel, xerr=err, color=colors, alpha=0.85, edgecolor='k', capsize=3)
        ax.set_yticks(y)
        ax.set_yticklabels([f'{c} ({t:g})' for c, t in zip(s0['cuts'], s0['thresholds'])])
        ax.tick_params(axis='y', which='minor', left=False, right=False)
        ax.set_ylim(-0.7, len(y) + 0.8)   # room for the legend
        ax.axvline(100. * min_gain, color='k', linestyle='--', label=f'min gain = {100. * min_gain:g}% of Z')
        ax.axvline(0., color='gray', linewidth=0.8)
        ax.bar([0], [0], color=kept_color, label='kept')
        ax.bar([0], [0], color=reverted_color, label='reverted to nominal')
        ax.set_xlabel(f'dZ / Z [%] when the cut is put back to nominal (test, {n_sigma:g}σ bootstrap errors)')
        ax.legend(loc='upper right', ncol=3,
                  title=f'Pruning, region {region}: Z(best run, test) = {s0["Z"]:.3f} ± {s0["Z_err"]:.3f}')
        cms_label(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, 'pruning.png'), dpi=120)
    plt.close(fig)


def plot_run_summary(hist, z_test, best_run, outdir, plt, region):
    """Final hard-cut Z on the test sample of every run, compared to nominal, best run and final."""
    zt = hist['zhard_test'][:, -1]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(np.arange(len(zt)), zt, 'o', color='C0', label='run: final thresholds (not rounded)')
    ax.plot([best_run], [zt[best_run]], 'o', color='C1', markersize=12, markerfacecolor='none', markeredgewidth=2,
            label=f'best run on the training sample (run {best_run})')
    for key, color, lab in (('nominal', NOMINAL, 'nominal'), ('best_run', 'C1', 'best run, rounded'),
                            ('final', FINAL, 'final (after pruning)')):
        z, e = z_test[key]
        ax.axhline(z, color=color, linestyle='--' if key == 'nominal' else '-', label=f'{lab}: {z:.3f} ± {e:.3f}')
        ax.axhspan(z - e, z + e, color=color, alpha=0.1)
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi + 0.6 * (hi - lo))   # room for the legend
    ax.set_xlabel('Run')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis='x', which='minor', bottom=False, top=False)
    ax.set_ylabel('Hard-cut Z (test)')
    ax.legend(loc='upper left', ncol=2, alignment='left',
              title=f'Region {region}, test sample (bands: bootstrap stat. uncertainty)')
    cms_label(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, 'run_summary.png'), dpi=120)
    plt.close(fig)


def _nminus1_frame(axes, prob, t, signal_scale, tex2mpl, t_final=None):
    theta = prob.theta_of(t)
    passes = prob.V > theta
    for j, ax in enumerate(axes):
        # clear the panel but keep the CMS label (texts of the first row are added once, outside the frames)
        for artist in list(ax.lines) + list(ax.patches) + list(ax.collections):
            artist.remove()
        if ax.get_legend():
            ax.get_legend().remove()
        m = np.delete(passes, j, axis=1).all(axis=1)
        lo, hi, nb = prob.cuts[j]['hrange']
        x = np.clip(prob.X_raw[:, j], lo, hi - 1e-9 * (hi - lo))   # overflow in the last bin
        b, edges = np.histogram(x[m & ~prob.sig], bins=nb, range=(lo, hi), weights=prob.w[m & ~prob.sig])
        s, _ = np.histogram(x[m & prob.sig], bins=nb, range=(lo, hi), weights=prob.w[m & prob.sig])
        ax.stairs(b, edges, fill=True, color='C1', alpha=0.6, label='background')
        ax.stairs(signal_scale * s, edges, color='C0', linewidth=1.8, label=f'signal x {signal_scale:g}')
        if prob.applied[j]:
            ax.axvline(prob.t_ref[j], color=NOMINAL, linestyle='--', linewidth=1.2, label='nominal')
        if not prob.is_off(j, t[j]):
            ax.axvline(t[j], color=FINAL, linewidth=1.8, label=f'threshold ({t[j]:.3g})')
        if t_final is not None and not prob.is_off(j, t_final[j]):
            ax.axvline(t_final[j], color=FINAL, linewidth=1.8)
        ax.relim()
        ax.autoscale_view()
        ax.set_ylim(0., 1.5 * max(b.max(), signal_scale * s.max(), 1e-9))   # room for the legend
        ax.set_xlabel(_label(prob, j, tex2mpl))
        ax.set_ylabel('Events / bin')
        _small(ax, 8)
        ax.legend(fontsize=6, title=prob.describe(j, t[j]) if prob.is_off(j, t[j]) else prob.names[j],
                  title_fontsize=7, alignment='left')


def plot_nminus1_final(prob, t_final, signal_scale, outdir, plt, tex2mpl, region):
    """N-1 distributions (all events, all the other cuts at their final values)."""
    J = len(prob.names)
    ncol = 4
    nrow = int(np.ceil(J / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4 * ncol, 3.6 * nrow), squeeze=False)
    _nminus1_frame([axes[j // ncol][j % ncol] for j in range(J)], prob, t_final, signal_scale, tex2mpl)
    for j in range(J, nrow * ncol):
        axes[j // ncol][j % ncol].axis('off')
    cms_label(axes[0][0], axes[0][ncol - 1], info=f'N-1 distributions at the final thresholds, region {region}',
              size=14, fig=fig)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, 'nminus1_final.png'), dpi=110)
    plt.close(fig)


def make_gif(prob, T_run, hist, run, signal_scale, outdir, plt, tex2mpl, region, n_frames=50, fps=8):
    """Animated N-1 distributions while the thresholds of one run move during the training."""
    from matplotlib import animation
    J = len(prob.names)
    E = T_run.shape[0] - 1
    frames = np.unique(np.linspace(0, E, n_frames).astype(int))
    ncol = 4
    nrow = int(np.ceil(J / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4 * ncol, 3.4 * nrow + 0.4), squeeze=False)
    for j in range(J, nrow * ncol):
        axes[j // ncol][j % ncol].axis('off')
    axs = [axes[j // ncol][j % ncol] for j in range(J)]
    ev = list(hist['eval_epochs'])
    cms_label(axes[0][0], axes[0][ncol - 1], size=14)
    info = fig.text(0.5, 0.975, '', ha='center', va='top', fontsize=11)

    def draw(i):
        ep = frames[i]
        k = hist['k'][run][min(ep, E - 1)]
        ie = int(np.searchsorted(ev, ep, side='right')) - 1
        _nminus1_frame(axs, prob, T_run[ep], signal_scale, tex2mpl)
        info.set_text(f'Region {region}, run {run}: epoch {ep}/{E}, k = {k:.2f}, hard-cut Z train = '
                      f'{hist["zhard_train"][run][ie]:.3f}, test = {hist["zhard_test"][run][ie]:.3f}')
        return axs

    # fixed spacing (tight_layout is computed before the frames are drawn, so it cannot be used here)
    fig.subplots_adjust(left=0.05, right=0.99, bottom=0.07, top=0.9, hspace=0.45, wspace=0.3)
    ani = animation.FuncAnimation(fig, draw, frames=len(frames), blit=False)
    path = os.path.join(outdir, f'nminus1_evolution_run{run}.gif')
    ani.save(path, writer='pillow', fps=fps)
    plt.close(fig)
    return path
