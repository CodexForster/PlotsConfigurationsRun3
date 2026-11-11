"""
Soft (sigmoid) cuts with trainable thresholds, used by optimize_thresholds.py.

Coordinates
-----------
Each trainable cut j is 'keep if x > t' or 'keep if x < t'. With s_j = +1 ('>') or -1 ('<') and the scale tau_j
(the step of the cut_scan scan of that variable), the cut is written in normalized, signed coordinates

    v_ij = s_j * x_ij / tau_j,   theta_j = s_j * t_j / tau_j,   keep event i if v_ij > theta_j for all j,

so every cut is a '>' cut and one unit of theta is one scan step of that variable (1 GeV for pT3, 0.2 for dphi, ...).

Soft cut
--------
    p_ij = sigmoid(k * (v_ij - theta_j)),   P_i = prod_j p_ij,   S = sum_{i in sig} w_i P_i,   B = sum_{i in bkg} w_i P_i

k is the sharpness: k -> infinity gives back the hard cut. d log p_ij / d theta_j = -k * (1 - p_ij), so the
gradients of S and B with respect to all the thresholds are computed analytically (no autodiff library needed).
"""

import numpy as np

# Cuts not applied in the nominal selection (nominal=None in cut_scan) are skipped by Problem, so this and the rest of
# the "off" handling (applied = False, off_edge) are not used at the moment. Without the skipping, the threshold of such
# a cut could move up to OFF_MARGIN scan steps beyond the loose end of the scan, where the cut is "not applied". Kept
# small, so that a cut starting "off" is still close enough to the events to feel a gradient.
OFF_MARGIN = 3.


###############################################################################
# Events and cut definitions of one region
###############################################################################

class Problem:
    """Events of one region (all MC samples, fixed cuts applied) and the trainable cuts."""

    def __init__(self, data, signal, cuts, pass_cut, freeze=()):
        # cuts not applied in the nominal selection (nominal=None in cut_scan: met, mjj_window) are skipped: not trained
        # and not applied. Once such a cut gets a nominal value in cut_scan, it is trained like the others.
        self.skipped = [c for c in cuts if c['op'] != 'fixed' and c['nominal'] is None]
        cuts = [c for c in cuts if c not in self.skipped]
        self.cuts = [c for c in cuts if c['op'] != 'fixed' and c['name'] not in freeze]
        # fixed cuts (b veto, njet) and frozen cuts are applied once, as hard cuts at their nominal values
        self.fixed = [c for c in cuts if c not in self.cuts]
        self.names = [c['name'] for c in self.cuts]
        self.ops = [c['op'] for c in self.cuts]
        J = len(self.cuts)
        self.sign = np.array([1. if c['op'] == '>' else -1. for c in self.cuts])
        self.tau = np.array([float(np.min(np.diff(np.sort(c['scan'])))) for c in self.cuts])
        self.scan_lo = np.array([float(np.min(c['scan'])) for c in self.cuts])
        self.scan_hi = np.array([float(np.max(c['scan'])) for c in self.cuts])
        self.applied = np.array([c['nominal'] is not None for c in self.cuts])

        # Threshold range: the cut_scan scan range. For the cuts that are not applied in the nominal selection (none at
        # the moment, they are skipped above), it is extended by OFF_MARGIN steps on the loose side, and the variable is
        # clipped one step beyond the loose end of the scan (off_edge), so that any threshold beyond off_edge keeps all
        # the events ("not applied"). The reference threshold t_ref (nominal selection) is then the end of the extended
        # range.
        self.t_lo, self.t_hi = self.scan_lo.copy(), self.scan_hi.copy()
        clip_lo, clip_hi = np.full(J, -np.inf), np.full(J, np.inf)
        self.t_ref, self.off_edge = np.zeros(J), np.full(J, np.nan)
        for j, c in enumerate(self.cuts):
            if self.applied[j]:
                self.t_ref[j] = c['nominal']
            elif self.sign[j] > 0:
                self.t_lo[j] = self.scan_lo[j] - OFF_MARGIN * self.tau[j]
                clip_lo[j] = self.off_edge[j] = self.scan_lo[j] - self.tau[j]
                self.t_ref[j] = self.t_lo[j]
            else:
                self.t_hi[j] = self.scan_hi[j] + OFF_MARGIN * self.tau[j]
                clip_hi[j] = self.off_edge[j] = self.scan_hi[j] + self.tau[j]
                self.t_ref[j] = self.t_hi[j]
        th_a, th_b = self.theta_of(self.t_lo), self.theta_of(self.t_hi)
        self.theta_lo, self.theta_hi = np.minimum(th_a, th_b), np.maximum(th_a, th_b)
        self.theta_ref = self.theta_of(self.t_ref)

        X, w, sig, proc = [], [], [], []
        self.proc_names = list(data.keys())
        for ip, (p, arr) in enumerate(data.items()):
            m = np.ones(len(arr['w']), dtype=bool)
        # Trainable cuts are never applied to the events inside Problem. The only filter in the following line removes events that would fail a cut even at its loosest allowed value. So V holds every event that could pass under any thresholds the optimizer might choose. Nothing there depends on the default thresholds except the fixed and frozen cuts.
            for c in self.fixed:
                m &= pass_cut(arr, c)
            X.append(np.column_stack([arr[f'cv_{n}'][m] for n in self.names]) if J else np.zeros((m.sum(), 0)))
            w.append(arr['w'][m])
            sig.append(np.full(m.sum(), p in signal))
            proc.append(np.full(m.sum(), ip))
        X_raw = np.concatenate(X)
        V = self.sign * np.clip(X_raw, clip_lo, clip_hi) / self.tau
        # events failing a cut at its loosest threshold can never pass: dropped
        keep = (V > self.theta_lo).all(axis=1)
        self.X_raw, self.V = X_raw[keep], V[keep]
        self.w, self.sig, self.proc = np.concatenate(w)[keep], np.concatenate(sig)[keep], np.concatenate(proc)[keep]

    def theta_of(self, t):
        return self.sign * np.asarray(t, dtype=float) / self.tau

    def t_of(self, theta):
        return self.sign * np.asarray(theta, dtype=float) * self.tau

    def is_off(self, j, t):
        # a cut that is not applied in the nominal selection is "off" beyond off_edge (all the events pass)
        if self.applied[j]:
            return False
        return t < self.off_edge[j] if self.sign[j] > 0 else t > self.off_edge[j]

    def is_ref(self, j, t):
        return self.is_off(j, t) if not self.applied[j] else abs(t - self.t_ref[j]) < 1e-9

    def round_threshold(self, j, t):
        """Threshold rounded to the cut_scan grid; snapped to nominal if within half a step of it."""
        if not self.applied[j] and self.is_off(j, t):
            return float(self.t_ref[j])
        if self.applied[j] and abs(t - self.t_ref[j]) < 0.5 * self.tau[j]:
            return float(self.t_ref[j])
        r = self.scan_lo[j] + self.tau[j] * np.round((t - self.scan_lo[j]) / self.tau[j])
        return float(np.round(np.clip(r, self.scan_lo[j], self.scan_hi[j]), 6))

    def describe(self, j, t):
        if self.is_off(j, t):
            return f'{self.names[j]}: not applied'
        return f'{self.names[j]} {self.ops[j]} {t:g}'


