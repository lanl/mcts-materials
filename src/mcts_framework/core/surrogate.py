"""
Gaussian-process surrogate of the reward over material descriptors.

Used by MCTS when expansion_prior == 'model': the estimate of an unevaluated
material is an acquisition value (mean + beta * std, or expected improvement)
from a GP fitted to every reward computed so far. The GP has a Matern-5/2
kernel with one length scale per descriptor and a white-noise term; the
hyperparameters are set by maximizing the log marginal likelihood (L-BFGS-B
with analytic gradients) and are refitted every `refit_every` new points, the
Cholesky factor being updated with the fixed hyperparameters in between.

Only numpy and scipy are required.

© 2026. Triad National Security, LLC. All rights reserved.
"""

from typing import Optional, Tuple

import numpy as np
from scipy.linalg import cho_factor, cho_solve, cholesky
from scipy.optimize import minimize
from scipy.stats import norm

_SQRT5 = np.sqrt(5.0)


def _sqdist_scaled(X: np.ndarray, Z: np.ndarray, ls: np.ndarray) -> np.ndarray:
    """Per-dimension squared scaled differences summed: r^2[i, j] = sum_d ((X_id - Z_jd) / ls_d)^2."""
    Xs, Zs = X / ls, Z / ls
    r2 = (Xs ** 2).sum(1)[:, None] + (Zs ** 2).sum(1)[None, :] - 2.0 * Xs @ Zs.T
    return np.maximum(r2, 0.0)


def _matern52(r2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Matern-5/2 correlation and the factor e^{-sqrt5 r} (1 + sqrt5 r) used by its gradient."""
    r = np.sqrt(r2)
    e = np.exp(-_SQRT5 * r)
    return (1.0 + _SQRT5 * r + 5.0 * r2 / 3.0) * e, e * (1.0 + _SQRT5 * r)


class GaussianProcess:
    """Matern-5/2 ARD Gaussian process on standardized targets."""

    def __init__(self, n_dim: int, refit_every: int = 10, max_iter: int = 40, noise_floor: float = 1e-4):
        self.n_dim = n_dim
        self.refit_every = refit_every
        self.max_iter = max_iter
        self.noise_floor = noise_floor
        # log hyperparameters: length scales (n_dim), signal variance, noise variance
        self.theta = np.concatenate([np.zeros(n_dim), [0.0], [np.log(1e-2)]])
        self.X: Optional[np.ndarray] = None
        self.y_mean = 0.0
        self.y_std = 1.0
        self._n_fitted_hyper = 0
        self._L: Optional[np.ndarray] = None
        self._alpha: Optional[np.ndarray] = None
        self.y_best = -np.inf

    # ---- kernel and likelihood ---------------------------------------
    def _kernel(self, X: np.ndarray, Z: np.ndarray, theta: np.ndarray) -> np.ndarray:
        ls, sf2 = np.exp(theta[: self.n_dim]), np.exp(2.0 * theta[self.n_dim])
        k, _ = _matern52(_sqdist_scaled(X, Z, ls))
        return sf2 * k

    def _nll_and_grad(self, theta: np.ndarray, X: np.ndarray, y: np.ndarray):
        n = len(y)
        ls, sf2, sn2 = np.exp(theta[: self.n_dim]), np.exp(2.0 * theta[self.n_dim]), np.exp(2.0 * theta[self.n_dim + 1])
        r2 = _sqdist_scaled(X, X, ls)
        corr, efac = _matern52(r2)
        K = sf2 * corr + (sn2 + self.noise_floor) * np.eye(n)
        try:
            L = cholesky(K, lower=True)
        except np.linalg.LinAlgError:
            return 1e25, np.zeros_like(theta)
        alpha = cho_solve((L, True), y)
        nll = 0.5 * y @ alpha + np.log(np.diag(L)).sum() + 0.5 * n * np.log(2 * np.pi)
        Kinv = cho_solve((L, True), np.eye(n))
        W = Kinv - np.outer(alpha, alpha)          # d nll / dK = 0.5 * W
        grad = np.empty_like(theta)
        base = sf2 * (5.0 / 3.0) * efac            # common factor of d k / d log(ls_d)
        for d in range(self.n_dim):
            diff2 = (X[:, d][:, None] - X[:, d][None, :]) ** 2 / ls[d] ** 2
            grad[d] = 0.5 * np.sum(W * (base * diff2))
        grad[self.n_dim] = 0.5 * np.sum(W * (2.0 * sf2 * corr))
        grad[self.n_dim + 1] = 0.5 * np.trace(W) * 2.0 * sn2
        return nll, grad

    # ---- fitting -----------------------------------------------------
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit to all points; refit the hyperparameters every refit_every new points."""
        X = np.asarray(X, float); y = np.asarray(y, float)
        self.y_mean, self.y_std = float(y.mean()), float(y.std()) + 1e-9
        ys = (y - self.y_mean) / self.y_std
        if len(y) >= 3 and (self._n_fitted_hyper == 0 or len(y) - self._n_fitted_hyper >= self.refit_every):
            res = minimize(self._nll_and_grad, self.theta, args=(X, ys), jac=True, method="L-BFGS-B",
                           bounds=[(-4.0, 4.0)] * self.n_dim + [(-3.0, 3.0), (np.log(1e-3), 0.0)],
                           options={"maxiter": self.max_iter})
            if np.isfinite(res.fun):
                self.theta = res.x
            self._n_fitted_hyper = len(y)
        n = len(y)
        sn2 = np.exp(2.0 * self.theta[self.n_dim + 1])
        K = self._kernel(X, X, self.theta) + (sn2 + self.noise_floor) * np.eye(n)
        self._L = cholesky(K, lower=True)
        self._alpha = cho_solve((self._L, True), ys)
        self.X = X
        self.y_best = float(ys.max())

    @property
    def is_fitted(self) -> bool:
        return self._alpha is not None

    def predict(self, Z: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Posterior mean and standard deviation (in the original reward units)."""
        Z = np.atleast_2d(np.asarray(Z, float))
        Ks = self._kernel(Z, self.X, self.theta)
        mu = Ks @ self._alpha
        v = cho_solve((self._L, True), Ks.T)
        sf2 = np.exp(2.0 * self.theta[self.n_dim])
        var = np.maximum(sf2 - np.einsum("ij,ji->i", Ks, v), 1e-12)
        return mu * self.y_std + self.y_mean, np.sqrt(var) * self.y_std

    def acquisition(self, Z: np.ndarray, kind: str = "ucb", beta: float = 1.0) -> np.ndarray:
        """'ucb': mean + beta * std; 'ei': expected improvement over the best observed reward."""
        mu, sd = self.predict(Z)
        if kind == "ucb":
            return mu + beta * sd
        best = self.y_best * self.y_std + self.y_mean
        z = (mu - best) / sd
        return (mu - best) * norm.cdf(z) + sd * norm.pdf(z)
