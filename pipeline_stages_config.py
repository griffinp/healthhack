
# stageDefaults contains the default options which are applied to each stage (command).
# This section is required for every Rubra pipeline.
# These can be overridden by options defined for individual stages, below.
# Stage options which Rubra will recognise are: 
#  - distributed: a boolean determining whether the task should be submitted to a cluster
#      job scheduling system (True) or run on the system local to Rubra (False). 
#  - walltime: for a distributed PBS job, gives the walltime requested from the job
#      queue system; the maximum allowed runtime. For local jobs has no effect.
#  - memInGB: for a distributed PBS job, gives the memory in Gigabytes requested from the 
#      job queue system. For local jobs has no effect.
#  - queue: for a distributed PBS job, this is the name of the queue to submit the
#      job to. For local jobs has no effect.
#  - modules: the modules to be loaded before running the task. This is intended for  
#      systems with environment modules installed. Rubra will call module load on each 
#      required module before running the task. Note that defining modules for individual 
#      stages will override (not add to) any modules listed here. This currently only
#      works for distributed jobs.
stageDefaults = {
    'distributed': True,
    'walltime': "08:00:00",
    'memInGB': 6,
    'queue': "batch",
    'modules': [
        "intel/13.1.3",
        "bwa-intel/0.6.2",
        "samtools-intel/0.1.19",
        #"picard/1.96",
        "picard/1.69",
        "R-gcc/3.0.2",
        "gatk/3.2-2",
        "java/1.7.0_25",
        "trimmomatic/0.30",
        "igv/2.3.15",
        "perl/5.18.0",
        "freebayes-gcc/0.9.10",
        "bismark/0.13.0",
        "bowtie2-intel/2.2.1"
    ],
    "jobscript": "--account=VR0002",
}

