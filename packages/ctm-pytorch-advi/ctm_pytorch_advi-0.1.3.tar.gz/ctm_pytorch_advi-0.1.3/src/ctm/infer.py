"""
Inference script for the CTM model.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

import torch
import tyro
from rich.console import Console

from .data import NewsgroupsBOW
from .model import CTM
from .utils import compute_per_word_perplexity, compute_topic_coherence

console = Console()


@dataclass
class InferConfig:
    """
    Configuration for inference.
    """

    checkpoint: str
    topn: int = 10
    mc_samples: int = 32
    device: str = "cuda"
    batch_size: int = 256
    coherence_metric: str = "npmi"  # one of: "npmi", "umass"
    penalize_zero_npmi: bool = True
    # Optional held-out fold-in for eval perplexity
    fold_in_val: bool = True
    fold_in_steps: int = 150
    fold_in_lr: float = 0.05


def top_words(
    beta: torch.Tensor,
    vocab: List[str],
    topn: int,
) -> List[List[str]]:
    """
    Get the top words for each topic.
    """

    # beta: (K, V)
    topk = beta.argsort(dim=-1, descending=True)[:, :topn]  # (K, topn)
    words = []
    for k in range(beta.size(0)):
        words.append([vocab[j] for j in topk[k].tolist()])
    return words


def main(cfg: InferConfig = tyro.cli(InferConfig)):
    """
    Main function for inference.

    Args:
        cfg: Configuration for inference.

    Returns:
        None
    """

    device = cfg.device if torch.cuda.is_available() and cfg.device == "cuda" else "cpu"
    ckpt = torch.load(cfg.checkpoint, map_location=device)
    run_dir = os.path.dirname(cfg.checkpoint)
    model = CTM(
        num_topics=ckpt["cfg"]["num_topics"],
        vocab_size=len(ckpt["vocab"]),
        beta_dirichlet_alpha=ckpt["cfg"]["beta_dirichlet_alpha"],
        device=device,
    )
    model.load_state_dict(ckpt["model_state"])
    model.to(device).eval()

    vocab = ckpt["vocab"]
    beta = model.beta.detach().cpu()
    words = top_words(beta, vocab, cfg.topn)

    # table = Table(title="Top words per topic")
    # table.add_column("Topic")
    # table.add_column("Words")
    # for k, ws in enumerate(words):
    #     table.add_row(str(k), ", ".join(ws))
    # console.print(table)

    # Save the top words to a file
    with open(os.path.join(run_dir, "top_words.txt"), "w", encoding="utf-8") as f:
        for k, ws in enumerate(words):
            f.write(f"Topic {k}: {', '.join(ws)}\n")

    # Show a quick summary of the prior correlations via Sigma
    with torch.no_grad():
        L = model.prior_cholesky()
        Sigma = L @ L.T
        # Correlation matrix from Sigma
        D = torch.sqrt(torch.diagonal(Sigma))
        corr = Sigma / (D.unsqueeze(0) * D.unsqueeze(1) + 1e-12)
        console.print(
            f"Avg |correlation| (off-diagonal): {corr.fill_diagonal_(0.0).abs().mean().item():.4f}"
        )

    # Load the original dataset using the saved config
    data_cfg = ckpt["cfg"]
    ng = NewsgroupsBOW(
        vocab_size=data_cfg["vocab_size"],
        max_df=data_cfg["max_df"],
        min_df=data_cfg["min_df"],
        remove_headers=data_cfg["remove_headers"],
        remove_footers=data_cfg["remove_footers"],
        remove_quotes=data_cfg["remove_quotes"],
        seed=data_cfg["seed"],
        val_split=data_cfg["val_split"],
        use_lemmatization=data_cfg.get("use_lemmatization", False),
        spacy_model=data_cfg.get("spacy_model", "en_core_web_sm"),
        vocabulary=vocab,
    )
    bow = ng.load()

    # Slice the saved variational params for train and val
    m_all: torch.Tensor = ckpt["m_all"].to(device)
    logvar_all: torch.Tensor = ckpt["logvar_all"].to(device)
    N_train = int(ckpt.get("N_train", bow.X_train.shape[0]))
    N_val = int(ckpt.get("N_val", bow.X_val.shape[0]))

    m_train, logvar_train = m_all[:N_train], logvar_all[:N_train]
    m_val, logvar_val = (
        m_all[N_train : N_train + N_val],
        logvar_all[N_train : N_train + N_val],
    )

    # Compute per-word perplexity on train/val using saved variational params
    ppl_train = compute_per_word_perplexity(
        bow.X_train,
        m_train,
        logvar_train,
        model.beta,
        mc_samples=cfg.mc_samples,
        batch_size=cfg.batch_size,
        device=device,
    )
    # Optionally run held-out inference for val docs
    if cfg.fold_in_val:
        import torch.nn as nn

        X = bow.X_val.tocsr()
        D, V = X.shape
        K = model.K
        m_local = nn.Parameter(torch.zeros((D, K), device=device))
        logvar_local = nn.Parameter(torch.zeros((D, K), device=device))
        for p in model.parameters():
            p.requires_grad_(False)
        opt = torch.optim.Adam([m_local, logvar_local], lr=cfg.fold_in_lr)
        L = model.prior_cholesky()
        for _ in range(cfg.fold_in_steps):
            for start in range(0, D, cfg.batch_size):
                end = min(start + cfg.batch_size, D)
                B = end - start
                Xb = torch.zeros((B, V), dtype=torch.float32, device=device)
                for b, i in enumerate(range(start, end)):
                    idx = X.indices[X.indptr[i] : X.indptr[i + 1]]
                    cnt = X.data[X.indptr[i] : X.indptr[i + 1]]
                    if idx.size > 0:
                        Xb[b, torch.as_tensor(idx, device=device)] = torch.as_tensor(
                            cnt, dtype=torch.float32, device=device
                        )
                elbo, _ = model.elbo_batch(
                    X=Xb,
                    m=m_local[start:end],
                    logvar=logvar_local[start:end],
                    L=L,
                    mc_samples=cfg.mc_samples,
                    scale=1.0,
                )
                loss = -elbo
                opt.zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_([m_local, logvar_local], max_norm=5.0)
                opt.step()
        m_val_eval, logvar_val_eval = m_local.detach(), logvar_local.detach()
    else:
        m_val_eval, logvar_val_eval = m_val, logvar_val

    ppl_val = compute_per_word_perplexity(
        bow.X_val,
        m_val_eval,
        logvar_val_eval,
        model.beta,
        mc_samples=cfg.mc_samples,
        batch_size=cfg.batch_size,
        device=device,
    )
    console.print(f"Per-word perplexity (train): {ppl_train:.3f}")
    console.print(f"Per-word perplexity (val):   {ppl_val:.3f}")

    # Compute topic coherence on the training corpus
    mean_coh, _ = compute_topic_coherence(
        model.beta.detach().cpu(),
        bow.X_train,
        vocab,
        topn=cfg.topn,
        metric=cfg.coherence_metric,
        penalize_zeros=cfg.penalize_zero_npmi,
    )
    console.print(
        f"Topic coherence [{cfg.coherence_metric.upper()}] (mean over topics): {mean_coh:.4f}"
    )


if __name__ == "__main__":
    main()
