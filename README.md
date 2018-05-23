# coner_document_analyser
Coner Collaborative NER Pipeline Component: Analyse documents (PDFs)

## Scripts Description
Run these scripts in this order to generate entity annotations for desired PDF papers: 

- fetch_publications.py:
  - Parameters: name of database data folder e.g. `tse_ner`, number of papers to fetch from database, number of items to skip from returned collection, versioning number used to name overview csv for databases
  - Description: Fetches papers from conferences as indicated in the 'booktitles' array; meta-data from server, various download methods for PDF, full text and number of citations retrieval
  - Example script execution: `python fetch_publications.py tse_ner 20000 0 1`
  - Booktitles usage should be set in the script itself

- generate_overview_top_by_citations_and_has_pdf.py
- Copy data/top_full_text/ tp TSE-NER
- Copy paper_overview_total.csv to TSE-NER conference directories
- Extract entities from data/top_full_text/ in TSE-NER
- Replace `{conference}_papers_overview_total` here with new one generated in TSE-NER
- Copy and replace new entity sets from TSE-NER if performance better

- generate_pdfs_overview.py:
  - Parameters: name of database data folder e.g. `tse_ner`
  - Description: Generates a new overview of fetched papers for conferences filtered on presence of pdf file and sorted on number of citations per paper. Also generates list of most interesting papers for viewer based on filters and sorting and copies PDFs for top X papers of interesting conference to `data/viewer_pdfs/`
  - Example script execution: `python generate_pdfs_overview.py tse_ner` 
  - Booktitles usage should be set in the script itself

- pdfnlt_find_occurrences.sh:
  - Prerequisites: 
    - Have [PDFNLT](https://github.com/KMCS-NII/PDFNLT-1.0) directory in same parent directory as this project
    - Put PDFs to be analysed in `../PDFNLT/pdfanalyzer/pdf/` directory
    - Each PDF needs entity set files (simple text files where every line contains 1 entity) for each facet with file name location `/data/<database_name>/<conference_name>/entity_set/<facet>_<publication_id>_entity_set_0.txt`
    - Have jruby installed in pfnlt gemset `rvm install jruby-9.1.13.0@pdfnlt`
  - Parameters: Path to directory with PDFs to be analysed e.g. `../PDFNLT/pdfanalyzer/pdf/`
  - Description: Takes PDFs `from data/viewer_pdfs/`, copies them to `../PDFNLT/pdfanalyzer/pdf/` analyses them with PDFNLT to generate files like full text, split up sentences, sentence metadata, xhtml, etc.
  - Example script execution: `bash pdfnlt_find_occurrences.sh tse_ner ../PDFNLT/pdfanalyzer/pdf/`

- copy_pdfnlt_xhtmls_to_local_xhtmls.py:
  - Parameters: name of database data folder e.g. `tse_ner`
  - Description: Copies xhtml files as listed in `data/viewer_pdfs` from `../PDFNLT/pdfanalyzer/xhtml/` to `data/xhtml_raw/` and `data/xhtml_enriched` to prepare for entity extraction and xhtml enrichment for xhtmls
  - Example script execution: `python copy_pdfnlt_xhtmls_to_local_xhtmls.py tse_ner`

- scripts/find_entity_occurrences.py

- GENERATE JS papers-list.js in data/term-highlights.js

- generate_pdf_term_highlights_file.py:
  - Parameters: name of database data folder e.g. `tse_ner`
  - Description: Iterates over publication names in `data/xhtml_enriched/` folder and creates array of all term highlight objects (containing content, position and metadata information) for every term occurrence for every facet in selected publications. Outputs all concatenated highlights in `highlights/term-highlights.js/json`
  - Example script execution: `python generate_pdf_term_highlights_file.py tse_ner` 


