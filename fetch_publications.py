# @author Daniel Vliegenthart
# Fetch data and write information files for certain number of papers information

import argparse
from pymongo import MongoClient
import operator
import csv
import re
import urllib3
import os
from config import booktitles, ROOTPATH, facets
from lib import scholar

def main():

  # ################### #
  #      SETUP ARGS     #
  # ################### #

  # TODO:
  # For multi-file input support check PDFNLT main.py

  parser = argparse.ArgumentParser(description='Fetch all information for papers')
  parser.add_argument('database', metavar='Database', type=str,
                     help='database name of data collection')
  parser.add_argument('number_papers', metavar='Number of Papers', type=int,
                     help='number of papers to be downloaded')

  args = parser.parse_args()
  database = args.database
  number_papers = args.number_papers

  client = MongoClient('localhost:4321')
  db = client.pub
  booktitles = ['TREC']

  # ########################### #
  #      FETCH PUBLICATIONS     #
  # ########################### #

  # print("Fetching publication information from TSE-NER server; publication attributes, has_pdf, number_entities, #citations_pub, #citations_author: ")

  for booktitle in booktitles:
    print(f'Fetching publications information for conference: {booktitle}')
    papers = []
    paper_info = [] #[_id, number_entities, year, ee, dblpkey, journal, title, type]
    counter_pub = 0
    counter_pdf = 0
    facets_columns = ';'.join(facets)
    results = db.publications.find({ 'booktitle': booktitle }).limit(number_papers)
    
    scholar.ScholarConf.COOKIE_JAR_FILE = ROOTPATH + ".scholar-cookies.txt"
    querier = scholar.ScholarQuerier()
    settings = scholar.ScholarSettings()
    querier.apply_settings(settings)
    query = scholar.SearchScholarQuery()

    for pub in results:
      author1 = pub['authors'][0]
      title = pub['title'].lower().capitalize().strip('.')
      paper_info = [pub['_id'], 'false', '0;0', '0', booktitle, pub['ee'], pub['year'], "'%s'" % title, pub['type'], 'author1;author2']

      # Set author info
      authors = ''
      for author in pub['authors']:
        authors += f'{author};'
      paper_info[9] = authors.strip(';')

      # Have multiple PDF fetch methods: Direct EE link, Arxiv
      if pub['ee'][-4:].lower() == '.pdf': 
        paper_info[1] = 'true'

      # Get distinct #entities for total facets
      facets_entities = ''
      for facet in facets:
        entities = fetch_paper_entities(pub['_id'], facet, db)
        facets_entities += f'{len(entities)};'

        # Write paper facet entity set to TXT
        write_entity_set_file(pub['_id'], booktitle, entities, database, facet)

      paper_info[2] = facets_entities.strip(';')

      papers.append(paper_info)
      print(f'✓ {pub["_id"]}')

      # Get number of citations info
      # query.set_author(author1)
      # query.set_phrase(title)
      # query.set_num_page_results(1)
      # querier.send_query(query)
      # querier.save_cookies()

      # print(querier.articles)

      # # # Print the URL of the first article found
      # if querier.articles:
      #   if not title == querier.articles[0]['title'].lower().capitalize().strip('.'):
      #     print(title)
      #   print(querier.articles[0]['title'], ":", querier.articles[0]['num_citations'], querier.articles[0]['url_pdf'])
      # # print(querier.articles[0]['num_citations'], querier.articles[0]['url_pdf'])

    # Write papers information to CSV file
    write_arrays_to_csv(papers, booktitle, database, ['paper_id', 'has_pdf', facets_columns, 'number_citations', 'booktitle', 'pdf_url', 'year', 'title', 'type', 'authors'])


# Fetch number of named entities for each papers in specific journal with facet
def fetch_paper_entities(paper_id, facet, db):
  papers_entities = {}
  results = db.named_entities.find({'$and': [{'paper_id': paper_id}, { 'label': facet}]})

  entities = []
  for ne in results: entities.append(ne['word'])

  return list(set(entities))

# Write list of tuples to csv file
def write_arrays_to_csv(array_list, booktitle, database, column_names):
  file_path = f'{ROOTPATH}/data/{database}/{booktitle.lower()}/{booktitle.lower()}_papers_overview.csv'
  os.makedirs(os.path.dirname(file_path), exist_ok=True)

  with open(file_path, 'w+') as outputFile:
    csv_out=csv.writer(outputFile)
    csv_out.writerow(column_names)
    
    for array1 in array_list:
      csv_out.writerow(array1)

def write_entity_set_file(paper_id, booktitle, entities, database, facet):
  file_path = f'{ROOTPATH}/data/{database}/{booktitle.lower()}/entity_set/{facet}_{paper_id}_entity_set_0.txt'
  os.makedirs(os.path.dirname(file_path), exist_ok=True)
  with open(file_path, 'w+') as outputFile:
    for e in entities:
      outputFile.write(f'{e}\n')

if __name__=='__main__':
  main()



