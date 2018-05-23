# @author Daniel Vliegenthart
# Generate pdfs overview files for booktitles

import argparse
import operator
import csv
import re
import urllib3
from operator import itemgetter
import os
from config import booktitles, ROOTPATH, facets, use_in_viewer, min_ne_threshold, nr_top_papers, nr_top_papers_cited
import unidecode
from shutil import copyfile, rmtree

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


top_full_text = f'{ROOTPATH}/data/top_full_text/'

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

  # ############################################# #
  #      GENERATE OVERVIEW FILES FOR TOP CITED    #
  # ############################################# #

  # Reset top full texts dir
  try:
    rmtree(top_full_texts)
  except:
    pass

  os.makedirs(os.path.dirname(top_full_text), exist_ok=True)

  for booktitle in booktitles:
    papers = read_overview_csv(database, booktitle, 0, 1)

    # Needs to have PDF paper
    papers_has_pdf = [paper for paper in papers if paper[1] == 'true']

    # Needs to have citations fetched from Google Scholar
    papers_has_pdf = [paper for paper in papers_has_pdf if int(paper[3]) > -1]
    papers_has_pdf.sort(key=lambda x: int(x[3]), reverse=True)

    # Only keep nr_top_papers_cited
    papers_has_pdf = copy_full_texts(papers_has_pdf, database, nr_top_papers_cited)

    # Generate overview files for booktitle
    write_arrays_to_csv(papers_has_pdf, booktitle, database, ['paper_id', 'has_pdf', facets_columns, 'number_citations', 'booktitle', 'pdf_url', 'year', 'title', 'type', 'authors'], nr_top_papers_cited) 

# Copy full texts to final selection
def copy_full_texts(papers, database, nr_top_papers_cited):
  top_papers_with_full_text = []
  counter = 0

  for paper in papers:
    if counter >= nr_top_papers_cited: continue
    file_name = paper[0]+".txt"

    src = f'{ROOTPATH}/data/{database}/{paper[4].lower()}/full_text/{file_name}'
    dst = f'{top_full_text}{file_name}'
    try:
      copyfile(src, dst)
      counter += 1
      top_papers_with_full_text.append(paper)
    except:
      pass

  return top_papers_with_full_text

# Parse string separated by ; to sum of integers
def nr_ne(entity_string):
  return sum(map(int, entity_string.split(";")))

# Read papers and number entities overview file
def read_overview_csv(database, booktitle, skip, version):
  file_path = f'{ROOTPATH}/data/{database}/{booktitle.lower()}/{booktitle.lower()}_papers_overview_total.csv'
  csv_raw = open(file_path, 'r').readlines()
  csv_raw = [line.rstrip('\n').split(',') for line in csv_raw]
  csv_raw.pop(0) # Remove header column
  
  return csv_raw

# Write list of tuples to csv file
def write_arrays_to_csv(array_list, booktitle, database, column_names, top):
  file_path = f'{ROOTPATH}/data/total/{booktitle.lower()}_papers_top_{top}_by_citations.csv'
  os.makedirs(os.path.dirname(file_path), exist_ok=True)

  with open(file_path, 'w+') as outputFile:
    csv_out=csv.writer(outputFile)
    csv_out.writerow(column_names)
    
    for array1 in array_list:
      csv_out.writerow(array1)

if __name__=='__main__':
  main()



