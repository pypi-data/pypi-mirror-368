from __future__ import annotations

from typing import Optional, Tuple

import torch
import torch.nn.functional as F
from torch import nn

from .utils import (
    diag_inverse_from_cholesky,
    logdet_from_cholesky,
    make_tril,
    quad_form_solve_cholesky,
)


class CTM(nn.Module):
    """Correlated Topic Model with ADVI.

    - Global parameters:
        * beta_logits: (K, V) -> beta = softmax over V
        * mu: (K,)
        * L_raw: (K, K) -> L = tril with softplus diag, Sigma = L L^T

    - Per-document variational parameters (kept externally):
        * m_d: (D, K)
        * logvar_d: (D, K)  (variances on diagonal)

    Likelihood:
        x_d ~ Multinomial with probability mixture p_v = sum_k theta_k beta_{k,v}, where theta = softmax(eta).
    We use MC to approximate E_q[log p(x_d | eta_d, beta)].
    """

    def __init__(
        self,
        num_topics: int,
        vocab_size: int,
        beta_dirichlet_alpha: float = 0.05,
        device: str = "cpu",
    ):
        super().__init__()
        self.K = num_topics
        self.V = vocab_size
        self.device = device

        # topic-word distributions
        self.beta_logits = nn.Parameter(torch.empty(self.K, self.V, device=device))
        nn.init.normal_(self.beta_logits, mean=0.0, std=0.02)

        # logistic-normal prior parameters
        self.mu = nn.Parameter(torch.zeros(self.K, device=device))
        self.L_raw = nn.Parameter(torch.randn(self.K, self.K, device=device) * 0.05)

        # symmetric Dirichlet prior concentration for beta
        self.alpha = beta_dirichlet_alpha

    @property
    def beta(self) -> torch.Tensor:
        return F.softmax(self.beta_logits, dim=-1)  # (K, V)

    def prior_cholesky(self) -> torch.Tensor:
        return make_tril(self.L_raw)  # (K, K)

    def prior_logdet(self, L: torch.Tensor) -> torch.Tensor:
        return logdet_from_cholesky(L)

    def dirichlet_log_prior_beta(self) -> torch.Tensor:
        """Log p(beta | alpha) with symmetric Dir(alpha) prior. Summed over topics.
        log Dir(beta_k; alpha) = logGamma(V*alpha) - V*logGamma(alpha) + (alpha-1) * sum_v log beta_{kv}
        """
        if self.alpha is None or self.alpha <= 0.0:
            return torch.tensor(0.0, device=self.device)
        beta = self.beta
        V = beta.size(1)
        a = torch.tensor(self.alpha, device=self.device)
        term0 = torch.lgamma(V * a) - V * torch.lgamma(a)
        term1 = (a - 1.0) * torch.log(beta + 1e-12).sum(-1)  # sum over vocab
        return (term0 + term1).sum()  # sum over topics

    def elbo_batch(
        self,
        X: torch.Tensor,  # (B, V) counts
        m: torch.Tensor,  # (B, K) variational means for docs
        logvar: torch.Tensor,  # (B, K) variational log-variances for docs
        L: Optional[torch.Tensor] = None,  # (K, K) prior cholesky
        mc_samples: int = 1,
        scale: float = 1.0,  # scaling factor N / B for minibatch
    ) -> Tuple[torch.Tensor, dict]:
        B, V = X.shape
        K = self.K
        assert m.shape == (B, K) and logvar.shape == (B, K)

        if L is None:
            L = self.prior_cholesky()
        mu = self.mu

        # Precompute Sigma^{-1} diag and logdet for KL terms
        logdet = self.prior_logdet(L)
        diag_inv = diag_inverse_from_cholesky(L)  # (K,)

        var = torch.exp(logvar)  # (B, K)

        # KL(q||p) per doc
        # trace(Sigma^{-1} S_d) = sum_i var_i * (Sigma^{-1})_{ii}
        trace_term = (var * diag_inv.unsqueeze(0)).sum(-1)  # (B,)
        # quadratic form (m-mu)^T Sigma^{-1} (m-mu)
        diff = m - mu.unsqueeze(0)  # (B, K)
        quad = quad_form_solve_cholesky(L, diff)  # (B,)
        # log|S_d| = sum logvar
        logdet_q = logvar.sum(-1)  # (B,)

        kl = 0.5 * (trace_term + quad - K + logdet - logdet_q)  # (B,)
        kl_sum = kl.sum()

        # Expected log likelihood via MC
        # sample eta ~ q
        # eta = m + sqrt(var) * eps
        # theta = softmax(eta)
        # p(w=v | eta, beta) = sum_k theta_k * beta_{k,v}
        beta = self.beta  # (K, V)

        ll = 0.0
        for _ in range(mc_samples):
            eps = torch.randn_like(m)
            eta = m + torch.sqrt(var + 1e-12) * eps  # (B, K)
            theta = F.softmax(eta, dim=-1)  # (B, K)
            mix = theta @ beta  # (B, V)
            mix = torch.clamp(mix, min=1e-12)
            ll += (X * torch.log(mix)).sum()
        ll = ll / mc_samples

        # Scale doc terms (likelihood and KL) by N/B to unbiasedly estimate sum over docs
        elbo_docs = scale * (ll - kl_sum)

        # Global prior on beta (do NOT scale by N/B)
        logp_beta = self.dirichlet_log_prior_beta()

        elbo = elbo_docs + logp_beta
        metrics = {
            "elbo_docs": elbo_docs.detach(),
            "ll_docs": (scale * ll).detach(),
            "kl_docs": (scale * kl_sum).detach(),
            "logp_beta": logp_beta.detach(),
        }
        return elbo, metrics
