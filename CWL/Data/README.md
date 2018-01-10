The demo workflow requires a sequence reference database. The reference database has been created using following commands:

1. wget ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz
2. unzip uniprot_sprot.fasta.gz
3. makeblastdb -in uniprot_sprot.fasta -dbtype prot -title swissprot -out swissprot -parse_seqids
4. blastx -db swissprot -query filtered.fasta -outfmt 6 -out output.tsv
5. cut -f2 -filtered output.tsv | sort -u | head -n 5000 > matched_sequences.subset
6. blastdbcmd -db swissprot -entry_batch matched_sequences.subset > demo_reference_db.fasta
7. makeblastdb -in demo_reference_db.fasta -dbtype prot -title DemoDB -out demodb -parse_seqids
