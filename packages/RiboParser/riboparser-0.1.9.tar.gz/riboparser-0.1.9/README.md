<!--
 * @Author: 'rensc' 'rensc0718@163.com'
 * @Date: 2024-10-15 11:44:58
 * @LastEditors: 'rensc' 'rensc0718@163.com'
 * @LastEditTime: 2025-02-18 03:50
 * @FilePath: \RiboParser\README.md 
 * 
-->


# RiboParser 

```
Ren, S., Li, Y. & Zhou, Z. 
RiboParser/RiboShiny: An integrated platform for comprehensive analysis and visualization of ribo-seq data. 
Journal of Genetics and Genomics (2025) 
doi:10.1016/j.jgg.2025.04.010.
```

To streamline understanding and application, we will analyze publicly accessible project data, breaking down each analytical step to illustrate the complete workflow.

This process encompasses both general analysis steps and specialized analysis and visualization techniques, facilitated by `RiboParser` and `RiboShiny`.

The specific steps involved are:

1. Software installation
2. Reference file creation
3. Raw data download
4. Raw data cleaning
5. Data alignment
6. Sequencing quality analysis
7. Gene-level analysis
8. Codon-level analysis

The results of this data analysis can be further analyzed and visualized in `RiboShiny`.



## 1. Software configuration

First, you need to install the software of `miniconda` or `micromamba`.

### 1.1 create the environment with `conda`

```bash
conda create -n ribo
conda activate ribo
```

### 1.2 Install `riboparser` and the entire environment directly via `miniconda` or `micromamba`.
```bash
# conda
conda install riboparser -c rensc

# mamba
micromamba install riboparser -c rensc

```


### 1.3 Install `riboparser` and software dependencies step by step.

Install the software dependencies.

```bash
conda install bowtie samtools cutadapt star bedtools subread rsem gffread sra-tools \
 ucsc-genepredtogtf ucsc-gtftogenepred ucsc-gff3togenepred ucsc-bedgraphtobigwig ucsc-bedsort \
 -c bioconda

conda install pigz -c conda-forge
```


`pip` install `RiboParser`

```bash
pip install riboparser
```

Alternatively, we can download the version from GitHub, re-setup and then install it.

```bash
cd RiboParser
# install the dependency
pip install build

# build the riboparser package
python -m build

# install the riboparser
pip install .

```

### 1.4 run the test
Test software for dependency, installation, and operation issues.

```bash
rpf_Check -h
rpf_CST -h
```

## 2. Prepare reference files

### 2.1 An example of the complete project directory is shown below

The complete data analysis includes reference preparation, rawdata, RNA-seq data analysis, and Ribo-seq data analysis.

```bash
$ cd && cd ./sce/
$ tree -d

.
├── 1.reference
│   ├── genome
│   ├── mrna
│   ├── ncrna
│   ├── norm
│   ├── rrna
│   ├── rsem-index
│   ├── star-index
│   └── trna
├── 2.rawdata
│   ├── ribo-seq
│   └── rna-seq
├── 3.rna-seq
│   ├── 1.cleandata
│   ├── 2.bowtie
│   ├── 3.star
│   ├── 4.quantification
│   └── 5.riboparser
│       ├── 01.qc
│       ├── 02.digestion
│       ├── 03.offset
│       ├── 04.density
│       ├── 05.merge
│       ├── 06.periodicity
│       ├── 07.metaplot
│       ├── 08.coverage
│       ├── 09.correlation
│       ├── 10.shuffle
│       └── 11.retrieve
└── 4.ribo-seq
    ├── 1.cleandata
    ├── 2.bowtie
    ├── 3.star
    ├── 4.quantification
    └── 5.riboparser
        ├── 01.qc
        ├── 02.digestion
        ├── 03.offset
        ├── 04.density
        ├── 05.merge
        ├── 06.periodicity
        ├── 07.metaplot
        ├── 08.coverage
        ├── 09.correlation
        ├── 10.quantification
        ├── 11.pausing_score
        ├── 12.codon_occupancy
        ├── 13.codon_decoding_time
        ├── 14.codon_selection_time
        ├── 15.coefficient_of_variation
        ├── 16.meta_codon
        ├── 17.shuffle
        ├── 18.retrieve
        └── 19.frame_shift
```

### 2.2 Prepare the reference genome index
#### 2.2.1 Create the directory

Create folders to hold different types of reference sequence files.

```bash
$ mkdir -p ./sce/1.reference/
$ cd ./sce/1.reference/
$ mkdir cdna genome gtf mrna ncrna rrna trna norm rsem-index
```

#### 2.2.2 Download reference files from NCBI

Use the most common data analysis file format, the genome sequence in fasta format, and the reference file in GTF or GFF3 format.

```bash
# genome sequence
$ wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/146/045/GCF_000146045.2_R64/GCF_000146045.2_R64_genomic.fna.gz

# GTF or GFF3
$ wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/146/045/GCF_000146045.2_R64/GCF_000146045.2_R64_genomic.gtf.gz
$ wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/146/045/GCF_000146045.2_R64/GCF_000146045.2_R64_genomic.gff.gz

# cDNA sequence
$ wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/146/045/GCF_000146045.2_R64/GCF_000146045.2_R64_rna.fna.gz

# feature table
$ wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/146/045/GCF_000146045.2_R64/GCF_000146045.2_R64_feature_table.txt.gz

# decompression
$ gunzip *.gz

$ gffread -g GCF_000146045.2_R64_genomic.fna GCF_000146045.2_R64_genomic.gff -F -w cdna.fa
```

#### 2.2.3 Create the `genome` index using `bowtie`

```bash
$ bowtie-build ../GCF_000146045.2_R64_genomic.fna ./genome/genome --threads 12 &>> ./genome/genome_build.log
```

#### 2.2.4 Create an `mRNA` index using `bowtie`

A custom script is used here to extract the corresponding sequence information 
from the `fasta` file based on the sequence name.

```bash
$ retrieve_seq -h

usage: retrieve_seq [-h] [-v] -i INPUT -n NAME [-u UNMAPPED] -o OUTPUT

This script is used to retrieve the fasta sequence by name.

options:
  -h, --help     show this help message and exit
  -v, --version  show programs version number and exit
  -i INPUT       input the fasta file
  -n NAME        gene ids in txt format
  -u UNMAPPED    output the unmapped gene ids
  -o OUTPUT      prefix of output file name (default results_peaks.txt)
```


```bash
# filter the mrna sequence
$ grep -i 'gbkey=mRNA' ./cdna.fa | cut -d ' ' -f 1 | cut -c 2- > ./mrna/mrna.ids
$ retrieve_seq -i ./cdna.fa -n ./mrna/mrna.ids -o ./mrna/mrna.fa &>> ./mrna/mrna_build.log
# build the mrna index
$ bowtie-build ./mrna/mrna.fa ./mrna/mrna --threads 12 &>> ./mrna/mrna_build.log
```

#### 2.2.5 Create an `rRNA` index using `bowtie`
```bash
# filter the rrna sequence
$ grep -i 'gbkey=rRNA' ./cdna.fa | cut -d ' ' -f 1 | cut -c 2- > ./rrna/rrna.ids
$ retrieve_seq -i ./cdna.fa -n ./rrna/rrna.ids -o ./rrna/rrna.fa &>> ./rrna/rrna_build.log
# build the rrna index
$ bowtie-build ./rrna/rrna.fa ./rrna/rrna --threads 12 &>> ./rrna/rrna_build.log
```

#### 2.2.6 Create an `tRNA` index using `bowtie`
```bash
# filter the trna sequence
$ grep -i 'gbkey=tRNA' ./cdna.fa | cut -d ' ' -f 1 | cut -c 2- > ./trna/trna.ids
$ retrieve_seq -i ./cdna.fa -n ./trna/trna.ids -o ./trna/trna.fa &>> ./trna/trna_build.log
# build the trna index
$ bowtie-build ./trna/trna.fa ./trna/trna --threads 12 &>> ./trna/trna_build.log
```


#### 2.2.7 Create an `ncRNA` index using `bowtie`
```bash
# filter the ncrna sequence
$ grep -iE 'gbkey=ncRNA|gbkey=lnc_RNA|gbkey=miRNA|gbkey=snoRNA|gbkey=snRNA|gbkey=misc_RNA' ./cdna.fa | cut -d ' ' -f 1 | cut -c 2- > ./ncrna/ncrna.ids
$ retrieve_seq -i ./cdna.fa -n ./ncrna/ncrna.ids -o ./ncrna/ncrna.fa &>> ./ncrna/ncrna_build.log
# build the ncrna index
$ bowtie-build ./ncrna/ncrna.fa ./ncrna/ncrna --threads 12 &>> ./ncrna/ncrna_build.log
```

#### 2.2.8 Standardized `gtf` or `gff3` files

- Explanation of `rpf_Reference` 

```bash
$ rpf_Reference -h

usage: rpf_Reference [-h] -g GENOME -t GTF -o OUTPUT [-u UTR] [-c] [-l] [-w]

This script is used to build the references for the RiboParser.

options:
  -h, --help  show this help message and exit
  -u UTR      add the pseudo UTR to the leaderless transcripts (default: 0 nt).
  -c          only retain the protein coding transcripts (default: False).
  -l          only retain the longest protein coding transcripts, it is recommended to select 
              the longest transcript for subsequent analysis. (default: False).
  -w          output whole message (default: False).

Required arguments:
  -g GENOME   the input file name of genome sequence
  -t GTF      the input file name of gtf file
  -o OUTPUT   the prefix of output file. (prefix + _norm.gtf)
```

- create the references from GTF and Genome fasta

```bash
$ rpf_Reference \
 -g ../GCF_000146045.2_R64_genomic.fna \
 -t ../GCF_000146045.2_R64_genomic.gff \
 -u 30 -o ./norm/gene &>> ./norm/norm_build.log
```

#### 2.2.9 Create a `genome` index using `STAR`

```bash
$ STAR \
 --genomeSAindexNbases 11 \
 --runThreadN 12 \
 --runMode genomeGenerate \
 --genomeDir ./star-index \
 --genomeFastaFiles GCF_000146045.2_R64_genomic.fna \
 --sjdbGTFfile ./norm/gene.norm.gtf
```

#### 2.2.10 Create a `transcriptome` index using `rsem`

```bash
$ rsem-prepare-reference \
 -p 12 \
 --gtf ../norm/gene.norm.gtf ../GCF_000146045.2_R64_genomic.fna ./rsem-index/rsem
```


## 3. Data preprocessing and alignment

In order to introduce the analysis process and usage of `RiboParser`, RNA-seq and Ribo-seq data from dataset `GSE67387` are used as examples here.

```shell
# dataset
https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE67387

# reference
Nedialkova DD, Leidel SA. Optimization of Codon Translation Rates via tRNA Modifications Maintains Proteome Integrity. Cell 2015 Jun 18;161(7):1606-18. 
PMID: 26052047
```


### 3.1 Fundamental analysis of RNA-seq data in `GSE67387` dataset

#### 3.1.1 Download RNA-seq raw data

Use `prefetch` in `sra-tools` to download the raw SRA-format data and extract it into `fastq` format files.

```bash
$ mkdir -p ./sce/2.rawdata/rna-seq/
$ cd ./sce/2.rawdata/rna-seq/

#################################################
# download rna-seq
$ prefetch -o SRR1944925.sra SRR1944925
$ prefetch -o SRR1944926.sra SRR1944926
$ prefetch -o SRR1944927.sra SRR1944927
$ prefetch -o SRR1944928.sra SRR1944928
$ prefetch -o SRR1944929.sra SRR1944929
$ prefetch -o SRR1944930.sra SRR1944930
$ prefetch -o SRR1944931.sra SRR1944931
$ prefetch -o SRR1944932.sra SRR1944932
$ prefetch -o SRR1944933.sra SRR1944933
$ prefetch -o SRR1944934.sra SRR1944934
$ prefetch -o SRR1944935.sra SRR1944935

# decompression
for sra in *.sra
do

fastq-dump $sra
pigz *fastq

done
```

#### 3.1.2 RNA-seq data cleaning

Because the data from the gse project is cleaned, it does not include adapter and index sequences. So the following is just to show the general steps, do not need to run.

