from __future__ import annotations

import math
from typing import List, Sequence, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from scipy import sparse as sp


def make_tril(raw_L: torch.Tensor) -> torch.Tensor:
    """
    Construct a proper lower-triangular matrix with positive diagonal from an unconstrained parameter.

    Args:
        raw_L: Full KxK tensor.

    Returns:
        Lower-triangular matrix with positive diagonal.
    """

    # raw_L is a full KxK tensor; we take its lower triangle and apply softplus to the diagonal.
    L = torch.tril(raw_L)
    diag = torch.diagonal(L, 0)
    diag = torch.nn.Softplus()(diag) + 1e-6
    L = L - torch.diag(torch.diagonal(L)) + torch.diag(diag)
    return L


def logdet_from_cholesky(L: torch.Tensor) -> torch.Tensor:
    """
    Compute the log determinant of a covariance matrix given its Cholesky decomposition.

    Args:
        L: Cholesky decomposition of the covariance matrix.

    Returns:
        Log determinant of the covariance matrix.
    """

    # For Sigma = L L^T, log|Sigma| = 2 * sum log diag(L)
    return 2.0 * torch.log(torch.diagonal(L)).sum()


def diag_inverse_from_cholesky(L: torch.Tensor) -> torch.Tensor:
    """
    Return diag(Sigma^{-1}) given lower-triangular Cholesky factor L, where Sigma = L L^T.

    Args:
        L: Cholesky decomposition of the covariance matrix.

    Returns:
        Diagonal of the inverse of the covariance matrix.
    """

    # We solve Sigma X = I -> X = Sigma^{-1} and return diag(X).
    # This costs O(K^3) but K is small (<= 100) which is fine.

    K = L.size(0)
    I = torch.eye(K, device=L.device, dtype=L.dtype)
    # Solve Sigma X = I using cholesky-based solver
    if hasattr(torch.linalg, "cholesky_solve"):
        X = torch.linalg.cholesky_solve(I, L, upper=False)  # X = Sigma^{-1}
    else:
        X = torch.cholesky_solve(I, L, upper=False)  # X = Sigma^{-1}
    return torch.diagonal(X)


