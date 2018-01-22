cwlVersion: v1.0
class: Workflow

# optional - additional requirements to execute this workflow
requirements:
  - class: InlineJavascriptRequirement

# required, workflow input mapping
inputs:
  pdf:
    type: File
    doc: PDF file for text extraction

# output mapping
# outputs: <LIST OF NAMED OUTPUTS AND MAPPING \
#          FROM TOOL OUTPUT TO WORKFLOW OUTPUT>

# list of workflow steps
steps:
  # step name
  pdf2text:
    label: pdf2text
    doc: extract ascii text from PDF
    # path to tool
    run: ../Tools/pdftotext.cwl
    # assign values to step/tool inputs
    in:
      # assign workflow input to tool input:
      # <tool input name>:<workflow input name>
      pdf: pdf
      text:
        # assign constant output file name
        default: "extracted.txt"

    out: [extractedText]

outputs:
  words:
    type: File
    outputSource: pdf2text/extractedText
