# @author Daniel Vliegenthart

import os
import time
import csv
from config import ROOTPATH, PDFNLT_PATH, facets, max_entity_words, tse_ner_conferences, iteration

base_entity_set_path = f'{ROOTPATH}/data/entity_sets'
database = 'tse_ner'

def main():
  # clean_entity_sets()

  find_doubly_entities(iteration)


def find_doubly_entities(iteration):
  filter = 'majority'
  doubly_filt_ent = read_entity_list(f'{ROOTPATH}/data/smartpub_files/doubly_classified_entities_{filter}_{iteration}.txt')

  print(len(doubly_filt_ent))

  for conference in tse_ner_conferences:
    overview = read_overview_csv(database, conference)
    missing_paper = 0

    for paper in overview:
      facet_entities = []
      for facet in facets:
        file_path = f'{base_entity_set_path}/entity_set_{facet}_{conference.lower()}__{paper[0]}__{iteration}.txt' 
        if os.path.exists(file_path):
          facet_entities+= read_entity_list(file_path)
        else:
          missing_paper +=1
          facet_entities = []
          break

      facet_entities = list(set(facet_entities))
      doubly_ent = [entity for entity in facet_entities if entity in doubly_filt_ent]
      paper[2] = len(doubly_ent)
      # print(len(facet_entities), len(doubly_ent), paper[0])

      file_path = f'{ROOTPATH}/data/entity_sets_doubly/entity_set_doubly_{facet}_{conference.lower()}__{paper[0]}__{iteration}.txt' 
      write_entity_set_file(file_path, doubly_ent)


    write_arrays_to_csv(overview, conference, database, iteration, ['paper_id', 'has_pdf', 'nr_doubly', 'number_citations', 'booktitle', 'pdf_url', 'year', 'title', 'type', 'authors'])
    print(conference, missing_paper, len(overview))

# Read papers and number entities overview file
def read_overview_csv(database, booktitle):
  file_path = f'{ROOTPATH}/data/{database}/{booktitle.lower()}/{booktitle.lower()}_papers_overview_total.csv'
  csv_raw = open(file_path, 'r').readlines()
  csv_raw = [line.rstrip('\n').split(',') for line in csv_raw if len(line.rstrip('\n').split(',')) > 1]
  csv_raw.pop(0) # Remove header column
  
  return csv_raw

# Write list of tuples to csv file
def write_arrays_to_csv(array_list, booktitle, database, iteration, column_names):
  file_path = f'{ROOTPATH}/data/total/overviews_doubly/{booktitle.lower()}_papers_overview_total_doubly_{iteration}.csv'
  os.makedirs(os.path.dirname(file_path), exist_ok=True)

  with open(file_path, 'w+') as outputFile:
    csv_out=csv.writer(outputFile)
    csv_out.writerow(column_names)
    
    for array1 in array_list:
      csv_out.writerow(array1)


def clean_entity_sets():
  for file_name in os.listdir(base_path):
    if not file_name.endswith(".txt"): continue

    file_path = f'{base_entity_set_path}/{file_name}'
    entity_set = read_entity_list(file_path)
    entity_set = list(set([entity.lower() for entity in entity_set]))

    write_entity_set_file(file_path, entity_set)

def read_entity_list(file_path):
  global number_entities_rejected
  entity_set_text = list(set(open(file_path, 'r').readlines()))
  entity_set = []

  for entity in entity_set_text:
    entity_temp = entity.rstrip('\n')
    if len(entity_temp.split(' ')) <= max_entity_words:
      entity_set.append(entity_temp.lower())
    else:
      number_entities_rejected+=1

  return entity_set

def write_entity_set_file(file_path, entity_set):

  os.makedirs(os.path.dirname(file_path), exist_ok=True)
  with open(file_path, 'w+') as outputFile:
    for e in entity_set:
      outputFile.write(f'{e}\n')

if __name__=='__main__':

  main()