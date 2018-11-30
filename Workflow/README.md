## Overview of the workflow to be run

**Inputs:**  Directory (prefix) containing all/only the relevant paired FASTQ's for a specific sample S3, and some reference files!!
**Process:** Get all relevant files from S3, concatenate, make into uBAM, then do GATK Best Practices pre-processing for variant calling.
**Output:** A clean BAM file ready for downstream variant calling and it's index written back to S3. 

### Sample data information
Prefix for containing all the fastq's for this sample in S3:
`fh-pi-paguirigan-a/tg/SR/ngs/illumina/apaguiri/160930_D00300_0322_BH3G32BCXY/Unaligned/Project_apaguiri/Sample_CM-M50-O50-B1/`


Example Forward read filename:
`CM-M50-O50-B1_CGAACTTA_L001_R1_001.fastq.gz`


Example Reverse read filename:
`CM-M50-O50-B1_CGAACTTA_L001_R2_001.fastq.gz`


### Concatenate and convert to uBAM

Merge any fastq.gz with R1 into one unzipped fastq, and the same with R2.   
>Note: Needs help with this regex/interfacing with S3.
```
zcat *_R1_*.fastq.gz > forwardReads_R1.fastq
zcat *_R2_*.fastq.gz > reverseReads_R2.fastq
```


Then you're ready to convert from FASTQ to uBAM:
```
java -Xmx8G -jar picard.jar FastqToSam \
    FASTQ=forwardReads_R1.fastq \ #first read file of pair
    FASTQ2=reverseReads_R2.fastq \ #second read file of pair
    OUTPUT=forprocessing.bam \
    READ_GROUP_NAME=H0164.2 \ #required; changed from default of A
    SAMPLE_NAME=NA12878 \ #required
    LIBRARY_NAME=Solexa-272222 \ #required
    PLATFORM_UNIT=H0164ALXX140820.2 \
    PLATFORM=illumina \ #recommended
    SEQUENCING_CENTER=BI \
    RUN_DATE=2014-08-20T00:00:00-0400
```
Docs on this step:
https://gatkforums.broadinstitute.org/gatk/discussion/6484#latest#top


### Pre-process step for downstream analysis
Then you're ready to pre-process the data for analysis:
https://github.com/gatk-workflows/gatk4-data-processing