###############################################################################
# Significance and its derivatives
###############################################################################

def significance(S, B, objective):
    """Z and its derivatives dZ/dS, dZ/dB (scalars)."""
    if S <= 0 or B <= 0:
        return 0., 0., 0.
    if objective == 'asimov':
        # Z_A = sqrt(2 [(S + B) ln(1 + S/B) - S]),  dZ/dS = ln(1 + S/B) / Z,  dZ/dB = (ln(1 + S/B) - S/B) / Z
        r = S / B
        l = np.log1p(r)
        f = (S + B) * l - S
        if f <= 0:
            return 0., 0., 0.
        Z = np.sqrt(2. * f)
        return Z, l / Z, (l - r) / Z
    # S / sqrt(B)
    Z = S / np.sqrt(B)
    return Z, 1. / np.sqrt(B), -0.5 * Z / B


def significance_array(S, B, objective):
    """Z for arrays of yields (hard cuts, bootstrap)."""
    S, B = np.broadcast_arrays(np.asarray(S, dtype=float), np.asarray(B, dtype=float))
    Z = np.zeros(S.shape)
    ok = (S > 0) & (B > 0)
    if objective == 'asimov':
        f = (S[ok] + B[ok]) * np.log1p(S[ok] / B[ok]) - S[ok]
        Z[ok] = np.sqrt(2. * np.maximum(f, 0.))
    else:
        Z[ok] = S[ok] / np.sqrt(B[ok])
    return Z


def hard_yields(V, w, sig, theta):
    m = (V > theta).all(axis=1)
    return w[m & sig].sum(), w[m & ~sig].sum()


def hard_significance(V, w, sig, theta, objective):
    S, B = hard_yields(V, w, sig, theta)
    return float(significance_array(S, B, objective))


###############################################################################
# Soft yields and gradients
###############################################################################

def soft_terms(V, w, theta, k):
    """Soft per-event weights a_i = w_i P_i, the matrix q_ij = 1 - p_ij, the yield and its gradient."""
    z = k * (V - theta)
    P = np.exp(-np.logaddexp(0., -z).sum(axis=1))   # prod_j sigmoid(z_ij)
    q = np.exp(-np.logaddexp(0., z))                # 1 - sigmoid(z_ij)
    a = w * P
    return a, q, a.sum(), -k * (a @ q)


