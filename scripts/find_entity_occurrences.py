# @author Daniel Vliegenthart

# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import re
from process_methods import find_pdf_terms_in_sent_tsv, read_entity_set
from process_xhtml import read_xhtml, enrich_xhtml
import statistics
from config import ROOTPATH, PDFNLT_PATH, facets, tse_ner_conferences
import os
import json
import csv

generate_overview = True

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
  
  # find_occurrences_unfiltered(database)
  find_occurrences_doubly(database)

def find_occurrences_doubly(database):
  facet = "doubly"
  total_occurrences = []
  
  # GENERATE OVERVIEW IF FILTERING NOT APPLICABLE
  if generate_overview: generate_paper_overviews(database, tse_ner_conferences, "doubly")
  
  for conf in tse_ner_conferences:
    booktitle = conf.lower()

    papers = read_overview_csv(booktitle)
  
    for paper in papers:

      pdf_name = paper[2]

      pdf_term_info_list = find_pdf_terms_in_sent_tsv(database, facet, pdf_name, booktitle)
      term_occurrences = [e.text for e in pdf_term_info_list if len(e.pdf_terms) > 0]

      occ_path = f'data/occurrence_sets_doubly/'
      os.makedirs(os.path.dirname(occ_path), exist_ok=True)

      with open(f'{occ_path}/occurrence_set_doubly_{booktitle.lower()}__{pdf_name}__0.txt', 'w+') as outputFile:
        for t in term_occurrences:
          outputFile.write(f'{t}\n')

      total_occurrences.append([pdf_name, term_occurrences, paper[1]])

      xhtml_soup = read_xhtml(f'data/xhtml_enriched/{pdf_name}.xhtml')
      
      if xhtml_soup:
        body = xhtml_soup.find("body")
        if not body.get('class') or (body.get('class') and not f'enriched-{facet}' in body.get('class')):
          enrich_xhtml(pdf_term_info_list, xhtml_soup, database, facet, pdf_name, booktitle)

  total_occurrences = [paper for paper in total_occurrences if paper[0].split("_")[1].upper() in tse_ner_conferences and len(paper[1]) > 0]
  total_occurrences.sort(key=lambda x: (x[0], x[1]))

  with open(f'data/total/{facet}_papers_terms_overview.csv', 'w+') as outputFile:
    outputFile.write("paper_id,number_terms, number_cited\n")
    for [pdf_name, term_occurrences, nr_cited] in total_occurrences:
      outputFile.write(str(len(term_occurrences)) + "," + nr_cited + "," + pdf_name + "\n")

def find_occurrences_unfiltered(database):
  for facet in facets:
    total_occurrences = []
    
    for file_name in os.listdir(f'{ROOTPATH}/data/viewer_pdfs/'):
      if not file_name.endswith(".pdf"): continue

      pdf_name = file_name.strip(".pdf")
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

# Read papers and number entities overview file
def read_overview_csv(booktitle, overviews_dir="total/overviews/"):
  file_path = f'{ROOTPATH}/data/{overviews_dir}{booktitle.lower()}_papers_overview.csv'
  csv_raw = open(file_path, 'r').readlines()
  csv_raw = [line.rstrip('\n').split(',') for line in csv_raw if len(line.rstrip('\n').split(',')) > 1]
  csv_raw.pop(0) # Remove header column
  
  return csv_raw

# Generate paper overviews if paper filtering by metadata and occurrences is not applicable
def generate_paper_overviews(database, confs, facet="doubly"):
  for conf in confs:
    papers = []
    for file_name in os.listdir(f'{ROOTPATH}/data/{database}/{conf}/pdf/'):
      if not file_name.endswith(".pdf"): continue

      pdf_name = file_name.strip(".pdf")

      if facet == "doubly":
        entity_set = read_entity_set(f'data/entity_sets_doubly/entity_set_doubly_{conf}__{pdf_name}__0.txt')
      else:
        entity_set = read_entity_set(f'data/{database}/{booktitle.lower()}/entity_set/{facet}_{pdf_name}_entity_set_0.txt')

      len_ent = len([ent.text for ent in entity_set])
      papers.append([len_ent, -1, pdf_name, conf, "NOURLFOUND"])

    write_arrays_to_csv(papers, conf, database, ['nr_doubly', 'number_citations', 'paper_id', 'booktitle', 'pdf_url'])

# Write list of tuples to csv file
def write_arrays_to_csv(array_list, booktitle, database, column_names, overviews_dir="total/overviews/"):
  file_path = f'{ROOTPATH}/data/{overviews_dir}{booktitle.lower()}_papers_overview.csv'
  os.makedirs(os.path.dirname(file_path), exist_ok=True)

  with open(file_path, 'w+') as outputFile:
    csv_out=csv.writer(outputFile)
    csv_out.writerow(column_names)
    
    for array1 in array_list:
      csv_out.writerow(array1)

  print("Wrote overview file for conference:", booktitle)

if __name__=='__main__':

  main()
