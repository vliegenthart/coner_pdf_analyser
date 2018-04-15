# coner_document_analyser
Coner Collaborative NER Pipeline Component: Analyse documents (PDFs)

## Scripts Description
- fetch_publications.py:
  - Parameters: name of database data folder, number of papers to fetch from database, number of items to skip from returned collection, versioning number used to name overview csv for databases
  - Description: Fetches papers from conferences as indicated in the 'booktitles' array; meta-data from server, various download methods for PDF, full text and number of citations retrieval
  - Example script execution: `python fetch_publications.py tse_ner 20000 0 1`
  - Booktitles usage should be set in the script itself


- generate_pdfs_overview.py:
  - Parameters: name of database data folder
  - Description: Generates a new overview of fetched papers for conferences filtered on presence of pdf file and sorted on number of citations per paper
  - Example script execution: `python generate_pdfs_overview.py tse_ner` 
  - Booktitles usage should be set in the script itself


