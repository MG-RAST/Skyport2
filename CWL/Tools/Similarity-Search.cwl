#!/usr/bin/env cwl-runner

class:  CommandLineTool
label: Similarity Search
doc: Nucleotide sequence similarity search using blastx
hints:
  - class: DockerRequirement
    dockerPull: mgrast/demo:demo
baseCommand: blastp
inputs:
  db:
    type: File
    inputBinding:
      prefix: -db
outputs:
  similarities:
    type: File
    outputBinding:
      glob: *
