cwlVersion: v1.0
class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: MultipleInputFeatureRequirement
  # - class: DockerRequirement

inputs:
  fastq_files:
    doc: A list of sequence files in fastq format
    type: File
  reference_database:
    doc: blast formatted index fastq_files
    type: File[]

outputs:
  preprocessed:
    type: File
    outputSource: [qc/processed]
  sims:
    type: File
    outputSource: [similaritySearch/similarities]

steps:

  qc:
    label: Quality Control
    doc: Filtering and removing reads below a certain quality threshold
    run: qc.cwl
    # scatter: [filter]
    # scatterMethod: dotproduct
    in:
      filter: fastq_files
    out: [processed]

  similaritySearch:
    # label: none
    doc: none
    run: Similarity-Search.cwl
    # scatter: [nucleotide_sequences]
    # scatterMethod: dotproduct
    in:
      db: reference_database
      nucleotide_sequences: qc/processed
    out: [similarities]