1. RNA-seq data cleaning

```bash
$ cd
$ mkdir -p ./sce/3.rna-seq/1.cleandata/
$ cd ./sce/3.rna-seq/1.cleandata/

#################################################
# run the cutadapt
for fq in ../../2.rawdata/rna-seq/*fastq.gz
do
cutadapt --match-read-wildcards \
 -a AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCGGTGGTCGC \
 -m 25 -O 6 -j 12 \
 -o `\basename $fq fastq.gz`clean.fastq.gz $fq &>> $fq".log"

done
```

#### 3.1.3 Align clean data to different types of reference files

To assess library quality and eliminate the impact of reads originating from different non-coding RNAs (ncRNAs) on subsequent analysis, we employed `bowtie` to classify the reads form sequencing data.

Under normal circumstances, especially for RNA-seq libraries constructed using the oligo(dT) method, most reads originate from mRNA. Therefore, for RNA-seq analysis, this step is generally not necessary. It is suitable for use in libraries constructed by the rRNA-depletion method.

1. Align the RNA-seq data to references

```bash
$ cd
$ mkdir -p ./sce/3.rna-seq/2.bowtie/
$ cd ./sce/3.rna-seq/2.bowtie/

#################################################
# set database
rrna='../../sce/1.reference/rrna/rrna'
trna='../../sce/1.reference/trna/trna'
ncrna='../../sce/1.reference/ncrna/ncrna'
mrna='../../sce/1.reference/mrna/mrna'
chrom='../../sce/1.reference/genome/genome'

threads=12
mismatch=1

# alignment reads to reference
for fq in ../1.cleandata/*fastq.gz
do
fqname=`\basename $fq .fastq.gz`

## rrna
bowtie -p $threads -v $mismatch --un="$fqname".norrna.fq --al="$fqname".rrna.fq \
 -x $rrna $fq -S "$fqname".rrna.sam 2>> "$fqname".log

## trna
bowtie -p $threads -v $mismatch --un="$fqname".notrna.fq --al="$fqname".trna.fq \
 -x $trna "$fqname".norrna.fq -S "$fqname".trna.sam 2>> "$fqname".log

## ncrna
bowtie -p $threads -v $mismatch --un="$fqname".noncrna.fq --al="$fqname".ncrna.fq \
 -x $ncrna "$fqname".notrna.fq -S "$fqname".ncrna.sam 2>> "$fqname".log

## mrna
bowtie -p $threads -v $mismatch --un="$fqname".nomrna.fq --al="$fqname".mrna.fq \
 -x $mrna "$fqname".noncrna.fq -S "$fqname".mrna.sam 2>> "$fqname".log

## genome
bowtie -p $threads -v $mismatch --un="$fqname".nogenome.fq --al="$fqname".genome.fq \
 -x $chrom "$fqname".nomrna.fq -S "$fqname".genome.sam 2>> "$fqname".log

## compress fastq
pigz *fq

## compress sam
for sam in *.sam
do

samtools view -h -F 4 $sam | samtools sort -@ $threads -o `\basename $sam sam`bam
rm $sam

done

done
```


2. Statistical alignment results for all references.

- Explanation of `merge_bwt_log`

```bash
$ merge_bwt_log -h

Step1: Checking the input Arguments.
usage: merge_bwt_log [-h] -l LIST [LIST ...] -o OUTPUT [-n NAME]

This script is used to statstic the mapped reads from log files

options:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  set the name of each database (default: rRNA,tRNA,ncRNA,mRNA,Genome).

Required arguments:
  -l LIST [LIST ...], --list LIST [LIST ...]
                        List for bowtie mapping log files (e.g., '*log').
  -o OUTPUT             prefix of output file name.
```

- Statistical alignment results

```bash
#################################################
# merge all log files
merge_bwt_log -n rRNA,tRNA,ncRNA,mRNA,Genome -l *log -o RNA_seq &>> merge_bowtie.log
```

#### 3.1.4 Aligning mRNA reads using `STAR`

Following the removal of ncRNA reads, the remaining clean reads were realigned to the yeast genome using `STAR`.

1. Aligning mRNA reads (RNA-seq) using `STAR`
```bash
$ cd
$ mkdir -p ./sce/3.rna-seq/3.star/
$ cd ./sce/3.rna-seq/3.star/

#################################################
# set the option and database
genome='../../1.reference/star-index/'
threads=12

#################################################
# map the all rna-seq reads to genome and transcriptome region
for fastq in ../2.bowtie/*.noncrna.fq.gz
do

## get file name
output=$(basename $fastq .noncrna.fq.gz)

#################################################
## run the alignment
STAR --runThreadN $threads \
 --readFilesCommand zcat \
 --genomeDir $genome \
 --readFilesIn $fastq \
 --outFileNamePrefix $output \
 --outSAMtype BAM Unsorted \
 --outFilterType BySJout \
 --quantMode TranscriptomeSAM GeneCounts \
 --outReadsUnmapped Fastx \
 --outSAMattributes All \
 --alignEndsType Local \
 --outFilterMultimapNmax 3 \
 --outFilterMismatchNmax 1 \
 --alignIntronMax 10000 \
 --outFilterMatchNmin 20
# --outWigType wiggle --outWigNorm RPM

pigz *mate1

#################################################
## sort the bam file
samtools sort -@ $threads $output"Aligned.out.bam" -o $output"Aligned.sortedByCoord.out.bam"
samtools index -@ $threads $output"Aligned.sortedByCoord.out.bam"
rm $output"Aligned.out.bam"

done
```

#### 3.1.5 Estimating gene expression levels with either `RSEM` or `featureCounts`

Both `RSEM` and `featureCounts` can be employed to quantify gene expression levels. For the purpose of this analysis, we will utilize `RSEM` as a representative tool.

1. Estimating transcript abundance using RNA-seq data

```bash
$ cd
$ mkdir -p ./sce/3.rna-seq/4.quantification/
$ cd ./sce/3.rna-seq/4.quantification/

#################################################
# quantify the gene expression
for bam in ../3.star/*Aligned.toTranscriptome.out.bam
do
rsem-calculate-expression -p 10 \
 --no-bam-output --alignments \
 -q $bam ../../1.reference/rsem-index/rsem `\basename $bam Aligned.toTranscriptome.out.bam`
# rsem-calculate-expression -p 10 \
# --paired-end --no-bam-output --alignments \
# -q $bam ../../1.reference/rsem-index/rsem `\basename $bam Aligned.toTranscriptome.out.bam`

done
```

2. Integrating RNA-seq quantification values for all samples

- Explanation of `merge_rsem`

```bash
$ merge_rsem -h

usage: merge_rsem [-h] -l LIST [LIST ...] -o OUTPUT [-c {expected_count,TPM,FPKM}]

This script is used to merge specified columns from result files

options:
  -h, --help            show this help message and exit
  -c {expected_count,TPM,FPKM}, --column {expected_count,TPM,FPKM}
                        Column name to merge (e.g., 'expected_count').

Required arguments:
  -l LIST [LIST ...], --list LIST [LIST ...]
                        List for result files (e.g., '*results').
  -o OUTPUT             output file name.
```

- Integrating RNA-seq quantification values

```bash
#################################################
# merge the gene expression
merge_rsem -c expected_count -l *.genes.results -o gene.expected_count.txt &>> merge_rsem.log
merge_rsem -c TPM -l *.genes.results -o gene.TPM.txt &>> merge_rsem.log
merge_rsem -c FPKM -l *.genes.results -o gene.FPKM.txt &>> merge_rsem.log

#################################################
# merge the isoforms expression
merge_rsem -c expected_count -l *.isoforms.results -o isoforms.expected_count.txt &>> merge_rsem.log
merge_rsem -c TPM -l *.isoforms.results -o isoforms.TPM.txt &>> merge_rsem.log
merge_rsem -c FPKM -l *.isoforms.results -o isoforms.FPKM.txt &>> merge_rsem.log
```


### 3.2 Fundamental analysis of Ribo-seq data in `GSE67387` dataset

#### 3.2.1 Download Ribo-seq raw data

Use `prefetch` in `sra-tools` to download the raw SRA-format data and extract it into `fastq` format files.

```bash
$ cd
$ mkdir -p ./sce/2.rawdata/ribo-seq/
$ cd ./sce/2.rawdata/ribo-seq/

#################################################
# download ribo-seq
prefetch -o SRR1944912.sra SRR1944912
prefetch -o SRR1944913.sra SRR1944913
prefetch -o SRR1944914.sra SRR1944914
prefetch -o SRR1944915.sra SRR1944915
prefetch -o SRR1944916.sra SRR1944916
prefetch -o SRR1944917.sra SRR1944917
prefetch -o SRR1944918.sra SRR1944918
prefetch -o SRR1944919.sra SRR1944919
prefetch -o SRR1944920.sra SRR1944920
prefetch -o SRR1944921.sra SRR1944921
prefetch -o SRR1944922.sra SRR1944922
prefetch -o SRR1944923.sra SRR1944923

# decompression
for sra in *.sra
do

fastq-dump $sra
pigz *fastq

done
```

#### 3.2.2 Ribo-seq data cleaning

```bash
$ cd
$ mkdir -p ./sce/4.ribo-seq/1.cleandata/
$ cd ./sce/4.ribo-seq/1.cleandata/

#################################################
# run the cutadapt
for fq in ../../2.rawdata/ribo-seq/*fastq.gz
do
cutadapt --match-read-wildcards \
 -a AAAAAAAA \
 -m 25 -O 6 -j 10 \
 -o `\basename $fq fastq.gz`clean.fastq.gz $fq &>> $fq".log"
done
```


#### 3.2.3 Align clean data to different types of reference files

To assess library quality and eliminate the impact of reads originating from different non-coding RNAs (ncRNAs) on subsequent analysis, we employed `bowtie` to classify the reads form sequencing data.

1. Aligning Ribo-seq data
```bash
$ cd
$ mkdir -p ./sce/4.ribo-seq/2.bowtie/
$ cd ./sce/4.ribo-seq/2.bowtie/

#################################################
# set database
rrna='../../sce/1.reference/rrna/rrna'
trna='../../sce/1.reference/trna/trna'
ncrna='../../sce/1.reference/ncrna/ncrna'
mrna='../../sce/1.reference/mrna/mrna'
chrom='../../sce/1.reference/genome/genome'

threads=12
mismatch=1

# alignment reads to reference
for fq in ../1.cleandata/*fastq.gz
do
fqname=`\basename $fq .fastq.gz`

## rrna
bowtie -p $threads -v $mismatch --un="$fqname".norrna.fq --al="$fqname".rrna.fq \
 -x $rrna $fq -S "$fqname".rrna.sam 2>> "$fqname".log

## trna
bowtie -p $threads -v $mismatch --un="$fqname".notrna.fq --al="$fqname".trna.fq \
 -x $trna "$fqname".norrna.fq -S "$fqname".trna.sam 2>> "$fqname".log

## ncrna
bowtie -p $threads -v $mismatch --un="$fqname".noncrna.fq --al="$fqname".ncrna.fq \
 -x $ncrna "$fqname".notrna.fq -S "$fqname".ncrna.sam 2>> "$fqname".log

## mrna
bowtie -p $threads -v $mismatch --un="$fqname".nomrna.fq --al="$fqname".mrna.fq \
 -x $mrna "$fqname".noncrna.fq -S "$fqname".mrna.sam 2>> "$fqname".log

## genome
bowtie -p $threads -v $mismatch --un="$fqname".nogenome.fq --al="$fqname".genome.fq \
 -x $chrom "$fqname".nomrna.fq -S "$fqname".genome.sam 2>> "$fqname".log

## compress fastq
pigz *fq

## compress sam
for sam in *.sam
do

samtools view -h -F 4 $sam | samtools sort -@ $threads -o `\basename $sam sam`bam
rm $sam

done

done
```

2. Statistical alignment results for all databases.
```bash
#################################################
# merge all log files
merge_bwt_log -n rRNA,tRNA,ncRNA,mRNA,Genome -l *log -o sce &>> merge_bowtie.log
```


#### 3.2.4 Aligning mRNA reads (Ribo-seq) using `STAR`

Following the removal of ncRNA reads, the remaining clean reads were realigned to the yeast genome using `STAR`.

