#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class:  CommandLineTool
baseCommand: qc-fastq
inputs:
  file:
    type: File
    inputBinding:
      position: 1
outputs:
  processed:
    type: File
    outputBinding:
      glob: *