###############################################################################
# Schedules and optimizer
###############################################################################

def k_schedule(epoch, n_epochs, k0, k1, kind):
    """Sharpness k at a given epoch: from k0 (soft) to k1 (almost hard), as in AnnealingScheduler of smart-pixels-ml."""
    r = epoch / max(n_epochs - 1, 1)
    if kind == 'linear':
        return k0 + (k1 - k0) * r
    if kind == 'cosine':
        return k0 + (k1 - k0) * 0.5 * (1. - np.cos(np.pi * r))
    if kind == 'exponential':
        return k0 * (k1 / k0) ** r
    raise ValueError(f'unknown k schedule {kind}')


def lr_schedule(epoch, n_epochs, lr):
    # cosine decay of the learning rate down to lr / 10, so that the thresholds settle at the end
    r = epoch / max(n_epochs - 1, 1)
    return lr * (0.1 + 0.9 * 0.5 * (1. + np.cos(np.pi * r)))


class Adam:
    def __init__(self, n, beta1=0.9, beta2=0.999, eps=1e-8):
        self.m, self.v = np.zeros(n), np.zeros(n)
        self.b1, self.b2, self.eps, self.t = beta1, beta2, eps, 0

    def step(self, grad, lr):
        self.t += 1
        self.m = self.b1 * self.m + (1. - self.b1) * grad
        self.v = self.b2 * self.v + (1. - self.b2) * grad ** 2
        mhat = self.m / (1. - self.b1 ** self.t)
        vhat = self.v / (1. - self.b2 ** self.t)
        return lr * mhat / (np.sqrt(vhat) + self.eps)


###############################################################################
# Training of one run
###############################################################################

def train_run(Vs, ws, Vb, wb, theta0, theta_ref, theta_lo, theta_hi, cfg, z0, evals):
    """
    Train all the thresholds simultaneously.

    Vs, ws / Vb, wb: signal / background events of the training sample. z0: hard significance of the nominal
    selection on the training sample (normalization of the loss). evals: {name: (V, w, sig)} samples on which the
    hard-cut significance is evaluated every cfg['eval_every'] epochs.

    Loss = -Z_soft / z0 + lam * sum_j |theta_j - theta_ref_j| + mu * max(0, 1 - Neff_B / Nmin)^2
    """
    E, J = cfg['epochs'], len(theta0)
    theta = theta0.copy()
    opt = Adam(J)
    hist = dict(theta=np.zeros((E + 1, J)), zsoft=np.zeros(E), loss=np.zeros(E), neff=np.zeros(E), k=np.zeros(E))
    eval_epochs = sorted(set(list(range(0, E, cfg['eval_every'])) + [E]))
    hard = {name: [] for name in evals}
    hist['theta'][0] = theta
    for ep in range(E + 1):
        if ep in eval_epochs:
            for name, (V, w, sig) in evals.items():
                hard[name].append(hard_significance(V, w, sig, theta, cfg['objective']))
        if ep == E:
            break
        k = k_schedule(ep, E, cfg['k_start'], cfg['k_end'], cfg['k_schedule'])
        _, _, S, dS = soft_terms(Vs, ws, theta, k)
        ab, qb, B, dB = soft_terms(Vb, wb, theta, k)
        Z, zS, zB = significance(S, max(B, 1e-9), cfg['objective'])
        grad = -(zS * dS + zB * dB) / z0
        loss = -Z / z0

        # MC statistics guard: Kish effective number of background events Neff = (sum a)^2 / sum a^2
        A, C = max(B, 0.), (ab * ab).sum()
        neff = A * A / C if C > 0 else 0.
        if cfg['min_neff'] > 0 and neff < cfg['min_neff'] and C > 0:
            dC = -2. * k * ((ab * ab) @ qb)
            dneff = (2. * A * dB * C - A * A * dC) / C ** 2
            d = 1. - neff / cfg['min_neff']
            loss += cfg['neff_weight'] * d * d
            grad += cfg['neff_weight'] * 2. * d * (-dneff / cfg['min_neff'])

        # L1 pull to the nominal threshold: a threshold moves only if the gain in Z pays for it
        loss += cfg['lam'] * np.abs(theta - theta_ref).sum()
        grad += cfg['lam'] * np.sign(theta - theta_ref)

        theta = np.clip(theta - opt.step(grad, lr_schedule(ep, E, cfg['lr'])), theta_lo, theta_hi)
        hist['theta'][ep + 1] = theta
        hist['zsoft'][ep], hist['loss'][ep], hist['neff'][ep], hist['k'][ep] = Z, loss, neff, k
    hist['eval_epochs'] = np.array(eval_epochs)
    for name in evals:
        hist[f'zhard_{name}'] = np.array(hard[name])
    return hist
