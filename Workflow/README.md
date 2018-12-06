## Overview of the workflow to be run

**Inputs:** There are 2 unmapped bam files available:

`rawData/Sample_CM-M50-O50-R1/CM-M50-O50-R1.unmapped.bam`

`rawData/Sample_CM-M40-O40-K20-R1/CM-M40-O40-K20-R1.unmapped.bam`

**Process:** GATK Best Practices [pre-processing for variant calling.](https://github.com/gatk-workflows/gatk4-data-processing)

**Output:** A clean BAM file ready for downstream variant calling and it's index written back to S3.

### Reference Data Bundle from the Broad
All reference data files used in these workflows are in S3:

`bundle/hg38/`






### Previous Processing

Concatenated all fastq's and convert to uBAM.

Merge any fastq.gz with R1 into one unzipped fastq, and the same with R2.   
>Note: Needs help with this regex/interfacing with S3.
```
sbatch --wrap="zcat *_R1_*.fastq.gz > forwardReads_R1.fastq"
sbatch --wrap="zcat *_R2_*.fastq.gz > reverseReads_R2.fastq"
```

```
#!/bin/bash

set -e

module load picard/2.18.1-Java-1.8.0_121

thisSample=${1}

java -Xmx8G -jar picard.jar FastqToSam \
    FASTQ=${thisSample}_R1.fastq \ #first read file of pair
    FASTQ2=${thisSample}_R2.fastq \ #second read file of pair
    OUTPUT=${thisSample}.bam \
    READ_GROUP_NAME=${thisSample} \ #required; changed from default of A
    SAMPLE_NAME=${thisSample} \ #required
    LIBRARY_NAME=${thisSample} \ #required
    PLATFORM=illumina \ #recommended
```
Docs on this step:
https://gatkforums.broadinstitute.org/gatk/discussion/6484#latest#top
