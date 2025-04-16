import json
import logging
from collections import defaultdict


def load_config(config_path: str = "config.json") -> dict:
    try:
        with open(config_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON config file: {config_path}")
    

def load_reference(fasta_path: str) -> dict:
    reference = {}
    current_chrom = None
    seq_lines = []

    with open(fasta_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_chrom:
                    reference[current_chrom] = "".join(seq_lines).upper()
                current_chrom = line[1:].split()[0]
                seq_lines = []
            else:
                seq_lines.append(line)
        # last chromosome
        if current_chrom:
            reference[current_chrom] = "".join(seq_lines).upper()

    return reference


def load_vcf(vcf_path: str, min_af: float = 0.05, sample_list_path: str = None):

    variants = defaultdict(lambda: defaultdict(dict))
    samples = []

    with open(vcf_path) as f:
        for line in f:
            if line.startswith("##"):
                continue  # skip header lines
            if line.startswith("#CHROM"):
                fields = line.strip().split('\t')
                samples = fields[9:]  # sample names
                if sample_list_path:
                    with open(sample_list_path) as s:
                        allowed_samples = set(line.strip() for line in s)
                    samples = [s for s in samples if s in allowed_samples]
                continue

            fields = line.strip().split('\t')
            chrom = fields[0]
            pos = int(fields[1]) - 1
            ref = fields[3]
            alt = fields[4]
            info = fields[7]
            format_keys = fields[8].split(':')

            if ',' in alt:
                continue  


            af = None
            for kv in info.split(';'):
                if kv.startswith("AF="):
                    af = float(kv.split("=")[1])
                    break

            if af is not None and af < min_af:
                continue

            sample_fields = fields[9:]
            for sample_name, sample_data in zip(samples, sample_fields):
                values = sample_data.split(':')
                sample_dict = dict(zip(format_keys, values))
                gt = sample_dict.get("GT", "")

                if '.' in gt:
                    continue

                # If ALT present in GT
                if '1' in gt.replace('|', '/').split('/'):
                    variants[chrom][pos][sample_name] = alt

    return variants, samples


def write_fasta(consensus_records: list, output_prefix: str):
    output_path = f"{output_prefix}.fa"

    with open(output_path, "w") as f:
        for record in consensus_records:
            header = f">{record['sample']}_{record['chrom']}:{record['start']}-{record['end']}"
            seq = record['sequence']

            f.write(header + "\n")

            for i in range(0, len(seq), 50):
                f.write(seq[i:i+60] + "\n")

    logging.info(f"FASTA written to: {output_path}")
