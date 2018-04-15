# @author Daniel Vliegenthart
# Generate pdfs overview files for booktitles


import argparse
from pymongo import MongoClient
import operator
import csv
import re
import urllib3
from operator import itemgetter
from statistics import mean

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
from config import booktitles, ROOTPATH, facets
from lib import scholar
# https://github.com/lukasschwab/arxiv.py
# https://github.com/titipata/arxivpy
import arxiv

import unidecode

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
  booktitles = ['ICWSM']

  # ########################### #
  #      FETCH PUBLICATIONS     #
  # ########################### #

  # print("Fetching publication information from TSE-NER server; publication attributes, has_pdf, number_entities, #citations_pub, #citations_author: ")

  for booktitle in booktitles:
    papers = read_overview_csv(database, booktitle, 0, 1)
    papers_has_pdf = [paper for paper in papers if paper[1] == 'true']
    papers_has_pdf.sort(key=lambda x: int(x[3]), reverse=True)
    citations_list = [int(row[3]) for row in papers_has_pdf]

    print('----- STATISTICS -----')
    print("Papers with PDF:", str(len(papers_has_pdf)) + '/' + str(len(papers)))
    print("Max number citations for paper:", papers_has_pdf[0][3])
    print("Average number citations per paper:", round(sum(citations_list)/len(citations_list),1))
    write_arrays_to_csv(papers_has_pdf, booktitle, database, ['paper_id', 'has_pdf', facets_columns, 'number_citations', 'booktitle', 'pdf_url', 'year', 'title', 'type', 'authors'])
    print('-----------------------')

# Read papers and number entities overview file
def read_overview_csv(database, booktitle, skip, version):
  file_path = f'{ROOTPATH}/data/{database}/{booktitle.lower()}/{booktitle.lower()}_papers_overview_{skip}_v{version}.csv'
  csv_raw = open(file_path, 'r').readlines()
  csv_raw = [line.rstrip('\n').split(',') for line in csv_raw]
  csv_raw.pop(0) # Remove header column
  
  return csv_raw

# Write list of tuples to csv file
def write_arrays_to_csv(array_list, booktitle, database, column_names, version=1):
  file_path = f'{ROOTPATH}/data/{database}/{booktitle.lower()}/{booktitle.lower()}_papers_has_pdf_v{version}.csv'
  os.makedirs(os.path.dirname(file_path), exist_ok=True)

  with open(file_path, 'w+') as outputFile:
    csv_out=csv.writer(outputFile)
    csv_out.writerow(column_names)
    
    for array1 in array_list:
      csv_out.writerow(array1)

if __name__=='__main__':
  main()



