This directory contains CWL tool and workflow definitions.
All tool and workflow files have a cwl suffix, corresponding job files have the same name but a yaml suffix.

To run the example from within this directory:

1. mkdir tmp
2.  cwl-runner ----tmp-outdir-prefix `pwd`/tmp Workflows/simple-bioinformatic-example.cwl Workflows/simple-bioinformatic-example.job.yaml
