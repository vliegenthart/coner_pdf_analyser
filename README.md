# coner_document_analyser
Coner Collaborative NER Pipeline Component: Analyse documents (PDFs)

## Scripts Description
- fetch_publications.py:
  - Parameters: name of database data folder, number of papers to fetch from database, number of items to skip from returned collection, versioning number used to name overview csv for databases
  - Description: Fetches papers from conferences as indicated in the 'booktitles' array; meta-data from server, various download methods for PDF, full text and number of citations retrieval
  - Example script execution: `python fetch_publications.py tse_ner 20000 0 1` 
