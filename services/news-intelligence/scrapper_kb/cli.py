"""`skb` command line entry point.

`skb publish-radar` re-publishes stored Reports without a new scrape/LLM run
(docs/02-news-radar.md, docs/05-backlog.md Fase 1).
"""

from __future__ import annotations

import argparse
import logging

from .config import load_config
from .pipeline import republish_from_store, run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skb")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--kb-dir", default="kb")
    parser.add_argument("--store-dir", default="store")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("run")
    subparsers.add_parser("publish-radar")

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    config = load_config(args.config)

    if args.command == "run":
        result = run(config, args.kb_dir, args.store_dir)
    else:
        result = republish_from_store(config, args.store_dir)

    print(
        f"signals={len(result.signals)} "
        f"published={len(result.published_ids)} "
        f"failed={len(result.failed_publish_ids)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
