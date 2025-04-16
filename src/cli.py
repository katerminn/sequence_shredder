import argparse
import logging
import os
import sys
import random

from datetime import datetime

from src.data_io import load_reference, load_vcf, write_fasta, load_config
from src.consensus import generate_consensus_sequences
from src.logging_config import setup_logging


def parse_args():
    config = load_config()

    parser = argparse.ArgumentParser(
        description="VCF -> Sample-specific consensus sequence generator"
    )

    parser.add_argument("--vcf", default=config.get("vcf"), help="Path to input VCF file")
    parser.add_argument("--fasta", default=config.get("fasta"), help="Path to reference genome FASTA file")
    parser.add_argument("--output", default=config.get("output"), help="Output FASTA filename prefix")

    parser.add_argument("--consensus-length", type=int, default=config.get("consensus_length"))
    parser.add_argument("--consensus-count", type=int, default=config.get("consensus_count"))

    parser.add_argument("--min-af", type=float, default=config.get("min_af"))
    parser.add_argument("--start-step", type=int, default=config.get("start_step"))

    parser.add_argument("--random-start", action="store_true", help="...")
    parser.add_argument("--no-random-start", dest="random_start", action="store_false", help="...")

    parser.add_argument("--max-overlap", type=int, default=config.get("max_overlap"))
    parser.add_argument("--sample-list", type=str, default=None)
    parser.add_argument("--seed", type=int, default=config.get("seed"))

    return parser.parse_args()


def main():
    log_file = f"logs/run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    setup_logging(log_file=log_file)

    logging.info("Starting consensus generator")
    
    args = parse_args()

    if not args.fasta:
        raise ValueError("Path to FASTA is required")
    else:
        logging.info(f"Loading reference genome: {args.fasta}")
        reference = load_reference(args.fasta)

    if not args.vcf:
        raise ValueError("Path to FASTA is required")
    else:
        logging.info(f"Loading VCF: {args.vcf}")
        variants, samples = load_vcf(args.vcf, args.min_af, args.sample_list)


    logging.info(f"Generating consensus sequences...")
    consensus_records = generate_consensus_sequences(
        reference=reference,
        variants=variants,
        samples=samples,
        consensus_length=args.consensus_length,
        consensus_count=args.consensus_count,
        start_step=args.start_step,
        random_start=args.random_start,
        max_overlap=args.max_overlap,
        seed=args.seed,
    )

    logging.info(f"Writing output FASTA...")
    write_fasta(consensus_records, args.output)

    logging.info("Done!")


if __name__ == "__main__":
    sys.exit(main())