```bash
$ cd
$ mkdir -p ./sce/4.ribo-seq/3.star/
$ cd ./sce/4.ribo-seq/3.star/

#################################################
# set the option and database
genome='../../1.reference/star-index/'
threads=12

#################################################
# map the all rna-seq reads to genome and transcriptome region
for fastq in ../2.bowtie/*.noncrna.fq.gz
do

## get file name
output=$(basename $fastq .noncrna.fq.gz)

#################################################
## run the alignment
STAR --runThreadN $threads \
 --readFilesCommand zcat \
 --genomeDir $genome \
 --readFilesIn $fastq \
 --outFileNamePrefix $output \
 --outSAMtype BAM Unsorted \
 --outFilterType BySJout \
 --quantMode TranscriptomeSAM GeneCounts \
 --outReadsUnmapped Fastx \
 --outSAMattributes All \
 --alignEndsType Local \
 --outFilterMultimapNmax 3 \
 --outFilterMismatchNmax 1 \
 --alignIntronMax 10000 \
 --outFilterMatchNmin 20
# --outWigType wiggle --outWigNorm RPM

pigz *mate1

#################################################
## sort the bam file
samtools sort -@ $threads $output"Aligned.out.bam" -o $output"Aligned.sortedByCoord.out.bam"
samtools index -@ $threads $output"Aligned.sortedByCoord.out.bam"
rm $output"Aligned.out.bam"

done
```


#### 3.2.5 Estimating gene expression levels with either `RSEM` or `featureCounts`

Both `RSEM` and `featureCounts` can be employed to quantify gene expression levels. For the purpose of this analysis, we will utilize `RSEM` as a representative tool.

1. Estimating transcript abundance using Ribo-seq data

```bash
$ cd
$ mkdir -p ./sce/4.ribo-seq/4.quantification/
$ cd ./sce/4.ribo-seq/4.quantification/

#################################################
# quantify the isoforms expression
for bam in ../3.star/*Aligned.toTranscriptome.out.bam
do

rsem-calculate-expression -p 12 \
 --no-bam-output --alignments \
 -q $bam ../../1.reference/rsem-index/rsem `\basename $bam Aligned.toTranscriptome.out.bam`

done
```

2. Integrating Ribo-seq quantification values for all samples

```bash
#################################################
# merge the gene expression
merge_rsem -c expected_count -l *.genes.results -o gene.expected_count.txt &>> merge_rsem.log
merge_rsem -c TPM -l *.genes.results -o gene.TPM.txt &>> merge_rsem.log
merge_rsem -c FPKM -l *.genes.results -o gene.FPKM.txt &>> merge_rsem.log

#################################################
# merge the isoforms expression
merge_rsem -c expected_count -l *.isoforms.results -o isoforms.expected_count.txt &>> merge_rsem.log
merge_rsem -c TPM -l *.isoforms.results -o isoforms.TPM.txt &>> merge_rsem.log
merge_rsem -c FPKM -l *.isoforms.results -o isoforms.FPKM.txt &>> merge_rsem.log
```


## 4. Perform RNA-seq data analysis of `GSE67387` with `RiboParser`

### 4.0 Prepare the directory to store the results

```bash
$ cd
$ mkdir -p ./3.rna-seq/5.riboparser/
$ cd ./3.rna-seq/5.riboparser/
$ mkdir 01.qc 02.digestion 03.offset 04.density 05.merge \
 06.periodicity 07.metaplot 08.coverage 09.correlation 10.shuffle
```

### 4.1 Quality check of sequencing data

1. Quality check of RNA-seq data

```bash
$ cd ./01.qc

#################################################
# check the ribo-seq quality
for bam in ../../3.star/*Aligned.toTranscriptome.out.bam
do
prefix_name=$(basename $bam Aligned.toTranscriptome.out.bam)

rpf_Check -b $bam -s --thread 10 \
 -t ../../../1.reference/norm/gene.norm.txt \
 -o $prefix_name &>> $prefix_name".log"

done
```

2. Integrating RNA-seq quality check results for all samples
```bash

#################################################
# merge the rna-seq quality results
merge_length -l *length_distribution.txt -o sce
merge_saturation -l *gene_saturation.txt -o sce

cd ..
```

### 4.2 Enzymatic bias in NGS library preparation
1. Bias in restriction enzyme digestion and ligation in sequencing data

```bash
$ cd ./02.digestion/

#################################################
# check the reads digestion
for bam in ../01.qc/*.bam
do
prefix_name=$(basename $bam .bam)

rpf_Digest -b $bam -m 25 -M 50 --scale \
 -s ../../../1.reference/norm/gene.norm.rna.fa \
 -t ../../../1.reference/norm/gene.norm.txt \
 -o $prefix_name &>> $prefix_name".log"

done
```

2. Integrating reads digestion results for all samples

```bash
#################################################
# merge the rpf digestion
merge_digestion -l ./02.digestion/*pwm.txt -o sce

cd ..
```

### 4.3 Use `RiboParser` to create the `offset` table

1. Create the `offset` table for RNA-seq

`Offset` prediction is unnecessary for RNA-seq analysis. A constant `offset` of 12 can be assigned to all entries in the table.

```bash
$ cd ./03.offset/

#################################################
# set the offset table
for bam in ../01.qc/*.bam
do

prefix_name=$(basename $bam .bam)
rna_Offset -m 27 -M 50 -e 12 -o $prefix_name &>> $prefix_name".log"

done
```

### 4.4 Convert the `BAM` file to reads density

Transform the read counts in a `BAM` file into density values and save them in a `TXT` format file.

1. Transform RNA-seq data output

```bash
$ cd ./04.density/

#################################################
# convert the reads to density
for bam in ../01.qc/*.bam
do
prefix_name=$(basename $bam .bam)

rna_Density -b $bam -m 27 -M 33 -l --thread 10 \
 -p ../03.offset/$prefix_name"_offset.txt" \
 -s ../../../1.reference/norm/gene.norm.rna.fa \
 -t ../../../1.reference/norm/gene.norm.txt \
 -o $prefix_name &>> $prefix_name".log"

done

cd ..
```


### 4.5 Integrating density file for all samples

Data from various batches and samples can be integrated for unified analysis. If not integrated, individual analysis for each sample is required, increasing the number of operational steps.

1. Integrating RNA-seq density results for all samples
```bash
$ cd ./05.merge/

#################################################
# create the samples file: RNA.file.list
merge_dst_list -l ../04.density/*_rna.txt -o RNA.file.list

cat RNA.file.list

Name File  Type
wt_rna_YPD1 /home/sce/3.rna-seq/5.riboparser/04.density/SRR1944924_rna.txt RNA
wt_rna_YPD2 /home/sce/3.rna-seq/5.riboparser/04.density/SRR1944925_rna.txt RNA
wt_rna_YPD3 /home/sce/3.rna-seq/5.riboparser/04.density/SRR1944926_rna.txt RNA
ncs2d_rna_YPD1  /home/sce/3.rna-seq/5.riboparser/04.density/SRR1944927rna.txt RNA
ncs2d_rna_YPD2  /home/sce/3.rna-seq/5.riboparser/04.density/SRR1944928_rna.txt RNA
ncs2d_rna_YPD3  /home/sce/3.rna-seq/5.riboparser/04.density/SRR1944929_rna.txt RNA
elp6d_rna_YPD1  /home/sce/3.rna-seq/5.riboparser/04.density/SRR1944930_rna.txt RNA
elp6d_rna_YPD2  /home/sce/3.rna-seq/5.riboparser/04.density/SRR1944931_rna.txt RNA
elp6d_rna_YPD3  /home/sce/3.rna-seq/5.riboparser/04.density/SRR1944932_rna.txt RNA
ncs2d_elp6d_rna_YPD1  /home/sce/3.rna-seq/5.riboparser/04.density/SRR1944933_rna.txt RNA
ncs2d_elp6d_rna_YPD2  /home/sce/3.rna-seq/5.riboparser/04.density/SRR1944934_rna.txt RNA
ncs2d_elp6d_rna_YPD3  /home/sce/3.rna-seq/5.riboparser/04.density/SRR1944935_rna.txt RNA

#################################################
# merge all the RNA-seq files
rpf_Merge -l RNA.file.list -o RNA &>> RNA.log

cd ..
```

### 4.6 Calculate tri-nucleotide periodicity

1. Check the tri-nucleotide periodicity of RNA-seq
```bash
$ cd ./06.periodicity/

#################################################
# check the periodicity
rpf_Periodicity \
 -r ../05.merge/RNA_merged.txt \
 -m 30 --tis 0 --tts 0 -o RNA &>> RNA.log
```

### 4.7 `Meta-gene` analysis

Investigation of reads density in the vicinity of start and stop codons using `meta-gene` analysis.

1. `Meta-gene` analysis of RNA-seq

```bash
$ cd ./07.metaplot/

#################################################
# metagene analysis
rpf_Metaplot \
 -t ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RNA_merged.txt \
 -m 50 --mode bar -o RNA &>> RNA.log
```

### 4.8 Gene coverage

Examine the distribution of read density along the gene body.

1. Check gene density of RNA-seq

```bash
$ cd ./08.coverage/

#################################################
# check the reads density along with the gene body
rpf_Coverage \
 -t ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RNA_merged.txt \
 -m 50 --outlier \
 -b 10,100,10 \
 -n --heat \
 -o RNA &>> RNA.log

rpf_Percent \
 -t ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RNA_merged.txt \
 -n -m 50 \
 -f 0 \
 -o RNA &>> RNA.log
```

### 4.9 Check the repeatability of samples

1. Check the repeatability of RNA-seq

```bash
$ cd ./09.correlation/

#################################################
# calculate the samples replication of RNA-seq
rpf_Corr \
 -r ../05.merge/RNA_merged.txt \
 -o RNA &>> RNA.log
```


## 5. Perform Ribo-seq data analysis of `GSE67387` with `RiboParser`

### 5.0 Prepare the directory to store the results

```bash
$ cd
$ mkdir -p ./4.ribo-seq/5.riboparser/
$ cd ./4.ribo-seq/5.riboparser/
$ mkdir 01.qc 02.digestion 03.offset 04.density 05.merge \
 06.periodicity 07.metaplot 08.coverage 09.correlation 10.quantification \
 11.pausing_score 12.codon_occupancy 13.codon_decoding_time 14.codon_selection_time \
 15.coefficient_of_variation 16.meta_codon 17.shuffle 18.retrieve
```

### 5.1 Quality check of sequencing data

To ensure the reliability of downstream analyses, rigorous quality control (QC) of ribosome profiling data must include systematic evaluation of peak detection and gene detection rate.

`Peak Detection`:\
Calculate the dominant RPF length (expected range: 26–34 nt) and its proportion within the total reads (QC pass threshold: ≥70% in expected range).

`Gene Detection Rate`:\
Sampling from 5% to 95% of the data, the number of covered genes and their expression levels are calculated. When the slope of the gene count curve approaches 0, it typically indicates that the sequencing data is near saturation.

1. Explanation of `rpf_Check`

```bash
$ rpf_Check -h

Check the RPFs mapping condition.

Step1: Checking the input Arguments.

usage: rpf_Check [-h] -t TRANSCRIPT -b BAM -o OUTPUT [--thread THREAD] [-g {0,1}] [-a {star,hisat2,bowtie2}] [-r] [-l] [-s]

This script is used to summary the BAM condition.

options:
  -h, --help            show this help message and exit.
  --thread THREAD       the number of threads (default: 1). Suitable for large bam files > 1G.
                        It will take a lot of memory.
  -g {0,1}              filter the number of reads mapped loci (default: 0). [0]: all reads will be
                        used; [1]: reads with unique mapped loci will be used
  -a {star,hisat2,bowtie2}
                        screen the reads mapped loci from BAM file generate with different reads alignment methods (default: star).
  -r                    reads aligned to negative strand will also be counted. (default: False).
  -l                    only keep the longest transcripts (default: False).
  -s                    whether to calculate RPF saturation. (default: False). This step will take 
                        a lot of time and memory.

Required arguments:
  -t TRANSCRIPT         the input file name of gene annotation.
  -b BAM                the input file name of bam.
  -o OUTPUT             the prefix of output file.
```

