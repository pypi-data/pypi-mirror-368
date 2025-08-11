"""
Configuration for training the CTM model.
"""

from dataclasses import dataclass


@dataclass
class TrainConfig:
    """
    Configuration for training the CTM model.
    """

    num_topics: int = 80
    vocab_size: int = 10000
    max_df: float = 0.95
    min_df: int = 5
    remove_headers: bool = True
    remove_footers: bool = True
    remove_quotes: bool = True
    batch_size: int = 128
    epochs: int = 50
    lr: float = 1e-2
    beta_dirichlet_alpha: float = 0.05
    mc_samples: int = 5
    seed: int = 42
    log_every: int = 50
    ckpt_dir: str = "runs/ctm"
    device: str = "cuda"
    val_split: float = 0.1
    # Visualization/logging
    use_tensorboard: bool = True
    plot_metrics: bool = False
    tensorboard_subdir: str = "tb"
    # Text preprocessing
    use_lemmatization: bool = True
    spacy_model: str = "en_core_web_sm"
