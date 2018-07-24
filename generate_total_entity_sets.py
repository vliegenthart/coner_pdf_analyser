# @author Daniel Vliegenthart

import argparse
import re
from config import ROOTPATH, PDFNLT_PATH, facets
import os

def main():

  # ################### #
  #      SETUP ARGS     #
  # ################### #

  parser = argparse.ArgumentParser(description='Annotate xhtml file with term set')

  parser.add_argument('database', metavar='Database', type=str,
                     help='database name of data collection')
  
  args = parser.parse_args()
  database = args.database

  # ####################### #
  #      INIT VARIABLES     #
  # ####################### #
  

  # ############################### #
  #      ENRICH XHTML WITH TERMS    #
  # ############################### #
  
  for facet in facets:
    total_entities = []
    for file_name in os.listdir(f'{ROOTPATH}/data/viewer_pdfs/'):
      if not file_name.endswith(".pdf"): continue


      name = file_name.strip(".pdf")
      booktitle = file_name.split("_")[1].lower()

      entities = read_entity_set(database, booktitle, facet, name)
      total_entities += entities
      print(facet, name, (len(entities)))


    total_entities = list(set(total_entities))

    with open(f'data/total/{facet}_all_entities.txt', 'w+') as outputFile:
      for entity in total_entities:
        outputFile.write(entity + "\n")

def read_entity_set(database, booktitle, facet, name):
  file_path = f'{ROOTPATH}/data/{database}/{booktitle}/occurrence_set/{facet}_{name}_occurrence_set_0.txt'
  set_raw = open(file_path, 'r').readlines()
  set_raw = [line.rstrip('\n') for line in set_raw]
  
  return set_raw

if __name__=='__main__':

  main()