2. Quality check of ribo-seq data

```bash
$ cd ./01.qc/

#################################################
# check the ribo-seq quality
for bam in ../../3.star/*Aligned.toTranscriptome.out.bam
do
prefix_name=$(basename $bam Aligned.toTranscriptome.out.bam)

rpf_Check -b $bam -s --thread 10 \
 -t ../../../1.reference/norm/gene.norm.txt \
 -o $prefix_name &>> $prefix_name".log"

done
```

3.  Results of `rpf_Check`

```bash
# results of sample SRR1944912
SRR1944912.bam # Filtered and sorted BAM file
SRR1944912.bam.bai # Index file for the BAM file
SRR1944912_gene_saturation.pdf # Barplot for gene saturation analysis
SRR1944912_gene_saturation.png # Barplot for gene saturation analysis
SRR1944912_gene_saturation.txt # Statistical results of gene saturation analysis
SRR1944912_length_distribution.pdf # Line graph of reads length distribution
SRR1944912_length_distribution.png # Line graph of reads length distribution
SRR1944912_length_distribution.txt # Statistical results of reads length distribution
SRR1944912.log # Log file of program execution
SRR1944912_reads_saturation.pdf # Boxplot for reads saturation analysis
SRR1944912_reads_saturation.png # Boxplot for reads saturation analysis
SRR1944912_reads_saturation.txt # Statistical results of reads saturation analysis
```


4. Explanation of `merge_length` and `merge_saturation`

```bash
Step1: Checking the input Arguments.
usage: merge_length [-h] -l LIST [LIST ...] -o OUTPUT

This script is used to merge the length distribution files

options:
  -h, --help            show this help message and exit

Required arguments:
  -l LIST [LIST ...], --list LIST [LIST ...]
                        List for length distribution files (e.g., '*length_distribution.txt').
  -o OUTPUT             prefix of output file name.
```

5. Integrating Ribo-seq quality check results for all samples

```bash
#################################################
# merge the ribo-seq quality results
merge_length -l *length_distribution.txt -o RIBO
merge_saturation -l *gene_saturation.txt -o RIBO

cd ..
```


### 5.2 Enzymatic bias in NGS library preparation

Ribonuclease digestion and ligation steps in Ribo-seq can introduce biases that affect the representation of RNA fragments.

`Ribonuclease Digestion Bias`:\
Ribonucleases may preferentially cleave certain RNA sequences or structures, leading to uneven fragmentation and skewed representation of RNA species in the data.

`Ligation Bias`:\
Ligation efficiency can vary by sequence context, RNA fragment length, or secondary structure.   This may result in overrepresentation of certain fragments due to more favorable ligation sites.

To reduce these biases, it's important to analyze digestion and ligation efficiency, optimize protocols, and include controls to ensure data accuracy and reliability.

1. Explanation of `rpf_Digest`

```bash
$ rpf_Digest -h

Step1: Checking the input Arguments.

usage: rpf_Digest [-h] -t TRANSCRIPT -s SEQUENCE -b BAM -o OUTPUT [-l] [--scale] [-m MIN] [-M MAX]

This script is used to Detect the digestion sites.

options:
  -h, --help     show this help message and exit
  -l             only retain the transcript with longest CDS of each gene (default: False).Recommended : True
  --scale        scale the motif matrix (default: False).
  -m MIN         the minimum reads length to keep (default: 20 nt).
  -M MAX         the maximum reads length to keep (default: 100 nt).

Required arguments:
  -t TRANSCRIPT  the name of input transcript file in TXT format.
  -s SEQUENCE    the name of input transcript sequence file in FA format.
  -b BAM         the name of mapping file in BAM format.
  -o OUTPUT      the name of output file. (prefix + _digestion_sites.txt)
```

2. Bias in restriction enzyme digestion and ligation in sequencing data

```bash
$ cd ./02.digestion/

#################################################
# check the reads digestion
for bam in ../01.qc/*.bam
do
prefix_name=$(basename $bam .bam)

rpf_Digest -b $bam -m 27 -M 33 --scale \
 -s ../../../1.reference/norm/gene.norm.rna.fa \
 -t ../../../1.reference/norm/gene.norm.txt \
 -o $prefix_name &>> $prefix_name".log"

done
```

3. Results of `rpf_Digest`

```bash
# results of SRR1944912
SRR1944912_3end_counts.txt # Statistical values of different bases at the 3'-end of reads
SRR1944912_3end_pwm.txt # PWM matrix of bases at the 3'-end of reads
SRR1944912_3end_seqlogo2.pdf # Seqlogo of bases at the 3'-end of reads
SRR1944912_5end_counts.txt # Statistical values of different bases at the 5'-end of reads
SRR1944912_5end_pwm.txt # PWM matrix of bases at the 5'-end of reads
SRR1944912_5end_seqlogo2.pdf # Seqlogo of bases at the 5'-end of reads
SRR1944912_digestion_sites.txt # Open reading frame aligned at the ends of reads
SRR1944912.log # Log file of program execution
SRR1944912_scaled_digestion_sites_plot.pdf # Heatmap of open reading frame aligned at the ends of reads
```


4. Explanation of `merge_digestion`

```bash
$ merge_digestion -h

Step1: Checking the input Arguments.
usage: merge_digestion [-h] -l LIST [LIST ...] -o OUTPUT

This script is used to merge the reads digestion files

options:
  -h, --help            show this help message and exit

Required arguments:
  -l LIST [LIST ...], --list LIST [LIST ...]
                        List for digestion files (e.g., '*_5end_pwm.txt').
  -o OUTPUT             prefix of output file name.
```

5. Integrating reads digestion results for all samples
```bash
#################################################
# merge the rpf digestion
merge_digestion -l *pwm.txt -o RIBO

cd ..
```


### 5.3 Use `RiboParser` to predict the optimal offset

The ability of Ribo-seq to analyze translation at codon resolution relies on accurately identifying the codons located at ribosomal `A-`, `P-`, and `E-`sites for each RPF.
The offset represents the distance of the 5’ end of the RPF to the first nucleotide of the `P-site` codon. 
Two commonly used methods are the ribosome structure-based model (`RSBM`) and the start/stop-based model (`SSCBM`).

1. Explanation of `rpf_Offset`

```bash
$ rpf_Offset -h

Step1: Checking the input Arguments.

usage: rpf_Offset [-h] -t TRANSCRIPT -b BAM -o OUTPUT [--mode {SSCBM,RSBM}] [-a {both,tis,tts}] [-l] [-m MIN] [-M MAX] [-p EXP_PEAK] [-s SHIFT] [--silence] [-d]

This script is used to detect the P-site offset.

options:
  -h, --help           show this help message and exit
  --mode {SSCBM,RSBM}  specify the mode of offset detect [SSCBM, RSBM]. (default: SSCBM).
  -a {both,tis,tts}    specify the alignment of reads for offset detect [both, tis, tts]. (default: both).
  -l                   only retain the transcript with longest CDS of each gene (default: False).
  -m MIN               the minimum reads length to keep (default: 27 nt).
  -M MAX               the maximum reads length to keep (default: 33 nt).
  -p EXP_PEAK          expected RPFs length fitted to ribosome structure [~30 nt] (default: 30 nt).
  -s SHIFT             psite shift for different RPFs length. (default: 2 nt).
  --silence            discard the warning information. (default: True).
  -d                   output the details of offset (default: False).

Required arguments:
  -t TRANSCRIPT        the name of input transcript filein TXT format.
  -b BAM               the name of mapping file in BAM format.
  -o OUTPUT            the prefix of output file. (prefix + _offset.txt)
```

2. Predict the optimal offset of Ribo-seq

```bash
$ cd ../03.offset/

#################################################
# predict the offset table
for bam in ../01.qc/*.bam
do
prefix_name=$(basename $bam .bam)

rpf_Offset -b $bam -m 27 -M 33 -p 30 -d \
 -t ../../../1.reference/norm/gene.norm.txt \
 -o $prefix_name &>> $prefix_name".log"

# rpf_RSBM_Offset

done
```

3. Results of `rpf_Offset`

```bash
# results of SRR1944912
SRR1944912.log # Log file of program execution
SRR1944912_RSBM_offset.pdf # Heatmap of RSBM model calculation results
SRR1944912_RSBM_offset.png # Heatmap of RSBM model calculation results
SRR1944912_RSBM_offset.txt # Calculation results of the RSBM model
SRR1944912_SSCBM_offset.pdf # Heatmap of SSCBM model calculation results
SRR1944912_SSCBM_offset.png # Heatmap of SSCBM model calculation results
SRR1944912_SSCBM_offset_scale.pdf # Row-normalized heatmap of SSCBM model calculation results
SRR1944912_SSCBM_offset_scale.png # Row-normalized heatmap of SSCBM model calculation results
SRR1944912_SSCBM_offset.txt # Calculation results of the SSCBM model
SRR1944912_tis_3end.txt # Distribution statistics of reads 3'-end at the start codon
SRR1944912_tis_5end.txt # Distribution statistics of reads 5'-end at the start codon
SRR1944912_tts_3end.txt # Distribution statistics of reads 3'-end at the stop codon
SRR1944912_tts_5end.txt # Distribution statistics of reads 5'-end at the stop codon
```

4. Explanation of `merge_offset`

```bash
$ merge_offset -h

Step1: Checking the input Arguments.
usage: merge_offset [-h] -l LIST [LIST ...] -o OUTPUT

This script is used to merge the reads offset files

options:
  -h, --help            show this help message and exit

Required arguments:
  -l LIST [LIST ...], --list LIST [LIST ...]
                        List for RSBM/SSCBM offset files (e.g., '*RSBM_offset.txt').
  -o OUTPUT             prefix of output file name (default: prefix + _offset.txt).
```

5. Integrating offset table results for all samples

```bash
#################################################
# merge the ribo-seq offset results
merge_offset_detail -l *end.txt -o RIBO
merge_offset -l *SSCBM_offset.txt -o RIBO_SSCBM
merge_offset -l *RSBM_offset.txt -o RIBO_RSBM

cd ..
```


### 5.4 Convert the `BAM` file to reads density

Transform the read counts in a `BAM` file into density values and save them in a `TXT` format file.

1. Explanation of `rpf_Density`

```bash
$ rpf_Density -h

Convert reads to RPFs density.

Step1: Checking the input Arguments.

usage: rpf_Density [-h] -t TRANSCRIPT -s SEQUENCE -b BAM -p PSITE -o OUTPUT [-l] [-m MIN] [-M MAX] [--period PERIODICITY] [--silence] [--thread THREAD]

This script is used to convert Ribo-seq bam to p-site density.

options:
  -h, --help            show this help message and exit
  -l                    only retain the transcript with longest CDS of each gene (default: False).Recommended : True
  -m MIN                the minimum reads length to keep (default: 27 nt).
  -M MAX                the maximum reads length to keep (default: 33 nt).
  --silence             discard the warning information. (default: True).
  --thread THREAD       the number of threads (default: 1). It will take a lot of memory.

Required arguments:
  -t TRANSCRIPT         the name of input transcript file in TXT format.
  -s SEQUENCE           the name of input transcript sequence file in FA format.
  -b BAM                the name of mapping file in BAM format.
  -p PSITE              the name of p-site offset file in TXT format.
  -o OUTPUT             the prefix of output file. (output = prefix + _rpf.txt)
  --period PERIODICITY  the minimum 3nt periodicity to keep. (default: 40).
```

2. Transform Ribo-seq data output

```bash
#################################################
# convert the rpf to density
for bam in ../01.qc/*.bam
do
prefix_name=$(basename $bam .bam)

rpf_Density -b $bam -m 27 -M 33 --period 40 -l --thread 12 \
 -p ../03.offset/$prefix_name"_SSCBM_offset.txt" \
 -s ../../../1.reference/norm/gene.norm.rna.fa \
 -t ../../../1.reference/norm/gene.norm.txt \
 -o $prefix_name &>> $prefix_name".log"

done

cd ..
```

3. Results of `rpf_Density`

```bash
# results of SRR1944912
SRR1944912.log # Log file of program execution
SRR1944912_rpf.txt # File contains RPFs density on each gene
```


### 5.5 Integrating density file for all samples

