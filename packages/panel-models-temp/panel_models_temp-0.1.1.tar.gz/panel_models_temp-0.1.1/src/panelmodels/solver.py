import numpy as np

def _soft_threshold(x, lam):
    if x > lam: return x - lam
    if x < -lam: return x + lam
    return 0.0

def fit_poisson_fe_lasso_normalized(
    X, y, group_ids,
    lambda_norm=1.0,        # user-scale penalty; ~1 starts zeroing coefs
    l2=0.0,                 # optional ridge on beta
    beta0=None,
    max_outer=50,
    max_inner=100,
    tol=1e-6,
    inner_tol=1e-8,
    eps=1e-12,
    verbose=False
):
    """
    Poisson FE (alphas absorbed exactly) + L1 on beta with a normalized lambda.
    We calibrate lambda so that lambda_norm=1 corresponds to lambda_max at beta=0
    in the first IRLS subproblem using weighted, FE-demeaned features.

    Returns: beta (p,), alpha (m,), info dict
    """
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    g = np.asarray(group_ids, dtype=np.int64)
    n, p = X.shape
    m = int(g.max()) + 1

    # Sufficient stats for alpha profile
    T = np.bincount(g, weights=y, minlength=m)

    # Start at beta=0 unless provided
    beta_std = np.zeros(p) if beta0 is None else beta0.astype(np.float64).copy()
    s = np.ones(p, dtype=np.float64)  # column scales for standardization (filled after calibration)
    lambda_calibrated = None          # actual lambda used in CD after calibration

    def profile_alpha(beta):
        eta0 = X @ (beta / s)  # because beta stored in "std" space
        S = np.bincount(g, weights=np.exp(eta0), minlength=m)
        alpha = np.log(np.maximum(T, eps)) - np.log(np.maximum(S, eps))
        return alpha, eta0

    # --- One-time calibration at beta=0 to define s and lambda_max ---
    beta_std[:] = 0.0
    alpha, eta0 = profile_alpha(beta_std)
    eta = eta0 + alpha[g]
    mu = np.exp(eta)
    W = mu
    z = eta + (y - mu) / np.maximum(mu, eps)

    # weighted FE demeaning
    Wg = np.maximum(np.bincount(g, weights=W, minlength=m), eps)
    Xw = X * W[:, None]
    Xgw = np.vstack([np.bincount(g, weights=Xw[:, j], minlength=m) for j in range(p)]).T
    zg  = np.bincount(g, weights=W * z, minlength=m)
    X_tilde = X - Xgw[g] / Wg[g, None]
    z_tilde = z - zg[g] / Wg[g]

    # column scales: s_j = sqrt(sum W * X_tilde_j^2); guard with eps
    for j in range(p):
        s[j] = np.sqrt((W * X_tilde[:, j] * X_tilde[:, j]).sum()) + 1e-12

    # standardized correlation at beta=0 → lambda_max
    rho0 = np.empty(p)
    for j in range(p):
        xj_std = X_tilde[:, j] / s[j]
        rho0[j] = (W * xj_std * z_tilde).sum()
    lambda_max = np.max(np.abs(rho0))
    lambda_calibrated = lambda_norm * lambda_max

    if verbose:
        print(f"lambda_max={lambda_max:.6g}  lambda_used={lambda_calibrated:.6g}")

    # ---- Outer IRLS loop ----
    for it in range(max_outer):
        # Profile alphas given current beta
        alpha, eta0 = profile_alpha(beta_std)
        eta = eta0 + alpha[g]
        mu = np.exp(eta)

        # IRLS weights/pseudo-response
        W = mu
        z = eta + (y - mu) / np.maximum(mu, eps)

        # Weighted FE demeaning for current W, z
        Wg = np.maximum(np.bincount(g, weights=W, minlength=m), eps)
        Xw = X * W[:, None]
        Xgw = np.vstack([np.bincount(g, weights=Xw[:, j], minlength=m) for j in range(p)]).T
        zg  = np.bincount(g, weights=W * z, minlength=m)
        X_tilde = X - Xgw[g] / Wg[g, None]
        z_tilde = z - zg[g] / Wg[g]

        # Work in standardized coordinates: X_std = X_tilde / s
        # Keep residual r_std = z_tilde - sum_j X_std_j * beta_std_j
        Xbeta_std = np.zeros(n)
        for j in range(p):
            Xbeta_std += (X_tilde[:, j] / s[j]) * beta_std[j]
        r_std = z_tilde - Xbeta_std

        # Per-feature curvature in std space: a_j = sum W * (X_tilde_j/s_j)^2 + l2 (on *unscaled* beta)
        # Ridge on original beta translates to l2 / s_j^2 on beta_std
        a = np.empty(p, dtype=np.float64)
        l2_std = l2 / (s * s)
        for j in range(p):
            xj_std = X_tilde[:, j] / s[j]
            a[j] = (W * xj_std * xj_std).sum() + l2_std[j]

        # Coordinate descent with soft-thresholding in std space
        for inner in range(max_inner):
            max_delta = 0.0
            for j in range(p):
                xj_std = X_tilde[:, j] / s[j]
                bj_old = beta_std[j]
                # rho_j = sum W * xj_std * (r_std + xj_std * bj_old)
                rho = (W * xj_std * (r_std + xj_std * bj_old)).sum()
                # soft-threshold
                bj_new = _soft_threshold(rho, lambda_calibrated) / a[j]
                if bj_new != bj_old:
                    delta = bj_new - bj_old
                    r_std -= xj_std * delta
                    beta_std[j] = bj_new
                    if abs(delta) > max_delta:
                        max_delta = abs(delta)
            if max_delta < inner_tol * (1.0 + np.linalg.norm(beta_std, ord=np.inf)):
                break

        # Convergence test on linear predictor change
        eta0_new = X @ (beta_std / s)
        if np.linalg.norm(eta0_new - eta0) < tol * (1.0 + np.linalg.norm(eta0)):
            break

    # Map back to original scale
    beta = beta_std / s
    # Final alpha on that beta
    eta0 = X @ beta
    S = np.bincount(g, weights=np.exp(eta0), minlength=m)
    alpha = np.log(np.maximum(T, eps)) - np.log(np.maximum(S, eps))

    info = {
        "outer_iters": it + 1,
        "lambda_norm": float(lambda_norm),
        "lambda_max": float(lambda_max),
        "lambda_used": float(lambda_calibrated),
        "l2": float(l2),
        "scales": s,
    }
    return beta, alpha, info
