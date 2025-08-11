from __future__ import annotations

import json
import os
import random
from dataclasses import asdict

import matplotlib.pyplot as plt
import numpy as np
import torch
import tyro
from rich.console import Console
from torch import nn
from tqdm import tqdm

from .config import TrainConfig
from .data import NewsgroupsBOW, make_dataloaders
from .model import CTM

console = Console()


def set_seed(seed: int):
    """
    Set the seed for the random number generators.
    """

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def main(cfg: TrainConfig = tyro.cli(TrainConfig)):
    set_seed(cfg.seed)
    device = (
        cfg.device
        if torch.cuda.is_available() and cfg.device == "cuda"
        # else "mps"
        # if torch.backends.mps.is_available()
        else "cpu"
    )
    console.print(f"[bold green]Device:[/bold green] {device}")

    # Load data
    ng = NewsgroupsBOW(
        vocab_size=cfg.vocab_size,
        max_df=cfg.max_df,
        min_df=cfg.min_df,
        remove_headers=cfg.remove_headers,
        remove_footers=cfg.remove_footers,
        remove_quotes=cfg.remove_quotes,
        seed=cfg.seed,
        val_split=cfg.val_split,
        use_lemmatization=cfg.use_lemmatization,
        spacy_model=cfg.spacy_model,
    )
    bow = ng.load()
    train_loader, val_loader, N_train, N_val, V = make_dataloaders(
        bow.X_train, bow.X_val, cfg.batch_size, device=device
    )
    console.print(f"Train docs: {N_train}, Val docs: {N_val}, Vocab: {V}")

    # Model
    model = CTM(
        cfg.num_topics,
        V,
        beta_dirichlet_alpha=cfg.beta_dirichlet_alpha,
        device=device,
    ).to(device)

    # Per-document variational parameters (mean, logvar)
    # We keep all docs from TRAIN + VAL jointly (so that val ELBO can be computed consistently)
    D_total = N_train + N_val
    m_all = nn.Parameter(
        torch.zeros(
            D_total,
            cfg.num_topics,
            device=device,
        )
    )
    logvar_all = nn.Parameter(
        torch.zeros(
            D_total,
            cfg.num_topics,
            device=device,
        )
    )

    # Optimizer
    optim = torch.optim.AdamW(
        [
            {"params": model.parameters(), "lr": cfg.lr},
            {"params": [m_all, logvar_all], "lr": cfg.lr},
        ]
    )

    # Run directory (resolve relative paths under the current working directory)
    ckpt_base = cfg.ckpt_dir
    if not os.path.isabs(ckpt_base):
        ckpt_base = os.path.abspath(os.path.join(os.getcwd(), ckpt_base))
    run_dir = os.path.join(
        ckpt_base,
        f"ctm_k{cfg.num_topics}_v{cfg.vocab_size}_e{cfg.epochs}_b{cfg.batch_size}",
    )
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(asdict(cfg), f, indent=2)

    # TensorBoard setup
    tb_writer = None
    if getattr(cfg, "use_tensorboard", False):
        try:
            from torch.utils.tensorboard import SummaryWriter

            tb_subdir = getattr(cfg, "tensorboard_subdir", "tb")
            tb_dir = os.path.join(run_dir, tb_subdir)
            os.makedirs(tb_dir, exist_ok=True)
            tb_writer = SummaryWriter(log_dir=tb_dir, flush_secs=2)
            console.print(f"[bold green]TensorBoard:[/bold green] logging to {tb_dir}")
        except Exception as e:
            console.print(f"[yellow]TensorBoard disabled ({e})[/yellow]")

    # Metric histories for optional plotting
    history_train_elbo = []
    history_val_elbo = []
    history_train_ll = []
    history_train_kl = []

    best_val = -1e18
    global_step = 0

    for epoch in tqdm(range(1, cfg.epochs + 1), desc="Training", unit="epoch"):
        model.train()
        # train_iter = iter(train_loader)
        # note: we need the correct doc indices to pick variational params; since we split train/val,
        # we map train docs to indices [0, N_train) and val docs to [N_train, N_train + N_val)
        # The collate returns dense tensors only, so we need to infer batch indices ourselves.
        # We'll implement simple cycling over dataset order to align indices.
        # To do this properly, we iterate over the underlying dataset order and slice the variational params accordingly.

        total_elbo = 0.0
        total_ll = 0.0
        total_kl = 0.0
        total_beta_prior = 0.0
        nbatches = 0

        # We re-create a dataloader that also yields the absolute indices of docs

        train_ds = train_loader.dataset  # BowDataset

        def collate_with_ids(batch, offset=0):
            # batch is list of (idx, cnt); we also need their absolute ids
            X = train_loader.collate_fn(batch)
            # DataLoader doesn't pass indices; we will monkey patch by storing last indices via sampler.
            return X

        # Instead, we'll iterate manually over dataset in chunks to know indices.
        B = cfg.batch_size
        for start in range(0, N_train, B):
            end = min(start + B, N_train)
            batch = [train_ds[i] for i in range(start, end)]
            X = train_loader.collate_fn(batch)  # (B, V)
            B_eff = X.size(0)
            idx = torch.arange(start, end, device=device)  # absolute doc ids for train
            m = m_all[idx]
            logvar = logvar_all[idx]

            L = model.prior_cholesky()
            scale = N_train / B_eff
            elbo, metrics = model.elbo_batch(
                X=X, m=m, logvar=logvar, L=L, mc_samples=cfg.mc_samples, scale=scale
            )
            loss = -elbo
            optim.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            torch.nn.utils.clip_grad_norm_([m_all, logvar_all], max_norm=1.0)
            optim.step()

            total_elbo += elbo.item()
            total_ll += metrics["ll_docs"].item()
            total_kl += metrics["kl_docs"].item()
            total_beta_prior += metrics["logp_beta"].item()
            nbatches += 1
            global_step += 1

            if global_step % cfg.log_every == 0:
                console.print(
                    f"[epoch {epoch} step {global_step}] ELBO: {elbo.item():.2f}  "
                    f"LL: {metrics['ll_docs'].item():.2f}  KL: {metrics['kl_docs'].item():.2f}  "
                    f"logp(beta): {metrics['logp_beta'].item():.2f}"
                )
                if tb_writer is not None:
                    tb_writer.add_scalar("train/elbo_batch", elbo.item(), global_step)
                    tb_writer.add_scalar(
                        "train/ll_docs_batch", metrics["ll_docs"].item(), global_step
                    )
                    tb_writer.add_scalar(
                        "train/kl_docs_batch", metrics["kl_docs"].item(), global_step
                    )
                    tb_writer.add_scalar(
                        "train/logp_beta_batch",
                        metrics["logp_beta"].item(),
                        global_step,
                    )
                    tb_writer.flush()

        # Validation ELBO (not used for early stopping strict, but we track best)
        model.eval()
        with torch.no_grad():
            val_elbo_total = 0.0
            nb = 0
            val_ds = val_loader.dataset
            for start in range(0, N_val, B):
                end = min(start + B, N_val)
                batch = [val_ds[i] for i in range(start, end)]
                X = val_loader.collate_fn(batch)
                B_eff = X.size(0)
                idx = torch.arange(
                    N_train + start, N_train + end, device=device
                )  # offset indices
                m = m_all[idx]
                logvar = logvar_all[idx]
                L = model.prior_cholesky()
                scale = N_val / B_eff
                elbo, _ = model.elbo_batch(
                    X=X, m=m, logvar=logvar, L=L, mc_samples=cfg.mc_samples, scale=scale
                )
                val_elbo_total += elbo.item()
                nb += 1
            val_elbo = val_elbo_total / max(nb, 1)

        train_elbo = total_elbo / max(nbatches, 1)
        train_ll_avg = total_ll / max(nbatches, 1)
        train_kl_avg = total_kl / max(nbatches, 1)

        # # Log table
        # table = Table(title=f"Epoch {epoch}")
        # table.add_column("Metric")
        # table.add_column("Value")
        # table.add_row("Train ELBO (avg/batch)", f"{train_elbo:.2f}")
        # table.add_row("Train LL (sum scaled)", f"{train_ll_avg:.2f}")
        # table.add_row("Train KL (sum scaled)", f"{train_kl_avg:.2f}")
        # table.add_row("log p(beta)", f"{total_beta_prior/nbatches:.2f}")
        # table.add_row("Val ELBO (avg/batch)", f"{val_elbo:.2f}")
        # console.print(table)

        # TensorBoard scalars per epoch
        if tb_writer is not None:
            tb_writer.add_scalar("elbo/train_avg_per_batch", train_elbo, epoch)
            tb_writer.add_scalar("elbo/val_avg_per_batch", val_elbo, epoch)
            tb_writer.add_scalar("train/ll_sum_scaled_avg", train_ll_avg, epoch)
            tb_writer.add_scalar("train/kl_sum_scaled_avg", train_kl_avg, epoch)
            tb_writer.flush()

        # Append histories
        history_train_elbo.append(train_elbo)
        history_val_elbo.append(val_elbo)
        history_train_ll.append(train_ll_avg)
        history_train_kl.append(train_kl_avg)

        # Save best
        if val_elbo > best_val:
            best_val = val_elbo
            ckpt = {
                "model_state": model.state_dict(),
                "m_all": m_all.clone().cpu(),
                "logvar_all": logvar_all.clone().cpu(),
                "cfg": asdict(cfg),
                # Save the exact vocabulary used to build X matrices to guarantee alignment at inference
                "vocab": bow.vocab,
                "N_train": N_train,
                "N_val": N_val,
            }
            torch.save(ckpt, os.path.join(run_dir, "ctm.pt"))
    console.print(
        f"[bold cyan]Saved checkpoint -> {os.path.join(run_dir, 'ctm.pt')}[/bold cyan]"
    )

    # Optional Matplotlib plot after training
    if getattr(cfg, "plot_metrics", False):
        try:
            fig, axs = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
            epochs = list(range(1, len(history_train_elbo) + 1))
            axs[0].plot(epochs, history_train_elbo, label="Train ELBO")
            axs[0].plot(epochs, history_val_elbo, label="Val ELBO")
            axs[0].set_ylabel("ELBO (avg/batch)")
            axs[0].legend()
            axs[0].grid(True, alpha=0.3)

            axs[1].plot(epochs, history_train_ll, label="Train LL (sum scaled)")
            axs[1].plot(epochs, history_train_kl, label="Train KL (sum scaled)")
            axs[1].set_xlabel("Epoch")
            axs[1].set_ylabel("Value")
            axs[1].legend()
            axs[1].grid(True, alpha=0.3)

            plot_path = os.path.join(run_dir, "metrics.png")
            fig.tight_layout()
            fig.savefig(plot_path)
            console.print(f"[bold green]Saved metrics plot:[/bold green] {plot_path}")
        except Exception as e:
            console.print(f"[yellow]Matplotlib plotting skipped ({e})[/yellow]")

    if tb_writer is not None:
        tb_writer.close()


if __name__ == "__main__":
    main()