Data from various batches and samples can be integrated for unified analysis. If not integrated, individual analysis for each sample is required, increasing the number of operational steps.

1. Explanation of `merge_dst_list`

```bash
$ merge_dst_list -h

Step1: Checking the input Arguments.
usage: merge_dst_list [-h] -l LIST [LIST ...] [-o OUTPUT]

This script is used to create the list of density files

options:
  -h, --help            show this help message and exit

Required arguments:
  -l LIST [LIST ...], --list LIST [LIST ...]
                        List for density files (e.g., '*_rpf.txt').
  -o OUTPUT             output file name (default: RIBO.file.list).
```

2. create the samples list

```bash
$ cd ./05.merge/

#################################################
# create the samples file: Ribo.file.list
merge_dst_list -l ../04.density/*_rpf.txt -o RIBO.file.list

cat RIBO.file.list

Name File  Type
wt_ribo_YPD1	/home/sce/4.ribo-seq/5.riboparser/04.density/SRR1944912_rpf.txt Ribo
wt_ribo_YPD2	/home/sce/4.ribo-seq/5.riboparser/04.density/SRR1944913_rpf.txt Ribo
wt_ribo_YPD3	/home/sce/4.ribo-seq/5.riboparser/04.density/SRR1944914_rpf.txt Ribo
ncs2d_ribo_YPD1	/home/sce/4.ribo-seq/5.riboparser/04.density/SRR1944915_rpf.txt Ribo
ncs2d_ribo_YPD2	/home/sce/4.ribo-seq/5.riboparser/04.density/SRR1944916_rpf.txt Ribo
ncs2d_ribo_YPD3	/home/sce/4.ribo-seq/5.riboparser/04.density/SRR1944917_rpf.txt Ribo
elp6d_ribo_YPD1	/home/sce/4.ribo-seq/5.riboparser/04.density/SRR1944918_rpf.txt Ribo
elp6d_ribo_YPD2	/home/sce/4.ribo-seq/5.riboparser/04.density/SRR1944919_rpf.txt Ribo
elp6d_ribo_YPD3	/home/sce/4.ribo-seq/5.riboparser/04.density/SRR1944920_rpf.txt Ribo
ncs2d_elp6d_ribo_YPD1	/home/sce/4.ribo-seq/5.riboparser/04.density/SRR1944921_rpf.txt Ribo
ncs2d_elp6d_ribo_YPD2	/home/sce/4.ribo-seq/5.riboparser/04.density/SRR1944922_rpf.txt Ribo
ncs2d_elp6d_ribo_YPD3	/home/sce/4.ribo-seq/5.riboparser/04.density/SRR1944923_rpf.txt Ribo
```

3. Explanation of `rpf_Merge`

```bash
$ rpf_Merge -h

Merge RPFs files from different samples.

Step1: Checking the input Arguments.
usage: rpf_Merge [-h] -l LIST -o OUTPUT

This script is used to merge the density file.

options:
  -h, --help  show this help message and exit

Required arguments:
  -l LIST     the sample list in TXT format.
  -o OUTPUT   the prefix of output file. (prefix + _merged.txt)
```


4. Integrating Ribo-seq density results for all samples

```bash
#################################################
# merge all the Ribo-seq files
rpf_Merge -l RIBO.file.list -o RIBO &>> RIBO.log

cd ..
```

5. Results of `rpf_Merge`

```bash
RIBO.log # Log file of program execution
RIBO.file.list # RPFs density file list of samples
RIBO_merged.txt # Merged RPFs density file
```



### 5.6 Calculate tri-nucleotide periodicity

Tri-nucleotide periodicity serves as a critical quality metric in Ribo-seq data analysis, fundamentally determining the biological interpretability of codon-resolution findings.

High-quality periodicity (typically >0.6 phase coherence score) constitutes an essential prerequisite for robust codon-level analysis, whereas insufficient periodicity (<0.45) systematically introduces frame ambiguity artifacts that compromise translational measurements.

Loss of reading frame synchronization leads to misassignment of ribosome `A/P/E` sites, generating false-positive pause sites from out-of-frame read aggregation.

1. Explanation of `rpf_Periodicity`

```bash
$ rpf_Periodicity -h

Draw the periodicity plot.

Step1: Checking the input Arguments.

usage: rpf_Periodicity [-h] -r RPF -o OUTPUT [-t TRANSCRIPT] [-m MIN] [--tis TIS] [--tts TTS]

This script is used to draw the periodicity plot.

options:
  -h, --help     show this help message and exit
  -m MIN         retain transcript with more than minimum RPFs. (default: 50).
  --tis TIS      The number of codons after TIS will be discarded.. (default: 0 AA).
  --tts TTS      The number of codons before TTS will be discarded.. (default: 0 AA).

Required arguments:
  -r RPF         the name of input RPFs file in TXT format.
  -o OUTPUT      the prefix of output file.
  -t TRANSCRIPT  the name of input transcript filein TXT format.
```

2. Check the tri-nucleotide periodicity of Ribo-seq

```bash
$ cd ./06.periodicity/

#################################################
# check the periodicity
rpf_Periodicity \
 -r ../05.merge/RIBO_merged.txt \
 -m 30 --tis 0 --tts 0 -o RIBO &>> RIBO.log

cd ..
```

3. Results of `rpf_Periodicity`

```bash
RIBO_count_periodicity_plot.pdf # Barplot of read counts showing 3-nucleotide periodicity
RIBO_count_periodicity_plot.png # Barplot of read counts showing 3-nucleotide periodicity
RIBO.log # Log file of program execution
RIBO_periodicity.txt # Statistical values of 3-nucleotide periodicity of all samples
RIBO_ratio_periodicity_plot.pdf # Barplot of read ratios showing 3-nucleotide periodicity
RIBO_ratio_periodicity_plot.png # Barplot of read ratios showing 3-nucleotide periodicity
```


### 5.7 `Meta-gene` analysis

Our `Meta-gene` analysis framework enables systematic investigation of translation dynamics proximal to start and stop codons.
It entails aggregates ribosome-protected fragment (RPF) density across -15 and +60 codon windows relative to initiation/termination sites, normalized by transcript abundance.

This reveals:\
Peak/trough patterns indicative of translation initiation efficiency,\
Read accumulation gradients reflecting termination kinetics,\
Tri-Nucleotide Periodicity Quantification.

1. Explanation of `rpf_Metaplot`

```bash
$ rpf_Metaplot -h

Draw the metaplot.

Step1: Checking the input Arguments.

usage: rpf_Metaplot [-h] -t TRANSCRIPT -r RPF -o OUTPUT [-m MIN] [--utr5 UTR5] [--cds CDS] [--utr3 UTR3] [-n] [--mode {line,bar}]

This script is used to draw the meta plot.

options:
  -h, --help         show this help message and exit
  -m MIN             delete transcript with less than minimum RPFs. (default: 50).
  --utr5 UTR5        the codon number in 5-utr region (default: 20 AA).
  --cds CDS          the codon number in cds region (default: 50 AA).
  --utr3 UTR3        the codon number in 3-utr region (default: 20 AA).
  -n                 normalize the RPFs count to RPM. (default: False).
  --mode {line,bar}  specify the mode of metaplot. (default: bar).

Required arguments:
  -t TRANSCRIPT      the name of input transcript filein TXT format.
  -r RPF             the name of input RPFs file in TXT format.
  -o OUTPUT          the prefix name of output file.
```

2. `Meta-gene` analysis of Ribo-seq

```bash
$ cd ./07.metaplot/

#################################################
# metagene analysis
rpf_Metaplot \
 -t ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RIBO_merged.txt \
 -m 50 --mode bar -o RIBO &>> RIBO.log

cd ..
```

3. Results of `rpf_Metaplot`

```bash
RIBO.log # Log file of program execution
RIBO_tis_tts_metaplot.txt # Metagene statistical values at start and stop codons across all samples
RIBO_SRR1944912_meta_bar_plot.pdf # Metaplot of all samples at start and stop codons
RIBO_SRR1944912_meta_bar_plot.png # Metaplot of all samples at start and stop codons
RIBO_SRR1944912_tis_tts_metaplot.txt # Metagene statistical values at start and stop codons for sample SRR1944912
```


### 5.8 Gene coverage

To systematically assess potential technical or translation biases in Ribo-seq data, we developed an analytical pipeline that quantifies genome-wide RPF coverage uniformity across gene bodies.

Genes are partitioned into fixed-length intervals (default: 10% of CDS length), with raw RPF counts per `bin` recorded.
These values undergo library-size normalization using reads per million (RPM) to account for transcript length and sequencing depth variations.

Processed data is rendered through three complementary analytical views:\
`Aggregate Density Profile`: Smoothed line plot displaying mean RPF density across all genes, highlighting global coverage trends.\
`Gene-specific Heatmap`: Matrix visualization of normalized RPF counts (log₂-transformed) ordered by gene expression levels, revealing individual gene coverage patterns.\
`Binned Coverage Distribution`: Stacked bar plot showing the percentage of genes achieving threshold coverage (≥50% of expected reads) in each interval.

1. Explanation of `rpf_Coverage`

```bash
$ rpf_Coverage -h

Draw the metagene coverage.

Step1: Checking the input Arguments.
usage: rpf_Coverage [-h] -t TRANSCRIPT -r RPF [-o OUTPUT] [-f {0,1,2,all}] [-m MIN] [-b BIN] [-n] [--thread THREAD] [--outlier] [--set {intersect,union}] [--heat] [--bar]

This script is used to draw the coverage meta plot.

options:
  -h, --help            show this help message and exit
  -f {0,1,2,all}        set the reading frame for occupancy calculation. (default: all).
  -m MIN                retain transcript with more than minimum RPFs. (default: 50).
  -b BIN                adjust the transcript to specified bins. 30 for 5'-UTRand 3'-UTR, 100 for CDS. (default: 30,100,30).
  -n                    normalize the RPFs count to RPM. (default: False).
  --thread THREAD       the number of threads. (default: 1).
  --outlier             filter the outliers (default: False).
  --set {intersect,union}
                        filter the gene list with 5-UTR / CDS / 3-UTR. (default: union).
  --heat                draw the coverage heatmap of whole gene. (default: False).
  --bar                 draw the coverage barplot of whole gene. (default: False).

Required arguments:
  -t TRANSCRIPT         the name of input transcript filein TXT format.
  -r RPF                the name of input RPFs file in TXT format.
  -o OUTPUT             the prefix of output file.
```

2. Check gene density of Ribo-seq

```bash
$ cd ./08.coverage/

#################################################
# check the rpf density along with the gene body
rpf_Coverage \
 -t ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RIBO_merged.txt \
 -m 50 --outlier \
 -b 10,100,10 \
 -n --heat \
 -o RIBO &>> RIBO.log

rpf_Percent \
 -t ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RIBO_merged.txt \
 -n -m 50 \
 -f 0 \
 -o RIBO &>> RIBO.log

cd ..
```

3. Results of `rpf_Coverage`

```bash
RIBO.log # Log file of program execution
RIBO_SRR1944912_10_150_10_coverage.txt # Statistical results of RPF density distribution across genes
RIBO_SRR1944912_10_150_10_heat_plot.png # Heatmap of RPF density distribution across genes
RIBO_SRR1944912_coverage_bar_plot.pdf # Percentage barplot of RPF density distribution across genes
RIBO_SRR1944912_coverage_bar_plot.png # Percentage barplot of RPF density distribution across genes
RIBO_SRR1944912_coverage_line_plot.pdf # Percentage lineplot of RPF density distribution across genes
RIBO_SRR1944912_coverage_line_plot.png # Percentage lineplot of RPF density distribution across genes
```


### 5.9 Check the repeatability of samples

Our analytical pipeline provides a hierarchical framework for assessing sample reproducibility in ribosome profiling studies, implementing dual-level correlation analyses.

`Gene-Level Reproducibility`:\
Quantifies ribosome-protected fragments (RPFs) across entire gene bodies, followed by inter-sample Pearson correlation coefficient calculation.
This approach evaluates global translation consistency, particularly suitable for highly expressed genes with robust ribosome coverage.

`ORF-Level Reproducibility`:\
Performs nucleotide-resolution quantification of RPFs within individual open reading frames (ORFs), then computes Pearson correlations between replicate samples.
This finer-grained analysis detects localized translational variations while maintaining phase-awareness through in-frame read filtering.


