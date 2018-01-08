#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class:  CommandLineTool
label: Similarity Search
doc: Nucleotide sequence similarity search using blastx
hints:
  - class: DockerRequirement
    dockerPull: mgrast/demo:demo

requirements:
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing: $(inputs.db)

baseCommand: blastx

arguments:
  - valueFrom: $(inputs.db[0].nameroot)
    prefix: -db
  - valueFrom: $(inputs.nucleotide_sequences.nameroot).sims
    prefix: -out

inputs:
  db:
    type: File[]
  nucleotide_sequences:
    type: File
    inputBinding:
      prefix: -query
  output_format:
    type: string
    default: "6"
    inputBinding:
      prefix: -outfmt
outputs:
  similarities:
    type: File
    outputBinding:
      glob: $(inputs.nucleotide_sequences.nameroot).sims
