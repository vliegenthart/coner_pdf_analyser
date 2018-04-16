# @author Daniel Vliegenthart

# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import re
from process_methods import find_pdf_terms_in_sent_tsv
from process_xhtml import read_xhtml, enrich_xhtml
import statistics
from config import ROOTPATH, PDFNLT_PATH, facets, viewer_pdfs
import os

def main():

  # ################### #
  #      SETUP ARGS     #
  # ################### #

  # TODO:
  # For multi-file input support check PDFNLT main.py

  parser = argparse.ArgumentParser(description='Annotate xhtml file with term set')

  parser.add_argument('database', metavar='Database', type=str,
                     help='database name of data collection')
  

  args = parser.parse_args()
  database = args.database

  # ####################### #
  #      INIT VARIABLES     #
  # ####################### #
  
  # TODO:
  # Create separate config file for more beautiful setup

  # statistics.init()
  total_occurrences = []

  # ############################### #
  #      ENRICH XHTML WITH TERMS    #
  # ############################### #
  
  for facet in facets:
    for booktitle, pdf_name in viewer_pdfs:
      booktitle = booktitle.lower()
      pdf_term_info_list = find_pdf_terms_in_sent_tsv(database, facet, pdf_name, booktitle)

      term_occurrences = [e.text for e in pdf_term_info_list if len(e.pdf_terms) > 0]

      occ_path = f'data/{database}/{booktitle}/occurrence_set/'
      os.makedirs(os.path.dirname(occ_path), exist_ok=True)

      with open(f'{occ_path}/{facet}_{pdf_name}_occurrence_set_0.txt', 'w+') as outputFile:
        for t in term_occurrences:
          outputFile.write(f'{t}\n')

      total_occurrences.append(term_occurrences)

      xhtml_soup = read_xhtml(f'data/xhtml_enriched/{pdf_name}.xhtml')
      
      body = xhtml_soup.find("body")
      if not body.get('class') or (body.get('class') and not f'enriched-{facet}' in body.get('class')):
        enrich_xhtml(pdf_term_info_list, xhtml_soup, database, facet, pdf_name, booktitle)

    with open(f'data/{database}/{booktitle}/{facet}_papers_terms_overview.csv', 'w+') as outputFile:
      outputFile.write("paper_id,number_terms\n")
      for term_occurrences in total_occurrences:
        outputFile.write(pdf_name + "," + str(len(term_occurrences)) + "\n")

if __name__=='__main__':

  main()