1. Explanation of `rpf_Corr`

```bash
$ rpf_Corr -h

Draw the correlation of samples.

Step1: Checking the input Arguments.

usage: rpf_Corr [-h] -r RPF -o OUTPUT

This script is used to draw the correlation of rpf density.

options:
  -h, --help  show this help message and exit

Required arguments:
  -r RPF      the name of input RPFs file in TXT format.
  -o OUTPUT   the prefix of output file. (prefix + _rpf_merged.txt)
```

2. Check the repeatability of Ribo-seq

```bash
$ cd ./09.correlation/

#################################################
# calculate the samples replication of Ribo-seq
rpf_Corr \
 -r ../05.merge/RIBO_merged.txt \
 -o RIBO &>> RIBO.log
```

3. Results of `rpf_Corr`

```bash
RIBO_gene_corr_f0.txt # Pearson correlation of total RPFs on gene frame 0
RIBO_gene_corr_f1.txt # Pearson correlation of total RPFs on gene frame 1
RIBO_gene_corr_f2.txt # Pearson correlation of total RPFs on gene frame 2
RIBO_gene_corr_frame.txt # Pearson correlation of RPFs across all gene frames
RIBO_gene_correlation_plot.pdf # Heatmap of Pearson correlation of RPFs across all gene frames
RIBO_gene_correlation_plot.png # Heatmap of Pearson correlation of RPFs across all gene frames
RIBO.log # Log file of program execution
RIBO_rpf_correlation_plot.pdf # Heatmap of Pearson correlation of RPFs on gene frame 0
RIBO_rpf_correlation_plot.png # Heatmap of Pearson correlation of RPFs on gene frame 0
RIBO_rpf_corr_f0.txt # Pearson correlation between RPFs on gene frame 0
RIBO_rpf_corr_f1.txt # Pearson correlation between RPFs on gene frame 1
RIBO_rpf_corr_f2.txt # Pearson correlation between RPFs on gene frame 2
RIBO_rpf_corr_frame.txt # Pearson correlation between RPFs across all gene frames
```


### 5.10 Quantification of gene expression and translation levels

Ribo-seq quantification fundamentally differs from RNA-seq approaches.
While RNA-seq quantifies expression via read coverage across transcripts, Ribo-seq specifically measures ribosome occupancy density within coding sequences (CDS).
To mitigate artifacts from transitional translation states, standard analytical pipelines exclude the first 15 codons downstream of start codons and the last 5 codons upstream of stop codons.

For enhanced precision, rigorous filtering protocols may be implemented to retain only in-frame ribosome-protected fragments (RPFs),
systematically removing out-of-frame reads that likely represent stochastic noise rather than true elongation events.


1. Explanation of `rpf_Quant`

```bash
$ rpf_Quant -h

Quantify the RPFs in the different region.

Step1: Checking the input Arguments.
usage: rpf_Quant [-h] -r RPF -o OUTPUT [-f {0,1,2,all}] [--tis TIS] [--tts TTS] [--utr5] [--utr3]

This script is used to quantify RPFs in the CDS region.

options:
  -h, --help      show this help message and exit
  -f {0,1,2,all}  set the reading frame for occupancy calculation. (default: all).
  --tis TIS       The number of codons after TIS will be discarded. (default: 0).
  --tts TTS       The number of codons before TES will be discarded. (default: 0).
  --utr5          quantification of 5'-utr. (default: False).
  --utr3          quantification of 3'-utr. (default: False).

Required arguments:
  -r RPF          the name of input RPFs file in TXT format.
  -o OUTPUT       the prefix of output file. (default: prefix + _rpf_quant.txt)
```

2. Quantification of Ribo-seq

```bash
$ cd ./10.quantification/

#################################################
# quantify the gene expression
rpf_Quant \
 -r ../05.merge/RIBO_merged.txt \
 --tis 15 \
 --tts 5 \
 -o RIBO &>> RIBO.log 

cd ..
```

3. Results of `rpf_Quant`

```bash
RIBO_cds_rpm_bar_plot.pdf # Barplot of RPFs distribution in the gene CDS region
RIBO_cds_rpm_cdf_plot.pdf # Cumulative distribution plot of RPFs in the gene CDS region
RIBO_cds_rpm_heatmap.pdf # Expression heatmap of RPFs in the gene CDS region
RIBO_cds_rpm_pca_plot.pdf # Principal component analysis (PCA) plot of RPFs in the gene CDS region
RIBO_cds_rpm_pca.txt # Principal component analysis (PCA) results of RPFs in the gene CDS region
RIBO_cds_rpf_quant.txt # Statistical results of RPFs in the gene CDS region
RIBO_cds_rpkm_quant.txt # Statistical results of RPKM in the gene CDS region
RIBO_cds_rpm_quant.txt # Statistical results of RPM in the gene CDS region
RIBO_cds_tpm_quant.txt # Statistical results of TPM in the gene CDS region
RIBO.log # Log file of program execution
RIBO_total.txt # Total RPFs across all samples
```


### 5.11 Calculate codon pausing score

Ribosome profiling studies are able to capture ribosome pausing because when a specific codon is translated more slowly on average, the increased ribosome occupancy indicates that there are more RPFs associated with that codon genome-wide.

Pause scores were calculated by normalizing per-nucleotide read counts against the gene's mean read density. For codon-level analysis, read counts across all three nucleotide positions of each codon could used for calculation. Final pause scores represent the averaged values derived from all occurrences of the target codon.

1. Explanation of `rpf_Pausing`

```bash
$ rpf_Pausing -h

Calculate the relative codon pausing score.

Step1: Checking the input Arguments.
usage: rpf_Pausing [-h] -r RPF [-l LIST] -o OUTPUT [-s {E,P,A}] [-f {0,1,2,all}] [-b BACKGROUND] [-m MIN] [--tis TIS] [--tts TTS] [-n] [--scale {zscore,minmax}] [--stop]
                   [--fig {none,png,pdf}] [--all]

This script is used to calculate the relative pausing score.

options:
  -h, --help            show this help message and exit
  -s {E,P,A}            set the E/P/A-site for pausing calculation. (default: P).
  -f {0,1,2,all}        set the reading frame for pausing calculation. (default: all).
  -b BACKGROUND         set the codon number before and after p-site as the background. (default: 2).
  -m MIN                retain transcript with more than minimum RPFs. (default: 50).
  --tis TIS             The number of codons after TIS will be discarded. (default: 10 AA).
  --tts TTS             The number of codons before TTS will be discarded. (default: 5 AA).
  -n                    normalize the RPFs count to RPM. (default: False).
  --scale {zscore,minmax}
                        normalize the pausing score. (default: minmax).
  --stop                rmove the stop codon. (default: False).
  --fig {none,png,pdf}  draw the rpf pausing score of each gene (it will takes a lot of time). (default: none).
  --all                 output all pausing score of each gene. (default: False).

Required arguments:
  -r RPF                the name of input RPFs file in TXT format.
  -l LIST               the gene name list in TXT format. (default: whole).
  -o OUTPUT             the prefix of output file.
```

2. Calculate codon-level pausing scores in Ribo-seq data

```bash
$ cd ./11.pausing_score/

#################################################
# calculate the codon pausing score of E/P/A site
for sites in E P A
do
rpf_Pausing \
 -l ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RIBO_merged.txt \
 -b 0 --stop \
 -m 30 \
 -s $sites \
 -f 0 \
 --scale minmax \
 -o "$sites"_site &>> "$sites"_site.log
done

cd ..
```

3. Results of `rpf_Pausing`

```bash
A_site_cds_codon_pausing_score.txt # Pausing score for each codon at the A-site in the gene CDS region
A_site_cds_pausing_score.txt # Sum of pausing score at the A-site in the gene CDS region
A_site.log # Log file of program execution
A_site_sum_codon_pausing_score.txt # Sum of pausing score for all codons at the A-site in the gene CDS region
A_site_total_pausing_heatplot.pdf # Heatmap of pausing score for all codons at the A-site in the gene CDS region
A_site_total_pausing_heatplot.png # Heatmap of pausing score for all codons at the A-site in the gene CDS region
A_site_valid_pausing_heatplot.pdf # Heatmap of pausing score for valid codons at the A-site in the gene CDS region
A_site_valid_pausing_heatplot.png # Heatmap of pausing score for valid codons at the A-site in the gene CDS region
```


### 5.12 Calculate codon occupancy

For global codon occupancy analysis, 
`A(P/E)-site` codons were assigned using the established criteria, 
and read counts at each codon were normalized against the average per-codon read density within their respective open reading frames (ORFs).


1. Explanation of `rpf_Occupancy`

```bash
$ rpf_Occupancy -h

Calculate the codon occupancy.

Step1: Checking the input Arguments.
usage: rpf_Occupancy [-h] -r RPF [-l LIST] -o OUTPUT [-s {E,P,A}] [-f {0,1,2,all}] [-m MIN] [-n] [--tis TIS] [--tts TTS] [--scale {zscore,minmax}] [--stop] [--all]

This script is used to draw the codon occupancy plot.

options:
  -h, --help            show this help message and exit
  -s {E,P,A}            set the E/P/A-site for occupancy calculation. (default: P).
  -f {0,1,2,all}        set the reading frame for occupancy calculation. (default: all).
  -m MIN                retain transcript with more than minimum RPFs. (default: 30).
  -n                    normalize the RPFs count to RPM. (default: False).
  --tis TIS             The number of codons after TIS will be discarded. (default: 15 AA).
  --tts TTS             The number of codons before TTS will be discarded.. (default: 5 AA).
  --scale {zscore,minmax}
                        normalize the occupancy. (default: minmax).
  --stop                rmove the stop codon. (default: False).
  --all                 output all RPFs density. (default: False).

Required arguments:
  -r RPF                the name of input RPFs file in TXT format.
  -l LIST               the gene name list in TXT format. (default: whole).
  -o OUTPUT             the prefix of output file.
```

2. Calculate codon-level occupancy in Ribo-seq data

```bash
$ cd ./12.codon_occupancy/

#################################################
# calculate the codon occupancy of E/P/A site
for sites in E P A
do
rpf_Occupancy \
 -l ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RIBO_merged.txt \
 -m 30 \
 -s "$sites" \
 -f 0 --stop \
 --scale minmax \
 -o "$sites"_site &>> "$sites"_site.log
 
done

cd ..
```

3. Results of `rpf_Occupancy`

```bash
A_site_codon_density.txt # Codon occupancy for each codon at the A-site in the gene CDS region
A_site_codon_occupancy.txt # Codon occupancy for all codon at the A-site in the gene CDS region
A_site.log # Log file of program execution
A_site_occupancy_corrplot.pdf # Correlation heatmap of codon occupancy at the A-site
A_site_occupancy_corrplot.png # Correlation heatmap of codon occupancy at the A-site
A_site_occupancy_corr.txt # Correlation of codon occupancy at the A-site
A_site_occupancy_heatplot.pdf # Heatmap of codon occupancy at the A-site
A_site_occupancy_heatplot.png # Heatmap of codon occupancy at the A-site
A_site_occupancy_relative_heatplot.pdf # Heatmap of relative codon occupancy at the A-site
A_site_occupancy_relative_heatplot.png # Heatmap of relative codon occupancy at the A-site
A_site_occupancy_relative_lineplot.pdf # Lineplot of relative codon occupancy at the A-site
A_site_occupancy_relative_lineplot.png # Lineplot of relative codon occupancy at the A-site
```


### 5.13 Calculate decoding time

In addition to translation elongation analysis performed at the Ribo-seq level, RNA-seq can also be used for correction to account for the influence of the mRNA's inherent state on translation.


1. Explanation of `rpf_CDT`