# stages should hold the details of each stage which can be called by runStageCheck.
# This section is required for every Rubra pipeline.
# Calling a stage in this way carries out checkpointing and, if desired, batch job
# submission. 
# Each stage must contain a 'command' definition. See stageDefaults above for other 
# allowable options.
stages = {
    "indexBWA": {
        "command": "bwa index -p %index_prefix %ref_file",
        "walltime": "2:00:00"
    },
    "indexSamtools": {
        "command": "samtools faidx %ref_file",
        "walltime": "1:00:00"
    },
    "dictPicard": {
        "command": "java -Xmx4g -jar /usr/local/picard/1.69/lib/CreateSequenceDictionary.jar R= %ref_file O= %out",
        "walltime": "1:00:00"
    },
    "fastqc": {
        "command": "fastqc --quiet -o %outdir %seq",
        "walltime": "1:00:00",
        'modules': [ "fastqc/0.10.1" ]
    },
    "trimReads": {
        "command": "java -Xmx6g -jar /usr/local/trimmomatic/0.30/trimmomatic-0.30.jar %paired -threads 1 -phred33 -trimlog %trim_log %parameters",
        "walltime": "4:00:00",
        "memInGB": 6,
    },
    "fastqc_trimmed": {
        "command": "fastqc --quiet -o %outdir %seq",
        "walltime": "1:00:00",
        "modules": [ "fastqc/0.10.1" ]
    },
    'gUnzip': {
        "command": "gunzip -c %seq > %out",
        "walltime": "0:30:00",
        "memInGB": 4
    },
    'alignBismark': {
        'command': "bismark --bowtie2 --non_directional -o %output_dir --score_min L,0,-0.6 --minins 0 --maxins 1000 --un --ambiguous -N 1 -L 16 -D 20 -R 5 -p 4 %ref_dir -1 %seq1 -2 %seq2",
        'walltime': "48:00:00",
        'queue': 'smp',
        'memInGB': 64
    },
    'alignBismarkSE_R1': {
        'command': "bismark --bowtie2 --non_directional -o %output_dir --score_min L,0,-0.6 --un --ambiguous -N 1 -L 16 -D 20 -R 5 -p 4 %ref_dir %seq",
        'walltime': "48:00:00",
        'queue': 'smp',
        'memInGB': 64
    },
    'alignBismarkSE_R2': {
        'command': "bismark --bowtie2 --non_directional -o %output_dir --score_min L,0,-0.6 --un --ambiguous -N 1 -L 16 -D 20 -R 5 -p 4 %ref_dir %seq",
        'walltime': "48:00:00",
        'queue': 'smp',
        'memInGB': 64
    },
#    'alignBWA': {
#        'command': "bwa aln -t 8 -n 0.01 -o 2 -d 12 -e 12 -l 150 %encodingflag %ref %seq > %out",
#        'walltime': "4:00:00",
#        'queue': 'smp',
#        'memInGB': 23
#    },
#    'alignToSamSE': {
#        'command': "bwa samse %ref %meta %align %seq > %out"
#    },
#    'alignToSamPE': {
#        'command': "bwa sampe %ref %meta %align1 %align2 %seq1 %seq2 > %out"
#    },
    'samToSortedBam': {
        'command': "java -Xmx4g -Djava.io.tmpdir=`pwd`/picard_tmp -jar /usr/local/picard/1.69/lib/SortSam.jar VALIDATION_STRINGENCY=LENIENT INPUT=%seq OUTPUT=%out SORT_ORDER=coordinate TMP_DIR=`pwd`/picard_tmp",
        'memInGB': 64,
        'walltime': "6:00:00",
    },
    'mergeBams': {
        'command': "java -Xmx4g -jar /usr/local/picard/1.69/lib/MergeSamFiles.jar %baminputs USE_THREADING=true VALIDATION_STRINGENCY=LENIENT AS=true OUTPUT=%out",
        'walltime': "72:00:00"
    },
    'indexBam': {
        'command': "samtools index %bam"
    },
    'fixReadGroups': {
        'walltime': "01:00:00",
        'command': "java -Xmx6g -jar /usr/local/picard/1.69/lib/AddOrReplaceReadGroups.jar INPUT=%input_bam OUTPUT=%output_bam %readgroup_string"
    },
    'flagstat': {
        'command': "samtools flagstat %bam > %out",
        'walltime': "00:10:00"
    },
    'igvcount': {
        'command': "igvtools count %bam %out hg19",
        'modules': [ "igvtools/2.3.15" ]
    },
    'indexVCF': {
        'command': "./vcftools_prepare.sh %vcf",
        'modules': [ "tabix/0.2.5" ]
    },
    'realignIntervals': {
        'command': "java -Xmx6g -jar /usr/local/gatk/3.2-2/GenomeAnalysisTK.jar --num_threads 8 -T RealignerTargetCreator -R %ref %bam_flags --log_to_file %log -o %out",
        'memInGB': 23,
        'walltime': "12:00:00"
    },
    'realign': {
        'command': "java -Xmx55g -jar /usr/local/gatk/3.2-2/GenomeAnalysisTK.jar  -T IndelRealigner -R %ref %bam_flags -targetIntervals %intervals --log_to_file %log --nWayOut dedup.realigned.2.bam",
        'memInGB': 63,
        'walltime': "30:00:00"
    },
    'dedup': {
        'command': "java -Xmx6g -jar /usr/local/picard/1.69/lib/MarkDuplicates.jar INPUT=%bam REMOVE_DUPLICATES=true VALIDATION_STRINGENCY=LENIENT AS=true METRICS_FILE=%log OUTPUT=%out",
        'memInGB': 23,
        'walltime': '7:00:00'
    },
    'freebayes1':{
#        'command': "freebayes -b %bam0 -b %bam1 -b %bam2 -b %bam3 -b %bam4 -b %bam5 -b %bam6 -b %bam7 -b %bam8 -b %bam9 --fasta-reference %ref --vcf %output_vcf --populations populations.txt --pooled-discrete --use-best-n-alleles 2 --ploidy 10 --hwe-priors-off --min-alternate-fraction 0.1 --min-alternate-count 5",
        'command': "freebayes -b %bam0 -b %bam1 -b %bam2 -b %bam3 -b %bam4 -b %bam5 -b %bam6 -b %bam7 -b %bam8 -b %bam9 --fasta-reference %ref --vcf %output_vcf --populations populations.txt --pooled-continuous --use-best-n-alleles 2 --ploidy 2 --hwe-priors-off --min-alternate-fraction 0.2 --min-alternate-total 50 --min-coverage 500",
        'memInGB': 135,
        'walltime': '36:00:00'
    },
    'selectHighQualVariants':{
        'command': 'java -Xmx6g -jar /usr/local/gatk/3.2-2/GenomeAnalysisTK.jar -R %ref -T SelectVariants -nt 8 --variant %input_vcf -o %output_vcf -select "QUAL > 1000.0 && DP > 500"',
        'memInGB': 23,
        'walltime':'7:00:00'
    },
    'baseQualRecalCount': {
        'command': "java -Xmx6g -jar /usr/local/gatk/2.6-5/GenomeAnalysisTK.jar -T CountCovariates -I %bam -R %ref --knownSites %dbsnp -nt 8 -l INFO -cov ReadGroupCovariate -cov QualityScoreCovariate -cov CycleCovariate -cov DinucCovariate -log %log -recalFile %out",
        'queue': 'smp',
        'memInGB': 23,
        'walltime': "3:00:00:00"
    },
    'baseQualRecalTabulate': {
        'command': "./GenomeAnalysisTK 4 -T TableRecalibration -I %bam -R %ref -recalFile %csvfile -l INFO -log %log -o %out",
        'walltime': "3:00:00:00"
    },
    'mpileup': {
        'command': "samtools mpileup -f %ref -q 20 -B %bam_files > %output_mpileup",
        'memInGB': 23,
        'walltime': '36:00:00'
    },
    'mpileuptosync': {
    'command': "java -Xmx5g -jar /vlsci/VR0267/pgriffin/hsm/variant_calling_pipeline/mpileup2sync.jar --input %input_mpileup --output %output_sync --fastq-type sanger --min-qual 20 --threads 8",
    'meminGB': 63,
    'walltime': '36:00:00'
    },
    'cmhTest': {
        'command': "perl /vlsci/VR0267/pgriffin/hsm/variant_calling_pipeline/popoolation2_1201/cmh-test.pl --input %sync --output %out --min-count 4 --min-coverage 20 --max-coverage 200 --population 1-6,2-7,3-8,4-9,5-10",
        'meminGB': 63,
        'walltime': '30:00:00'
    },
    'cmh2gwas': {
        'command': "perl /vlsci/VR0267/pgriffin/hsm/variant_calling_pipeline/popoolation2_1201/export/cmh2gwas.pl --input %test_results --output %gwas --min-pvalue 1.0e-25",
        'meminGB': 63,
        'walltime': '16:00:00'
    },
    'callSNPs': {
    'command': "./GenomeAnalysisTK 12 -T UnifiedGenotyper -nt 8 -R %ref -I %bam --dbsnp %dbsnp -stand_call_conf 50.0 -stand_emit_conf 10.0 -dcov 1600 -l INFO -A AlleleBalance -A DepthOfCoverage -A FisherStrand -glm SNP -log %log -o %out",
    'queue': 'smp',
    'memInGB': 23,
    'walltime': "24:00:00"
    },
    'callIndels': {
    'command': "./GenomeAnalysisTK 12 -T UnifiedGenotyper -nt 8 -R %ref -I %bam --dbsnp %dbsnp -stand_call_conf 50.0 -stand_emit_conf 10.0 -dcov 1600 -l INFO -A AlleleBalance -A DepthOfCoverage -A FisherStrand -glm INDEL -log %log -o %out",
        'queue': 'smp',
        'memInGB': 23,
        'walltime': "24:00:00"
    },
    'filterSNPs': {
        # Very minimal hard filters based on GATK recommendations. VQSR is preferable if possible.
        'command': "./GenomeAnalysisTK 4 -T VariantFiltration -R %ref --variant %vcf --filterExpression 'QD < 2.0 || MQ < 40.0 || FS > 60.0 || HaplotypeScore > 13.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0' --filterName 'GATK_MINIMAL_FILTER' -log %log -o %out",
    },
    'filterIndels': {
        # Very minimal hard filters based on GATK recommendations. VQSR is preferable if possible.
        # If you have 10 or more samples GATK also recommends the filter InbreedingCoeff < -0.8
        'command': "./GenomeAnalysisTK 4 -T VariantFiltration -R %ref --variant %vcf --filterExpression 'QD < 2.0 || ReadPosRankSum < -20.0 || FS > 200.0' --filterName 'GATK_MINIMAL_FILTER' -log %log -o %out",
    },
    'depthOfCoverage': {
        'command': "./GenomeAnalysisTK 4 -T DepthOfCoverage -R %ref -I %bam -omitBaseOutput -ct 1 -ct 10 -ct 20 -ct 30 -o %out",
    },
    'collateReadcounts': {
        'command': 'python count_flagstat_wgs.py %dir %outdir',
        'walltime': "8:00:00"
    }
}