def quad_form_solve_cholesky(L: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """
    Compute b^T Sigma^{-1} b using Cholesky L of Sigma.

    Uses cholesky_solve for maximal version compatibility.

    Args:
        L: Cholesky factor (lower) of Sigma (K, K).
        b: Batch of vectors of shape (..., K).

    Returns:
        Scalar per batch element: (...,).
    """

    # Solve (L L^T) x = b^T for x, then b^T Sigma^{-1} b = sum(b^T * x) over rows
    b_T = b.T  # (K, ...)
    if hasattr(torch.linalg, "cholesky_solve"):
        x = torch.linalg.cholesky_solve(b_T, L, upper=False)
    else:
        x = torch.cholesky_solve(b_T, L, upper=False)
    # x, b_T shapes: (K, B) if b is (B, K)
    return (b_T * x).sum(dim=0)


def expected_theta(
    m: torch.Tensor,
    logvar: torch.Tensor,
    mc_samples: int,
) -> torch.Tensor:
    """
    Monte Carlo estimate of E_q[softmax(eta)], eta ~ N(m, diag(exp(logvar)))

    Args:
        m: Mean of the Gaussian distribution.
        logvar: Log variance of the Gaussian distribution.
        mc_samples: Number of Monte Carlo samples.

    Returns:
        Expected theta.
    """

    # Monte Carlo estimate of E_q[softmax(eta)], eta ~ N(m, diag(exp(logvar)))
    var = torch.exp(logvar)
    thetas = []
    for _ in range(mc_samples):
        eps = torch.randn_like(m)
        eta = m + torch.sqrt(var + 1e-12) * eps
        thetas.append(F.softmax(eta, dim=-1))
    return torch.stack(thetas, dim=0).mean(dim=0)  # (B, K)


def _binary_doc_term_matrix(X_csr) -> sp.csr_matrix:
    """
    Return a boolean CSR doc-term matrix where entries indicate presence of a term.
    """
    X = X_csr.tocsr()
    X_bin = X.copy()
    X_bin.data = np.ones_like(X_bin.data, dtype=np.int8)
    return X_bin


def _top_word_indices_per_topic(beta: torch.Tensor, topn: int) -> List[List[int]]:
    """
    Return topn vocabulary indices per topic from beta (K, V).
    """
    with torch.no_grad():
        topk = beta.argsort(dim=-1, descending=True)[:, :topn]
    return [row.tolist() for row in topk]


def _compute_cooccurrence(
    X_bin: sp.csr_matrix, vocab_indices: Sequence[int]
) -> np.ndarray:
    """
    Compute a document co-occurrence matrix for a subset of vocabulary indices.

    Returns an array C of shape (M, M) where C[i, j] is the number of docs
    containing both vocab_indices[i] and vocab_indices[j].
    """
    # Subset columns and force boolean
    X_sub = X_bin[:, vocab_indices]
    # Doc co-occurrence using sparse multiplication
    C = (X_sub.T @ X_sub).astype(np.int64)
    if sp.issparse(C):
        C = C.toarray()
    return C


def compute_topic_coherence(
    beta: torch.Tensor,
    X_csr,
    _vocab: List[str],
    topn: int = 10,
    metric: str = "npmi",
    penalize_zeros: bool = True,
) -> Tuple[float, List[float]]:
    """
    Compute topic coherence (UMass or NPMI) from beta and corpus document counts.

    Args:
        beta: Topic-word probabilities (K, V).
        X_csr: Corpus document-term matrix (CSR or compatible) over the same vocab.
        vocab: Vocabulary list (unused for math, helpful for debugging).
        topn: Number of top words per topic.
        metric: "umass" or "npmi".

    Returns:
        (mean_coherence, per_topic_coherence_list)
    """
    metric = metric.lower()
    assert metric in {"umass", "npmi"}

    X_bin = _binary_doc_term_matrix(X_csr)
    num_docs = X_bin.shape[0]

    # Get top indices per topic and their union for efficient cooccurrence computation
    top_indices_per_topic = _top_word_indices_per_topic(beta, topn)
    union_indices = sorted({idx for topic in top_indices_per_topic for idx in topic})
    index_to_union_pos = {v_idx: i for i, v_idx in enumerate(union_indices)}

    C = _compute_cooccurrence(X_bin, union_indices)
    # Single-word document frequencies
    df_union = np.diag(C).astype(np.int64)

    per_topic_scores: List[float] = []
    eps = 1e-12

    for topic_word_indices in top_indices_per_topic:
        # Map to union positions
        topic_pos = [index_to_union_pos[j] for j in topic_word_indices]
        scores: List[float] = []
        for i in range(len(topic_pos)):
            for j in range(i + 1, len(topic_pos)):
                a = topic_pos[i]
                b = topic_pos[j]
                co = C[a, b]
                df_b = df_union[b]
                if metric == "umass":
                    # UMass: log((D(w_i, w_j) + 1) / D(w_j)) using doc counts
                    denom = max(df_b, 0) + 0.0
                    score = math.log((co + 1.0) / (denom + eps))
                else:
                    # NPMI: pmi / -log p(w_i,w_j), bounded in [-1, 1]
                    # Probabilities in (0,1)
                    p_i = df_union[a] / num_docs
                    p_j = df_union[b] / num_docs
                    p_ij = co / num_docs
                    if p_ij <= 0.0 or p_i <= 0.0 or p_j <= 0.0:
                        if penalize_zeros:
                            scores.append(-1.0)
                        continue
                    pmi = math.log(p_ij / (p_i * p_j))
                    denom = -math.log(p_ij)
                    if denom <= 0.0:
                        if penalize_zeros:
                            scores.append(-1.0)
                        continue
                    score = pmi / denom
                    # Clip for numerical safety
                    if score > 1.0:
                        score = 1.0
                    elif score < -1.0:
                        score = -1.0
                scores.append(score)
        per_topic_scores.append(
            float(np.mean(scores)) if len(scores) > 0 else float("nan")
        )

    mean_score = float(np.nanmean(np.array(per_topic_scores, dtype=np.float64)))
    return mean_score, per_topic_scores


@torch.no_grad()
def compute_per_word_perplexity(
    X_csr,
    m: torch.Tensor,
    logvar: torch.Tensor,
    beta: torch.Tensor,
    mc_samples: int = 32,
    batch_size: int = 256,
    device: str = "cpu",
) -> float:
    """
    Approximate per-word perplexity: exp(- total_log_likelihood / total_token_count).

    Uses MC expectation over q(eta | m, logvar) for each document; beta is fixed.
    """
    X = X_csr.tocsr()
    N_docs, V = X.shape
    assert beta.shape[1] == V
    total_ll = 0.0
    total_tokens = 0.0

    # Pre-move for speed
    beta_t = beta.to(device)
    for start in range(0, N_docs, batch_size):
        end = min(start + batch_size, N_docs)
        batch = [
            (
                X.indices[X.indptr[i] : X.indptr[i + 1]],
                X.data[X.indptr[i] : X.indptr[i + 1]],
            )
            for i in range(start, end)
        ]
        # Build dense batch on device
        B = len(batch)
        Xb = torch.zeros((B, V), dtype=torch.float32, device=device)
        for b, (idx, cnt) in enumerate(batch):
            if idx.size > 0:
                Xb[b, torch.as_tensor(idx, device=device)] = torch.as_tensor(
                    cnt, dtype=torch.float32, device=device
                )
        # Select variational params
        m_b = m[start:end].to(device)
        logvar_b = logvar[start:end].to(device)
        var_b = torch.exp(logvar_b)

        ll_sum = 0.0
        for _ in range(mc_samples):
            eps = torch.randn_like(m_b)
            eta = m_b + torch.sqrt(var_b + 1e-12) * eps
            theta = F.softmax(eta, dim=-1)  # (B, K)
            mix = torch.clamp(theta @ beta_t, min=1e-12)  # (B, V)
            ll_sum += (Xb * torch.log(mix)).sum().item()
        total_ll += ll_sum / mc_samples
        total_tokens += float(Xb.sum().item())

    if total_tokens <= 0.0:
        return float("nan")
    ppl = math.exp(-total_ll / total_tokens)
    return float(ppl)
