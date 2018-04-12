# coner_document_analyser
Coner Collaborative NER Pipeline Component: Analyse documents (PDFs)

## Scripts Description
- fetch_publications.py:
  - Parameters: name of database data folder, starting index of returned Mongodb collection (skip no items index: 1), number of papers to fetch from database
  - Description: Fetches papers from conferences as indicated in the 'booktitles' array; meta-data from server, various download methods for PDF, full text and number of citations retrieval
  - Example script execution: `python fetch_publications.py tse_ner 1 20000` 
