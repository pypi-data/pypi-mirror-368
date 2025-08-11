# Utility to export topics to a CSV
import argparse, csv, torch
from ctm.model import CTM

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--topn", type=int, default=15)
    ap.add_argument("--out", default="topics.csv")
    args = ap.parse_args()

    ckpt = torch.load(args.checkpoint, map_location="cpu")
    model = CTM(
        num_topics=ckpt["cfg"]["num_topics"],
        vocab_size=len(ckpt["vocab"]),
        beta_dirichlet_alpha=ckpt["cfg"]["beta_dirichlet_alpha"],
        device="cpu",
    )
    model.load_state_dict(ckpt["model_state"])
    beta = model.beta.detach()
    vocab = ckpt["vocab"]

    topk = beta.argsort(dim=-1, descending=True)[:, :args.topn]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["topic", "words"])
        for k in range(beta.size(0)):
            words = [vocab[j] for j in topk[k].tolist()]
            w.writerow([k, " ".join(words)])

    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
