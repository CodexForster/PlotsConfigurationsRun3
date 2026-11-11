"""
Validation of the trained thresholds, used by optimize_thresholds.py: selection of the best run, bootstrap uncertainty
of the hard-cut significance, and pruning of the threshold changes with too little gain.
"""

import numpy as np

from softcuts import significance_array


def round_all(prob, t):
    """Thresholds rounded to the cut_scan grid (snapped to nominal if within half a step, 'off' kept off)."""
    return np.array([prob.round_threshold(j, t[j]) for j in range(len(prob.names))])


def select_best(prob, t_final_runs, V, w, sig, objective):
    """
    Best run: the one whose final thresholds, rounded, give the highest hard-cut significance on the training sample
    (all the training events, not resampled). The test sample is not used, so it stays independent for the pruning
    and the final numbers. (The median of the runs is not used: when the runs end in different optima, e.g. a cut
    tightened in some runs and left off in others, the median is a mixture of them that is in none of the optima.)
    Returns the rounded thresholds of the best run, its index and the training Z of every run.
    """
    rounded = [round_all(prob, t) for t in t_final_runs]
    z = np.array([evaluate(V, w, sig, prob.theta_of(t), objective)['Z'] for t in rounded])
    best = int(np.argmax(z))
    return rounded[best], best, z


def bootstrap_significance(V, w, sig, thetas, n_boot, seed, objective, chunk=20):
    """
    Hard-cut significance of several selections (one theta each) on n_boot bootstrap replicas of the sample.
    Each replica gives every event a Poisson(1) multiplicity. The same replicas (same seed) are used for all the
    selections, so differences between selections have the correct (correlated) uncertainty.
    Returns an array (n_boot, len(thetas)).
    """
    M = np.stack([(V > th).all(axis=1) for th in thetas]).astype(np.float64).T   # (N, n_sel)
    ws, wb = np.where(sig, w, 0.), np.where(sig, 0., w)
    rng = np.random.default_rng(seed)
    Z = []
    for start in range(0, n_boot, chunk):
        R = rng.poisson(1., size=(min(chunk, n_boot - start), len(w)))
        Z.append(significance_array((R * ws) @ M, (R * wb) @ M, objective))
    return np.concatenate(Z)


def evaluate(V, w, sig, theta, objective):
    m = (V > theta).all(axis=1)
    S, B = w[m & sig].sum(), w[m & ~sig].sum()
    return dict(S=S, B=B, S_over_B=S / B if B > 0 else 0., S_over_sqrtB=S / np.sqrt(B) if B > 0 else 0.,
                Z=float(significance_array(S, B, objective)))


def prune(prob, V, w, sig, t_start, min_gain, n_sigma, n_boot, seed, objective):
    """
    Backward elimination of the threshold changes, on the test sample (hard cuts).
    At each iteration, every changed cut j is put back to nominal (the others stay as they are) and
        dZ_j = Z(current) - Z(current with cut j at nominal)
    is computed, with its bootstrap uncertainty sigma_j. A change is worth keeping if
        dZ_j >= max(min_gain * Z(current), n_sigma * sigma_j).
    If some changes fail, the one with the smallest dZ_j is reverted and the procedure is repeated; otherwise it stops.
    Returns the final thresholds and the list of iterations.
    """
    t = np.array(t_start, dtype=float)
    steps = []
    while True:
        changed = [j for j in range(len(t)) if not prob.is_ref(j, t[j])]
        if not changed:
            break
        selections = [t]
        for j in changed:
            tj = t.copy()
            tj[j] = prob.t_ref[j]
            selections.append(tj)
        thetas = [prob.theta_of(s) for s in selections]
        z = np.array([evaluate(V, w, sig, th, objective)['Z'] for th in thetas])
        zb = bootstrap_significance(V, w, sig, thetas, n_boot, seed, objective)
        dz = z[0] - z[1:]
        dz_err = (zb[:, :1] - zb[:, 1:]).std(axis=0)
        required = np.maximum(min_gain * z[0], n_sigma * dz_err)
        step = dict(Z=float(z[0]), Z_err=float(zb[:, 0].std()), cuts=[prob.names[j] for j in changed],
                    thresholds=[float(t[j]) for j in changed], dZ=dz.tolist(), dZ_err=dz_err.tolist(),
                    required=required.tolist(), reverted=None)
        failing = [i for i in range(len(changed)) if dz[i] < required[i]]
        steps.append(step)
        if not failing:
            break
        i = min(failing, key=lambda i: dz[i])
        step['reverted'] = prob.names[changed[i]]
        t[changed[i]] = prob.t_ref[changed[i]]
    return t, steps
