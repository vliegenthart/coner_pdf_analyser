# @author Daniel Vliegenthart
# Generate pdfs overview files for booktitles

import argparse
import operator
import csv
import re
import urllib3
from operator import itemgetter
import os
from config import booktitles, ROOTPATH, facets, use_in_viewer, min_ne_threshold, nr_top_papers, seedsize, iteration
import unidecode
from shutil import copyfile, rmtree

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():

  # ################### #
  #      SETUP ARGS     #
  # ################### #

  parser = argparse.ArgumentParser(description='Fetch all information for papers')
  parser.add_argument('database', metavar='Database', type=str,
                     help='database name of data collection')

  args = parser.parse_args()
  database = args.database
  facets_columns = ';'.join(facets)
  booktitles = use_in_viewer
  # TEMP CHANGE
  version = 3

  total_papers = []
  total_papers_has_pdf = []
  total_citations_list = []
  total_nr_entities_list = []
  total_nr_entities_filtered_list = []

  # Reset data/viewer_pdfs directory
  base_path = f'{ROOTPATH}/data'
  viewer_pdfs = f'{base_path}/viewer_pdfs/'
  rmtree(viewer_pdfs)
  os.makedirs(os.path.dirname(viewer_pdfs), exist_ok=True)

  # ########################################### #
  #      GENERATE OVERVIEW FILES FOR HAS PDF    #
  # ########################################### #

  for booktitle in booktitles:
    papers = read_overview_csv(database, booktitle, seedsize, iteration)
    total_papers.extend(papers)

    # Needs to have PDF paper
    papers_has_pdf = [paper for paper in papers if paper[1] == 'true']
    nr_entities_list = [nr_ne(paper[2]) for paper in papers_has_pdf]

    # TEMP CHANGE
    # TEMP FILTERING OUT OF PUBLICATIONS WITHOUT EXTRACTED ENTITIES UNTILL CAN RUN TSE-NER
    # Needs to have at least config.min_ne total extracted entities
    papers_has_pdf = [paper for paper in papers_has_pdf if nr_ne(paper[2]) >= min_ne_threshold]
    nr_entities_filtered_list = [nr_ne(paper[2]) for paper in papers_has_pdf]

    # Needs to have citations fetched from Google Scholar
    papers_has_pdf = [paper for paper in papers_has_pdf if int(paper[3]) > -1]
    citations_list = [int(paper[3]) for paper in papers_has_pdf]
    papers_has_pdf.sort(key=lambda x: int(x[3]), reverse=True)

    # Generate overview files for booktitle
    write_arrays_to_csv(papers_has_pdf, booktitle, database, ['paper_id', 'has_pdf', facets_columns, 'number_citations', 'booktitle', 'pdf_url', 'year', 'title', 'type', 'authors'], seedsize, iteration)

    # Copy PDFs of top config.nr_top_papers to data/viewer_pdfs/
    for paper in papers_has_pdf[:nr_top_papers]:
      file_name = paper[0]+".pdf"
      src = f'{base_path}/{database}/{paper[4]}/pdf/{file_name}'
      dst = f'{viewer_pdfs}{file_name}'
      copyfile(src, dst)

    # Extend lists to generate total overview file for all booktitles
    total_papers_has_pdf.extend(papers_has_pdf)
    total_citations_list.extend(citations_list)
    total_nr_entities_list.extend(nr_entities_list)
    total_nr_entities_filtered_list.extend(nr_entities_filtered_list)

    print('----- STATISTICS -----')
    print("BOOKTITLE:", booktitle)
    if len(papers_has_pdf) is 0:
      print("No papers found with PDF and extracted entities...")
      print('-----------------------\n')
      continue
    else:
      print("Papers with PDF and fetched citations:", str(len(papers_has_pdf)) + "/" + str(len(papers)))
      print("Max number citations for paper:", papers_has_pdf[0][3])
      print("Average number citations per paper:", round(sum(citations_list)/len(citations_list),1))
      print("Max number entities for paper:", max(nr_entities_list))
      print("Average number entities per paper (filtered has_pdf):", round(sum(nr_entities_list)/len(nr_entities_list),1))
      print("Average number entities per paper (filtered has_pdf, citations and ne threshold):", round(sum(nr_entities_filtered_list)/len(nr_entities_filtered_list),1))

    print('-----------------------\n')

  # Concatenated results from all papers
  total_papers_has_pdf.sort(key=lambda x: int(x[3]), reverse=True)
  write_arrays_to_csv(total_papers_has_pdf, 'total', 'total', ['paper_id', 'has_pdf', facets_columns, 'number_citations', 'booktitle', 'pdf_url', 'year', 'title', 'type', 'authors'], seedsize, iteration)

  # Print final statistics
  print('----- TOTAL STATISTICS -----')
  if len(total_papers_has_pdf) is 0:
    print("No papers found with PDF and extracted entities...")
  else:
    print("Papers with PDF and fetched citations:", str(len(total_papers_has_pdf)) + "/" + str(len(total_papers)))
    print("Max number citations for paper:", total_papers_has_pdf[0][3])
    print("Average number citations per paper:", round(sum(total_citations_list)/len(total_citations_list),1))
    print("Max number entities for paper:", max(total_nr_entities_list))
    print("Average number entities per paper (filtered has_pdf):", round(sum(total_nr_entities_list)/len(total_nr_entities_list),1))
    print("Average number entities per paper (filtered has_pdf, citations and ne threshold):", round(sum(total_nr_entities_filtered_list)/len(total_nr_entities_filtered_list),1))

  print('-----------------------------\n')

# Parse string separated by ; to sum of integers
def nr_ne(entity_string):
  return sum(map(int, entity_string.split(";")))

# Read papers and number entities overview file
def read_overview_csv(database, booktitle, seedsize, iteration):
  file_path = f'{ROOTPATH}/data/{database}/{booktitle.lower()}/{booktitle.lower()}_papers_overview_total_limited_{seedsize}_{iteration}.csv'
  csv_raw = open(file_path, 'r').readlines()
  csv_raw = [line.rstrip('\n').split(',') for line in csv_raw]
  csv_raw.pop(0) # Remove header column
  
  return csv_raw

# Write list of tuples to csv file
def write_arrays_to_csv(array_list, booktitle, database, column_names, seedsize, iteration):
  file_path = f'{ROOTPATH}/data/{database}/{booktitle.lower()}/{booktitle.lower()}_papers_enough_entities_{seedsize}_{iteration}.csv'
  os.makedirs(os.path.dirname(file_path), exist_ok=True)

  with open(file_path, 'w+') as outputFile:
    csv_out=csv.writer(outputFile)
    csv_out.writerow(column_names)
    
    for array1 in array_list:
      csv_out.writerow(array1)

if __name__=='__main__':
  main()