```bash
$ rpf_CDT -h

Calculate the codon decoding time.

Step1: Checking the input Arguments.
usage: rpf_CDT [-h] --rpf RPF --rna RNA -l LIST -o OUTPUT [-s {E,P,A}] [-f {0,1,2,all}] [-m MIN] [--tis TIS] [--tts TTS] [--scale {zscore,minmax}] [--stop]

This script is used to draw the codon decoding time plot.

options:
  -h, --help            show this help message and exit
  -s {E,P,A}            set the E/P/A-site for codon decoding time calculation. (default: P).
  -f {0,1,2,all}        set the reading frame for codon decoding time calculation. (default: all).
  -m MIN                retain transcript with more than minimum RPFs. (default: 30).
  --tis TIS             The number of codons after TIS will be discarded.. (default: 15 AA).
  --tts TTS             The number of codons before TTS will be discarded.. (default: 5 AA).
  --scale {zscore,minmax}
                        normalize the codon decoding time. (default: minmax).
  --stop                rmove the stop codon. (default: False).

Required arguments:
  --rpf RPF             the name of input RPFs file in TXT format.
  --rna RNA             the name of input reads file in TXT format.
  -l LIST               the gene name list in TXT format. (default: whole).
  -o OUTPUT             the prefix of output file.
```

2. Calculate codon-level decoding time in Ribo-seq data

```bash
$ cd ./13.codon_decoding_time/

#################################################
# calculate the codon decoding time of E/P/A site
for sites in E P A
do
rpf_CDT \
 -l ../../../1.reference/norm/gene.norm.txt \
 --rna ../../../3.rna-seq/5.riboparser/05.merge/RNA_merged.txt \
 --rpf ../05.merge/RIBO_merged.txt \
 --stop \
 -m 50 \
 -f 0 \
 -s $sites \
 --tis 10 \
 --tts 5 \
 -o "$sites"_site &>> "$sites"_site.log

done

cd ..
```

3. Results of `rpf_CDT`

```bash
A_site_cdt_corrplot.pdf # Correlation heatmap of codon decoding time at the A-site
A_site_cdt_corrplot.png # Correlation heatmap of codon decoding time at the A-site
A_site_cdt_corr.txt # Correlation of codon decoding time at the A-site
A_site_cdt_heatplot.pdf # Heatmap of codon decoding time at the A-site
A_site_cdt_heatplot.png # Heatmap of codon decoding time at the A-site
A_site_cdt.txt # Codon decoding time for all codon at the A-site in the gene CDS region
A_site.log # Log file of program execution
```


### 5.14 Calculate selection time

Codon usage is not equal across genomes, with some codons being more frequently used than others, thought to improve translational efficiency.
However, previous studies reveal that translational efficiency is optimized by a mechanism involving proportional codon usage based on tRNA concentrations.
These results provide new insights into protein translation, explain unequal codon usage, and highlight natural selection for translational efficiency. Codon selection time can be used to quantify this process.

1. Explanation of `rpf_CST`

```bash
$ rpf_CST -h

Calculate the codon decoding time.

Step1: Checking the input Arguments.
usage: rpf_CST [-h] --rpf RPF --rna RNA [-l LIST] -o OUTPUT [-s {E,P,A}] [-f {0,1,2,all}] [-m MIN] [-t TIMES] [--tis TIS] [--tts TTS] [--scale {zscore,minmax}] [--stop]

This script is used to draw the codon decoding time plot.

options:
  -h, --help            show this help message and exit
  -s {E,P,A}            set the E/P/A-site for codon decoding time calculation. (default: P).
  -f {0,1,2,all}        set the reading frame for codon decoding time calculation. (default: all).
  -m MIN                retain transcript with more than minimum RPFs. (default: 30).
  -t TIMES              Specify the number of iteration times required for computation. (default: 10).
  --tis TIS             The number of codons after TIS will be discarded. (default: 0 AA).
  --tts TTS             The number of codons before TTS will be discarded. (default: 0 AA).
  --scale {zscore,minmax}
                        normalize the codon selection time. (default: minmax).
  --stop                rmove the stop codon. (default: False).

Required arguments:
  --rpf RPF             the name of input RPFs file in TXT format.
  --rna RNA             the name of input reads file in TXT format.
  -l LIST               the gene name list in TXT format. (default: whole).
  -o OUTPUT             the prefix of output file.
```

2. Calculate codon-level selection time in Ribo-seq data

```bash
$ cd ./14.codon_selection_time/

#################################################
# calculate the codon selection time of E/P/A site
for sites in E P A
do
rpf_CST \
 -l ../../../1.reference/norm/gene.norm.txt \
 --rna ../../../3.rna-seq/5.riboparser/05.merge/RNA_merged.txt \
 --rpf ../05.merge/RIBO_merged.txt \
 --stop \
 -m 50 \
 -f 0 \
 -s $sites \
 --tis 10 \
 --tts 5 \
 -o "$sites"_site &>> "$sites"_site.log

done

cd ..
```

3. Results of `rpf_CST`

```bash
A_site_codon_selection_time.txt # Codon selection time for all codon at the A-site in the gene CDS region
A_site_cst_corrplot.pdf # Correlation heatmap of codon selection time at the A-site
A_site_cst_corrplot.png # Correlation heatmap of codon selection time at the A-site
A_site_cst_corr.txt # Correlation of codon selection time at the A-site
A_site_cst_heatplot.pdf # Heatmap of codon selection time at the A-site
A_site_cst_heatplot.png # Heatmap of codon selection time at the A-site
A_site_iterative_codon_selection_time.txt # Codon selection time for all codon at the A-site in the gene CDS region
A_site.log # Log file of program execution
```


### 5.15 Calculate Coefficient of Variation

While codon-level analysis can indicates alterations in translation elongation, gene-level validation is complicated by variable ribosome profiling coverage due to gene expression dynamics.
Low-coverage genes may artifactually appear to exhibit more translational pausing due to noise inversely scaling with coverage. 

To resolve this, Peter et. al developed a gene-level analytical method that explicitly models noise dependence on coverage. They fit the following two-parameter model to the data to accommodate a variety of statistical behaviors for counting noise:

$$log_2(CV) = \frac{1}{2} log_2 (\frac{β}{μ} + α)$$

where CV is the coefficient of variation in the ribosome profile of a given gene, 
μ is mean coverage (RPF reads percodon), and α and β are fitting parameters. 
Importantly, when α = 0 and β = 1, Equation results from a Poisson distribution, 
whereas α > 0 and β = 1 indicates a negative binomial distribution.

1. Explanation of `rpf_CoV`

```bash
$ rpf_CoV -h

Calculate CoV in the CDS region.

Step1: Checking the input Arguments.
usage: rpf_CoV [-h] -r RPF [-g GROUP] [-l LIST] -o OUTPUT [-f {0,1,2,all}] [-m MIN] [-n] [--tis TIS] [--tts TTS] [--fig]

This script is used to calculate CoV in the CDS region.

options:
  -h, --help      show this help message and exit
  -f {0,1,2,all}  set the reading frame for occupancy calculation. (default: all).
  -m MIN          retain transcript with more than minimum RPFs. (default: 5).
  -n              normalize the RPFs count to RPM. (default: False).
  --tis TIS       The number of codons after TIS will be discarded. (default: 15).
  --tts TTS       The number of codons before TES will be discarded. (default: 5).
  --fig           show the figure. (default: False).

Required arguments:
  -r RPF          the name of input RPFs file in TXT format.
  -g GROUP        specify the list of sample group. (default: None)
  -l LIST         the gene name list in TXT format. (default: whole).
  -o OUTPUT       the prefix of output file. (prefix + _Cov.txt)

The group file needs to contain at least two column:
+----------+---------+
| name     | group  |
+==========+=========+
| wt1      | wt      |
| wt2      | wt      |
| treat1   | treat   |
| treat2   | treat   |
| ko1      | ko      |
| ko2      | ko      |
+----------+---------+
```

2. Calculate gene coefficient of variation in Ribo-seq data

```bash
$ cd ./15.coefficient_of_variation/

#################################################
# Here we can configure the design file to calculate differences between different groups.
$ cat design.txt
Name	Group
WT_ribo_YPD1	WT_ribo_YPD
WT_ribo_YPD2	WT_ribo_YPD
WT_ribo_YPD3	WT_ribo_YPD
ncs2d_ribo_YPD1	ncs2d_ribo_YPD
ncs2d_ribo_YPD2	ncs2d_ribo_YPD
ncs2d_ribo_YPD3	ncs2d_ribo_YPD
elp6d_ribo_YPD1	elp6d_ribo_YPD
elp6d_ribo_YPD2	elp6d_ribo_YPD
elp6d_ribo_YPD3	elp6d_ribo_YPD
ncs2d_elp6d_ribo_YPD1	ncs2d_elp6d_ribo_YPD
ncs2d_elp6d_ribo_YPD2	ncs2d_elp6d_ribo_YPD
ncs2d_elp6d_ribo_YPD3	ncs2d_elp6d_ribo_YPD

#################################################
# calculate the coefficient of variation
rpf_CoV \
 -l ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RIBO_merged.txt \
 -f 0 \
 -m 30 \
 --tis 10 \
 --tts 5 \
 --fig \
 -g design.txt \
 -o RIBO &>> RIBO.log

```

3. Explanation of `rpf_Cumulative_CoV`

```bash
$ rpf_Cumulative_CoV -h

Retrieve the RPFs with gene list.

Step1: Checking the input Arguments.

usage: rpf_Cumulative_CoV [-h] -r RPF [-o OUTPUT] [-l LIST] [-m MIN] [-n] [-t TRIM] [-s] [-z]

This script is used to calculate the cumulative CoV.

options:
  -h, --help  show this help message and exit
  -l LIST     the list of input genes for transcript id.
  -m MIN      retain transcript with more than minimum RPFs (default: 0).
  -n          normalize the RPFs count to RPM (default: False).
  -t TRIM     trim transcript with specific length (default: 50 nt).
  -s          split gene rpf to each TXT file (default: False).
  -z          set the start site to zero (default: False).

Required arguments:
  -r RPF      the name of input RPFs density file in TXT format.
  -o OUTPUT   prefix of output file name (default: filename + '_cumulative_CoV.txt'.

```


4. Calculate the cumulative gene coefficient of variation in Ribo-seq data

```bash
#################################################
# calculate the cumulative coefficient of variation
rpf_Cumulative_CoV \
 -l ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RIBO_merged.txt \
 -m 50 \
 -n \
 -z \
 -t 300 \
 -o RIBO &>> RIBO.log
```

5. Results of `rpf_CoV`

```bash
gene_compared_CoV.txt # Compared gene coefficient of variation
gene_CoV.txt # Gene coefficient of variation
gene.log # Log file of program execution
gene_WT_ribo_YPD_vs_ncs2d_ribo_YPD_CoV_fitplot.pdf # Fitted lineplot of gene coefficient of variation
gene_WT_ribo_YPD_vs_ncs2d_ribo_YPD_CoV_fitplot.png # Fitted lineplot of gene coefficient of variation
```


### 5.16 Meta-codon analysis

To demonstrate the pausing patterns of different codons, a meta plot is utilized here to display the RPF density within a 20-nucleotide window surrounding the specified codon.  
The program also supports the visualization of different frames and incorporates a smoothing function to mitigate spike signals caused by data instability.

1. Explanation of `rpf_Meta_Codon`

```bash
$ rpf_Meta_Codon -h

Draw the meta-codon plot.

Step1: Checking the input Arguments.
usage: rpf_Meta_Codon [-h] [-l LIST] -r RPF [-c CODON] -o OUTPUT [-f {0,1,2}] [-a AROUND] [-m MIN] [--tis TIS] [--tts TTS] [-n] [-u] [-s] [--smooth SMOOTH] [--thread THREAD] [--fig]

This script is used to draw the meta codon plot.

options:
  -h, --help       show this help message and exit
  -f {0,1,2}       set the reading frame for occupancy calculation. (default: all).
  -a AROUND        retrieve length of codon upstream and downstream. (default: 20).
  -m MIN           retain transcript with more than minimum RPFs. (default: 50).
  --tis TIS        The number of codons after TIS will be discarded.. (default: 0 AA).
  --tts TTS        The number of codons before TTS will be discarded.. (default: 0 AA).
  -n               normalize the RPFs count to RPM. (default: False).
  -u               delete the cross repetition codon in different window. (default: False).
  -s               scale the window density with gene density. (default: False).
  --smooth SMOOTH  smooth the window density [eg, 3,1]. (default: None).
  --thread THREAD  the number of threads (default: 1).
  --fig            output the figure. (default: False).

Required arguments:
  -l LIST          the gene name list in TXT format. (default: whole).
  -r RPF           the name of input RPFs file in TXT format.
  -c CODON         the codon list in TXT format.
  -o OUTPUT        the prefix of output file.
```

