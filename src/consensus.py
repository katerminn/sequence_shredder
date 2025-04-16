
def generate_consensus_sequences(reference: dict,
                                 variants: dict,
                                 samples: list,
                                 consensus_length: int,
                                 consensus_count: int,
                                 start_step: int = 1,
                                 random_start: bool = False,
                                 max_overlap: int = None,
                                 seed: int = 37) -> list:

    consensus_records = []

    for sample in samples:
        for chrom in reference:
            ref_seq = reference[chrom]
            chrom_len = len(ref_seq)

            starts = []

            if random_start:
                while len(starts) < consensus_count:
                    pos = random.randint(0, chrom_len - consensus_length)
                    if max_overlap is not None:
                        if any(abs(pos - s) < (consensus_length - max_overlap) for s in starts):
                            continue
                    starts.append(pos)
            else:
                pos = 0
                while pos + consensus_length <= chrom_len and len(starts) < consensus_count:
                    starts.append(pos)
                    pos += start_step

            for start in starts:
                end = start + consensus_length
                seq = list(ref_seq[start:end])

                for pos in range(start, end):
                    if pos in variants.get(chrom, {}) and sample in variants[chrom][pos]:
                        seq[pos - start] = variants[chrom][pos][sample]

                consensus_records.append({
                    "sample": sample,
                    "chrom": chrom,
                    "start": start,
                    "end": end,
                    "sequence": "".join(seq)
                })

    return consensus_records
