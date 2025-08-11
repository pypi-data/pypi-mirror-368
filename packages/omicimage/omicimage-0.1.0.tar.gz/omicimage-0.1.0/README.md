# omicimage

Convert sequencing alignments (SAM) — with optional CpG methylation reports — into RGBA images.

## Installation

```bash
pip install omicimage
```

## Command-line usage

**Without methylation:**
```bash
build-rgba-nomethylation sam_file.sam output_prefix [--width N] [--full-read] [--mapq N]
```

**With methylation:**
```bash
build-rgba-methylation sam_file.sam cpg_report.txt output_prefix [--width N] [--full-read] [--mapq N]
```

## Output

Creates a timestamped folder containing:
- `image.png` — RGBA representation of the data
- `readalignmentcoordinates.tsv` — per-pixel genomic metadata
- `metadata` — image dimensions

## Requirements

- Python 3.9+
- numpy, pillow, pysam, tqdm
