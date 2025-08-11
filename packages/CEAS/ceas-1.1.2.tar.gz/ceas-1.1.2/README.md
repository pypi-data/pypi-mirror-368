# CEASp3

CEASp3 is a Python 3 port of the **Cis-regulatory Element Annotation System** (CEAS), a toolkit for annotating ChIP–seq peaks and generating signal profiles around genomic features.

## Reference

If you use CEASp3 please cite:

> H. Gene Shin, et al. ["CEAS: cis-regulatory element annotation system."](https://academic.oup.com/bioinformatics/article/25/19/2605/182052) *Bioinformatics* 25(19):2605–2606, 2009.

## Installation

1. Install the dependency:

   ```bash
   pip install -r requirements.txt
   ```

2. Install CEASp3:

   ```bash
   pip install .
   ```

   The scripts listed in [`bin/`](bin) such as `ceas`, `ceasBW`, `sitepro`, etc. will be placed on your `PATH`.

## Example usage

### Annotate ChIP peaks

Annotate a BED file of ChIP regions using a local gene table and generate enrichment profiles:

```bash
ceas -b peaks.bed -g refGene.sqlite --name my_chip
```

### Wig signal profiling

Generate average signal plots around gene bodies from a WIG track:

```bash
ceas -w treat.wig -g refGene.sqlite --name treat_profile --rel-dist 3000 --pf-res 50
```

### BigWig support

Work with bigWig signals using `ceasBW`:

```bash
ceasBW -b peaks.bed -w signal.bw -g refGene.sqlite --name chip_bw
```

### Site-centric profiling

Average enrichment around a set of regions:

```bash
sitepro -w signal.wig -b motifs.bed --span 1000 --step 20
```

For bigWig input use:

```bash
siteproBW -w signal.bw -b motifs.bed --span 1000 --step 20
```

`siteproBW` relies on the [`bx-python`](https://github.com/bxlab/bx-python)
library for BigWig access. Install it with:

```bash
pip install bx-python
```

### Gene-centered annotation only

Generate annotation without profiling:

```bash
gca -b peaks.bed -g refGene.sqlite --span 3000 --name gca_out
```

### Build genome background annotation

Pre-compute genome background tables for use with CEAS:

```bash
./build_genomeBG.sh hg38
```

Each script supports `--help` for additional options.

## License

The package is distributed under the Artistic License. See [LICENSE](LICENSE).

