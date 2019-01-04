#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class:  CommandLineTool
label: QC Fastq File
hints:
  - class: DockerRequirement
    dockerPull: mgrast/demo:demo
baseCommand: vsearch
arguments:
  - prefix: --fastaout
    valueFrom: "filtered.fasta"
  - prefix:  --fastaout_discarded
    valueFrom: "discarded.fasta"
inputs:
  filter:
    type: File
    inputBinding:
      position: 1
      prefix:  --fastq_filter
  maximum_expected_error_rate:
    type: float
    default: 0.03
    inputBinding:
      prefix: --fastq_maxee_rate
outputs:
  processed:
    type: File
    outputBinding:
      glob: "filtered.fasta"
  discarded:
    type: File
    outputBinding:
      glob: "discarded.fasta"
