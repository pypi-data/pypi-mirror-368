### Correlated Topic Models in PyTorch (ADVI)

An end-to-end, clean implementation of the Correlated Topic Model (CTM) with Automatic Differentiation Variational Inference (ADVI) in PyTorch. This repo includes dataset preprocessing, training, evaluation, TensorBoard logging, and utilities to export topics and compute topic coherence.

CTM extends LDA by replacing the Dirichlet prior over document-topic proportions with a logistic-normal prior with full covariance, capturing correlations between topics.

### Highlights

- Full-covariance logistic-normal prior parameterized via a learned Cholesky factor
- Mean-field Gaussian per-document variational posterior trained with ADVI
- Mini-batch ELBO with MC estimates of the collapsed word-likelihood
- Optional symmetric Dirichlet prior on topic-word distributions `beta`
- TensorBoard logging and optional metrics plot export
- Reproducible training with saved configs and exact vocabulary for deterministic inference

### Project Structure

```
src/ctm/
  __init__.py
  config.py         # TrainConfig dataclass (CLI surface)
  data.py           # 20NG loader + vectorization + DataLoaders
  model.py          # CTM module + ELBO
  train.py          # training loop, logging, checkpointing
  infer.py          # top-words, coherence, perplexity
  utils.py          # math and evaluation helpers
src/scripts/
  export_topics.py  # export top words to CSV from a checkpoint
```

### Requirements

- Python >= 3.10
- Key dependencies (see `pyproject.toml`): 

```
torch
numpy
scipy
scikit-learn
tqdm
tyro
rich
tensorboard
matplotlib
spacy
```

If you enable lemmatization, install a spaCy model:

```bash
python -m spacy download en_core_web_sm
```

### Install

Using uv (recommended):

```bash
uv venv
uv sync
```

Or using pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Dataset

Training uses scikit-learn 20 Newsgroups. Text is vectorized via `CountVectorizer` with n-grams `(1, 3)`, English stopwords, token pattern `(?u)\b[a-zA-Z]{3,}\b`, and configurable `max_df`, `min_df`, and `vocab_size`. Optionally, spaCy lemmatization can be enabled. A validation split is drawn from the training set.

### Quickstart

Train a CTM with 50 topics and a 5k vocabulary:

```bash
uv run python -m ctm.train --num-topics 50 --vocab-size 5000 --epochs 50 --batch-size 128 --lr 1e-2
```

After training, export top words and evaluate metrics:

```bash
uv run python -m ctm.infer --checkpoint runs/ctm/ctm_k50_v5000_e50_b128/ctm.pt --topn 12
```

Export topics to CSV:

```bash
uv run python src/scripts/export_topics.py --checkpoint runs/ctm/ctm_k50_v5000_e50_b128/ctm.pt --topn 15 --out topics.csv
```

### CLI Usage

Training (`ctm.train`) uses `tyro` to expose the `TrainConfig` as CLI flags. Defaults shown below:

```bash
uv run python -m ctm.train \
  --num-topics 80 \
  --vocab-size 10000 \
  --max-df 0.95 \
  --min-df 5 \
  --remove-headers True \
  --remove-footers True \
  --remove-quotes True \
  --batch-size 128 \
  --epochs 50 \
  --lr 0.01 \
  --beta-dirichlet-alpha 0.05 \
  --mc-samples 5 \
  --seed 42 \
  --log-every 50 \
  --ckpt-dir runs/ctm \
  --device cuda \
  --val-split 0.1 \
  --use-tensorboard True \
  --plot-metrics False \
  --tensorboard-subdir tb \
  --use-lemmatization True \
  --spacy-model en_core_web_sm
```

Inference (`ctm.infer`) options:

```bash
uv run python -m ctm.infer \
  --checkpoint runs/ctm/ctm_k80_v10000_e50_b128/ctm.pt \
  --topn 10 \
  --mc-samples 32 \
  --device cuda \
  --batch-size 256 \
  --coherence-metric npmi \
  --penalize-zero-npmi True \
  --fold-in-val True \
  --fold-in-steps 150 \
  --fold-in-lr 0.05
```

Notes:
- Set `--device cpu` if you do not have a CUDA GPU.
- Inference loads the exact vocabulary saved during training for consistent evaluation.

### Outputs

For a run with `K=80`, `V=10000`, `epochs=50`, `batch_size=128`, outputs are placed under:

```
runs/ctm/ctm_k80_v10000_e50_b128/
  ├── config.json           # full TrainConfig used
  ├── ctm.pt                # checkpoint: model_state, m_all, logvar_all, vocab, N_train, N_val, cfg
  ├── tb/                   # TensorBoard events (if enabled)
  ├── metrics.png           # optional plot (if plot_metrics=True)
  └── top_words.txt         # written by ctm.infer
```

### Model and Objective (brief)

- Document-topic logits: `eta_d ~ N(mu, Sigma)`, with `Sigma = L L^T` learned via an unconstrained `L_raw` -> `L = tril(L_raw)` with softplus on the diagonal.
- Topic proportions: `theta = softmax(eta)`.
- Likelihood: words drawn from the mixture `p(v | eta, beta) = sum_k theta_k beta_{k,v}`.
- Per-document variational posterior: `q(eta_d) = N(m_d, diag(exp(logvar_d)))`.
- ELBO estimated with Monte Carlo samples for the expected log-likelihood; global prior includes optional symmetric Dirichlet on `beta`.

### TensorBoard

Enable with `--use-tensorboard True` and then run:

```bash
tensorboard --logdir runs/ctm/ctm_k80_v10000_e50_b128/tb
```

### Reproducibility

- Seeds are set for Python, NumPy, and PyTorch (`--seed`).
- Training saves the exact vectorizer vocabulary to the checkpoint; inference reconstructs data using it to ensure alignment.

### FAQ / Troubleshooting

- 20 Newsgroups download fails: ensure internet access; scikit-learn will cache the dataset.
- CUDA not used: pass `--device cpu` or ensure your PyTorch build detects CUDA.
- spaCy errors: install the model `en_core_web_sm` or disable lemmatization with `--use-lemmatization False`.

### License

MIT

### References

- Blei, D. M., & Lafferty, J. D. (2006). Correlated Topic Models.