# @author Daniel Vliegenthart

# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import re
from process_methods import find_pdf_terms_in_sent_tsv
from process_xhtml import read_xhtml, enrich_xhtml
import statistics
from config import ROOTPATH, PDFNLT_PATH, facets
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

  # ############################### #
  #      ENRICH XHTML WITH TERMS    #
  # ############################### #
  
  for facet in facets:
    total_occurrences = []
    for file_name in os.listdir(f'{ROOTPATH}/data/viewer_pdfs/'):
      pdf_name = file_name.strip(".pdf")
      print(pdf_name)
      booktitle = file_name.split("_")[1].lower()

      pdf_term_info_list = find_pdf_terms_in_sent_tsv(database, facet, pdf_name, booktitle)
      term_occurrences = [e.text for e in pdf_term_info_list if len(e.pdf_terms) > 0]

      occ_path = f'data/{database}/{booktitle}/occurrence_set/'
      os.makedirs(os.path.dirname(occ_path), exist_ok=True)

      with open(f'{occ_path}/{facet}_{pdf_name}_occurrence_set_0.txt', 'w+') as outputFile:
        for t in term_occurrences:
          outputFile.write(f'{t}\n')

      total_occurrences.append([pdf_name, term_occurrences])

      xhtml_soup = read_xhtml(f'data/xhtml_enriched/{pdf_name}.xhtml')
      
      body = xhtml_soup.find("body")
      if not body.get('class') or (body.get('class') and not f'enriched-{facet}' in body.get('class')):
        enrich_xhtml(pdf_term_info_list, xhtml_soup, database, facet, pdf_name, booktitle)

    with open(f'data/total/{facet}_papers_terms_overview.csv', 'w+') as outputFile:
      outputFile.write("paper_id,number_terms\n")
      for [pdf_name, term_occurrences] in total_occurrences:
        outputFile.write(pdf_name + "," + str(len(term_occurrences)) + "\n")

if __name__=='__main__':

  main()