2. Calculate meta-codon density in Ribo-seq data

```bash
$ cd ./16.meta_codon/

#################################################
# Here we can configure the codon list.
$ cat codon_list.txt
AAA
AAC
AAG
AAT
AAGAAG
ATGATG
CCCGGG
...

#################################################
# codon meta analysis
rpf_Meta_Codon \
 -r ../05.merge/RIBO_merged.txt \
 -m 50 -f 0 \
 -c codon_list.txt \
 -a 15 -u -n \
 -o RIBO &>> RIBO.log

cd ..
```

3. Results of `rpf_Meta_Codon`

```bash
RIBO.log # Log file of program execution
RIBO_AAA_97591_8146_meta_density.txt # RPFs density of AAA codon
RIBO_AAA_97591_8146_meta_sequence.txt # Upstream and downstream sequence around AAA codon
RIBO_AAA.pdf # Metaplot of AAA codon
RIBO_AAA.png # Metaplot of AAA codon
```


## 6. Other toolkits
### 6.1 Data shuffling

Some analysis processes require randomly assigned data for control,
 so a step is added here to reshuffling the RPFs density file.

1. Explanation of `rpf_Shuffle`

```bash
$ rpf_Shuffle -h

Shuffle the RPFs data.

Step1: Checking the input Arguments.

usage: rpf_Shuffle [-h] -r RPF -o OUTPUT [-l LIST] [-s SEED] [-i]

This script is used to shuffle the RPFs data.

options:
  -h, --help  show this help message and exit
  -l LIST     the list of input genes for transcript id.
  -s SEED     the random seed for shuffle. (default: 0).
  -i          shuffle the RPFs data for each samples. (default: False).

Required arguments:
  -r RPF      the name of input RPFs density file in TXT format.
  -o OUTPUT   the prefix of output file. (prefix + _shuffle.txt)
```

2. Shuffle gene density values in Ribo-seq data.

```bash
$ cd
$ cd ./sce/4.ribo-seq/5.riboparser/17.shuffle/

#################################################
# codon meta analysis
rpf_Shuffle \
 -l ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RIBO_merged.txt \
 -s 0 \
 -i \
 -o RIBO &>> RIBO.log
```

3. Shuffle gene density values in RNA-seq data

```bash
$ cd
$ cd ./sce/3.rna-seq/5.riboparser/10.shuffle/

#################################################
# retrieve and format the gene density
rpf_Shuffle \
 -l ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RNA_merged.txt \
 -s 0 \
 -i \
 -o RNA &>> RNA.log
```

4. Results of `rpf_Shuffle`

```bash
# results of ribo-seq
RIBO.log # Log file of program execution
RIBO_shuffle.txt # Shuffled RPFs density file
```


### 6.2 Retrieve and format the gene density

In many cases, it is necessary to perform some additional operations on the gene set in the RPFs density file, 
such as filtering, RPM standardization, long and width data format conversion, etc. 
A specialized tool is provided here for these operations.

1. Explanation of `rpf_Retrieve`

```bash
$ rpf_Retrieve -h

Retrieve the RPFs with gene list.

Step1: Checking the input Arguments.

usage: rpf_Retrieve [-h] -r RPF [-o OUTPUT] [-l LIST] [-m MIN] [-n] [-f] [-s]

This script is used to retrieve density files.

options:
  -h, --help  show this help message and exit
  -l LIST     the list of input genes for transcript id.
  -m MIN      retain transcript with more than minimum RPFs (default: 0).
  -n          normalize the RPFs count to RPM (default: False).
  -f          melt three column data of each sample to one column (default: False).
  -s          split gene rpf to each TXT file (default: False).

Required arguments:
  -r RPF      the name of input RPFs density file in TXT format.
  -o OUTPUT   prefix of output file name (default: filename + '_retrieve.txt'.
```

2. Extract and format gene density from Ribo-seq data

```bash
$ cd
$ cd ./sce/4.ribo-seq/5.riboparser/18.retrieve/

#################################################
# retrieve and format the gene density with gene covered more than 50 reads
rpf_Retrieve \
 -l ../../../1.reference/norm/gene.norm.txt \ 
 -r ../05.merge/RIBO_merged.txt \
 -m 50 \
 -f \
 -n \
 -o RIBO &>> RIBO.log

cd ..
```

3. Extract and format gene density from RNA-seq data

```bash
$ cd
$ cd ./sce/3.rna-seq/5.riboparser/11.retrieve/

#################################################
# retrieve and format the gene density with gene covered more than 50 reads
rpf_Retrieve \
 -l ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RNA_merged.txt \
 -m 50 \
 -f \
 -n \
 -o RNA &>> RNA.log

cd ..
```

4. Results of `rpf_Retrieve`

```bash
# results of ribo-seq
RIBO.log
RIBO_retrieve.txt
```

### 6.3 Filter the frame shifting genes

A frameshift in translation occurs when the ribosome shifts by one or more nucleotides in the mRNA sequence, causing a misreading of the codons.
This results in a completely altered amino acid sequence downstream of the shift,
often leading to premature termination or a nonfunctional protein.
Frameshifts can occur naturally due to mutations or during translation errors, and they can significantly impact protein function.
Whenever a stable frameshift occurs, we can detect ribosome occupancy in different reading frames from the Ribo-seq data.

1. Explanation of `rpf_Shift`

```bash
$ rpf_Shift -h

Draw the frame shifting plot.

Step1: Checking the input Arguments.

usage: rpf_Shift.py [-h] -r RPF -o OUTPUT [-t TRANSCRIPT] [-p PERIOD] [-m MIN] [--tis TIS] [--tts TTS]

This script is used to draw the frame shift plot.

options:
  -h, --help     show this help message and exit
  -p PERIOD      the minimum in-frame value for frame shifting screen, range [0 - 100]. (default: 45).
  -m MIN         retain transcript with more than minimum RPFs. (default: 50).
  --tis TIS      the number of codons after TIS will be discarded.. (default: 0 AA).
  --tts TTS      the number of codons before TTS will be discarded.. (default: 0 AA).

Required arguments:
  -r RPF         the name of input RPFs file in TXT format.
  -o OUTPUT      the prefix of output file.
  -t TRANSCRIPT  the name of input transcript filein TXT format.

```

2. Filter the frame shifting genes

```bash
$ cd
$ cd ./sce/4.ribo-seq/5.riboparser/19.frame_shift/

#################################################
# filter the frame shifting genes
rpf_Shift \
 -t ../../../1.reference/norm/gene.norm.txt \
 -r ../05.merge/RIBO_merged.txt \
 --tis 5 --tts 5 \
 -m 50 \
 -p 45 \
 -o RIBO &>> RIBO.log

cd ..
```

4. Results of `rpf_Shift`

```bash
# results of ribo-seq
RIBO.log
RIBO_gene_frame_shift_count_plot.pdf
RIBO_gene_frame_shift_count_plot.png
RIBO_gene_frame_shift_count.txt
RIBO_gene_periodicity.txt
RIBO_SRR1944912_gene_frame_shift.txt
```


## 7. one step for pipeline

### 7.0 Prepare the directories and design file for your project

1. create the directories to store the raw-data and results

```bash
$ cd
$ mkdir sce
$ cd ./sce/
$ mkdir -p ./sce/1.reference
$ mkdir -p ./sce/2.rawdata/ribo-seq ./sce/2.rawdata/rna-seq
$ mkdir -p ./sce/3.rna-seq
$ mkdir -p ./sce/4.ribo-seq
```

2. prepare the design file for your RNA-seq and Ribo-seq data

The design file must contain at least two columns names `Name` and `Group`

```bash
$ cat design.txt

Name    Group
SRR1944912      WT_ribo_YPD
SRR1944913      WT_ribo_YPD
SRR1944914      WT_ribo_YPD
SRR1944915      ncs2d_ribo_YPD
SRR1944916      ncs2d_ribo_YPD
SRR1944917      ncs2d_ribo_YPD
```


### 7.1 run_step1.sh

This step is used for constructing the database, which is essential for the alignment of reads and subsequent analysis using `RiboParser`.

This step is suitable for most genome and gene annotation files derived from `NCBI`.

`NOTE`: The download files in `Step 0.0` need to be modified according to the `species` used in your project!

```bash
$ nohup sh run_step1.sh &
```

### 7.2 run_step2.sh

This step is used for analyzing `RNA-seq` data, including data cleaning, 
alignment, and expression quantification.

`NOTE`: The `adapter` information in `Step 0.0` needs to be modified according to the sequencing 
method used in your project!

```bash
$ nohup sh run_step2.sh &
```

### 7.3 run_step3.sh

This step is used for analyzing `Ribo-seq` data, including data cleaning, 
alignment, and expression quantification.

The `adapter` information in `Step 0.0` needs to be modified according to the 
sequencing method used in your project!

```bash
$ nohup sh run_step3.sh &
```

### 7.4 run_step4.sh

This step is used for analyzing `RNA-seq` data, utilizing `RiboParser` to check the 
sequencing quality of the `RNA-seq` data and prepare formatted files for subsequent 
joint analysis with `Ribo-seq`.

The `BAM` files and `reference genome information` files in `Step 1.0` may need to be 
modified according to the files defined for your project!

```bash
$ nohup sh run_step4.sh &
```

### 7.5 run_step5.sh

This step is used for analyzing `Ribo-seq` data, utilizing `RiboParser` to check the 
sequencing quality of the `Ribo-seq` data.

The `BAM` files, `parameters` and `reference genome information` files in `Step 0.0` may 
need to be modified according to the files defined for your project!

```bash
$ nohup sh run_step5.sh &
```


## 8. Computational performance of the RiboParser
We assessed the workflow on a CentOS 7 system using 12 threads, with RNA-seq and Ribo-seq data from three different species (S. cerevisiae, M. musculus, and H. sapiens). 

| | | | | | | | | | | |
|-|-|-|-|-|-|-|-|-|-|-|
||||||Index building| |Preprocessing & Alignment| |Riboparser| |
|species|Dataset|library|sample number|sample size|Elapsed time|Disk usage|Elapsed time|Disk usage|Elapsed time|Disk usage|
|S. cerevisiae|GSE67387|Ribo-seq|6|32 G|38 s|357 M|43 m 21 s|30 G|1 h 26 m 23s|3.6 G|
| | |RNA-seq|6|17 G|38 s|357 M|32 m 52 s|26 G|37 m 42 s|2.8 G|
|M. musculus|GSE114064|Ribo-seq|6|43 G|59 m 8 s|36G|50 m 27 s|31 G|32 m 3 s|7.9 G|
| | |RNA-seq|6|60 G|59 m 8 s|36G|4 h 14 m 45 s|62 G|29 m 30 s|7.6 G|
|H. sapiens|GSE131650|Ribo-seq|6|42G|1 h 55 m 56 s|44 G|2 h 11 m 42 s|29 G|2 h 18 m 57 s|14 G|
| | |RNA-seq|6|54G|1 h 55 m 56 s|44 G|1 h 15 m 15 s|30 G|40 m 35 s|11 G|

System Recommendations for RiboParser:
For optimal performance, we recommend deploying RiboParser on Linux-based systems (tested on Ubuntu 20.04 LTS/CentOS 7). The hardware specifications scale with biological complexity:

Minimum Configuration
- Memory: ≥ 16 GB RAM
- Processor: ≥ 4-core CPU (Intel Xeon E5-2600+ or equivalent)
- Storage: ≥ 512 GB HDD (SATA III)

Optimal Configuration
- Memory: ≥ 32 GB RAM
- Processor: ≥ 8-core CPU (AMD EPYC 7B12/Intel i9-10900X)
- Storage: ≥ 512 GB NVMe SSD for rapid I/O and 2 TB HDD (SATA III)


## 9. Contribution

Thanks for all the open source tools used in the process.

Thanks to Nedialkova DD and Leidel SA for providing the excellent dataset.

Contribute to our open-source project by submitting questions and code.

Contact `rensc0718@163.com` for more information.


## 10. License

GPL License.
