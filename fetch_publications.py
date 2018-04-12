# @author Daniel Vliegenthart
# Fetch data and write information files for certain number of papers information

import argparse
from pymongo import MongoClient
import operator
import csv
import re
import urllib3

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

  # TODO:
  # For multi-file input support check PDFNLT main.py

  parser = argparse.ArgumentParser(description='Fetch all information for papers')
  parser.add_argument('database', metavar='Database', type=str,
                     help='database name of data collection')
  parser.add_argument('starting_index', metavar='Starting Index', type=int,
                     help='starting index of returned Mongodb collection')
  parser.add_argument('number_papers', metavar='Number of Papers', type=int,
                     help='number of papers to be downloaded')

  args = parser.parse_args()
  database = args.database
  number_papers = args.number_papers
  starting_index = args.starting_index

  client = MongoClient('localhost:4321')
  db = client.pub
  booktitles = ['ACL']

  # ########################### #
  #      FETCH PUBLICATIONS     #
  # ########################### #

  # print("Fetching publication information from TSE-NER server; publication attributes, has_pdf, number_entities, #citations_pub, #citations_author: ")

  for booktitle in booktitles:
    papers = []
    paper_info = [] #[_id, number_entities, year, ee, dblpkey, journal, title, type]
    counter_pub = 0
    counter_pdf = 0
    facets_columns = ';'.join(facets)
    results = db.publications.find({ 'booktitle': booktitle }).skip(starting_index-1).limit(number_papers).batch_size(100)
    print(f'Fetching {results.count()} publications information for conference: {booktitle}')

    scholar.ScholarConf.COOKIE_JAR_FILE = ROOTPATH + ".scholar-cookies.txt"
    querier = scholar.ScholarQuerier()
    settings = scholar.ScholarSettings()
    querier.apply_settings(settings)
    scholar_query = scholar.SearchScholarQuery()

    for pub in results:
      if not pub['title'] or not pub['authors']: continue
      author1 = pub['authors'][0]
      counter_pub += 1
      title = pub['title'].lower().capitalize().strip('.')
      paper_info = [pub['_id'], 'false', '-1;-1', '-1', booktitle, pub['ee'], pub['year'], "'%s'" % title, pub['type'], 'author1;author2']
      no_accent_author1 = unidecode.unidecode(author1)

      # Set author info
      authors = ''
      for author in pub['authors']:
        authors += f'{author};'
      paper_info[9] = authors.strip(';')

      pdf_file_path = f'{ROOTPATH}/data/{database}/{booktitle.lower()}/pdf/'
      os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)

      # Have multiple PDF fetch methods: Direct EE link, Arxiv
      # ADD ELSAPY
      if pub['ee'][-4:].lower() == '.pdf': 
        paper_info[1] = 'true'
        download_pdf(pdf_file_path, paper_info[5], database, booktitle, paper_info[0])
      else:
        arxiv_query=f'au:{author1}+AND+ti:{title}'
        articles = arxiv.query(search_query=arxiv_query)
        if articles:
          for art in articles:
            if art['title'].lower().capitalize().strip('.') == title:
              paper_info[5] = art['pdf_url']
              paper_info[1] = 'true'
              arxiv.download(art, pdf_file_path, slugify=True)
              os.rename(f'{pdf_file_path}{to_slug(art["title"])}.pdf', f'{pdf_file_path}{paper_info[0]}.pdf')

              print(f'Finished PDF download for {paper_info[0]}')

      # Download full text
      if 'content' in pub.keys() and 'fulltext' in pub['content'].keys(): write_full_text_file(paper_info[0], database, booktitle, pub['content']['fulltext'])

      # Get distinct #entities for total facets
      # ADD PROPER ENTITIES EXTRACTION
      facets_entities = ''
      for facet in facets:
        entities = fetch_paper_entities(pub['_id'], facet, db)
        facets_entities += f'{len(entities)};'

        # Write paper facet entity set to TXT
        write_entity_set_file(pub['_id'], booktitle, entities, database, facet)

      paper_info[2] = facets_entities.strip(';')

      # Only fetch citations if a PDF has been downloaded
      if paper_info[1] == 'true':  
        counter_pdf += 1    
        # Get number of citations info
        scholar_query.set_author(no_accent_author1)
        scholar_query.set_phrase(title)
        scholar_query.set_num_page_results(1)
        querier.send_query(scholar_query)
        querier.save_cookies()

        # # Print the URL of the first article found
        if querier.articles and title == querier.articles[0]['title'].lower().capitalize().strip('.'):
          print(f'Fetched number citations for {paper_info[0]}: {querier.articles[0]["num_citations"]}')
          paper_info[3] = querier.articles[0]['num_citations']

          # print(querier.articles[0]['title'], ":", querier.articles[0]['num_citations'], querier.articles[0]['url_pdf'])
        # print(querier.articles[0]['num_citations'], querier.articles[0]['url_pdf'])


      # Add paper information to list
      papers.append(paper_info)
      print(f'✓ {pub["_id"]}')

      # Write papers information to CSV file
      if counter_pub % 50 == 0: 
        print('----- STATISTICS -----')
        print("Processed:", counter_pub)
        write_arrays_to_csv(papers, booktitle, database, ['paper_id', 'has_pdf', facets_columns, 'number_citations', 'booktitle', 'pdf_url', 'year', 'title', 'type', 'authors'])
        print(f'PDFs downloaded for {counter_pdf}/{counter_pub} publications for {booktitle}')
        print('----------------------')

    print(f'Finished processing {counter_pub} publications and downloading {counter_pdf} PDFs for {booktitle}')
    # SAVE OVERVIEW OLD FILE

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

def write_full_text_file(paper_id, database, booktitle, full_text):
  file_path = f'{ROOTPATH}/data/{database}/{booktitle.lower()}/full_text/{paper_id}.txt'
  os.makedirs(os.path.dirname(file_path), exist_ok=True)

  file = open(file_path, 'w+')
  file.write(full_text)
  file.close()

def download_pdf(file_path, download_url, database, booktitle, paper_name):
  os.makedirs(os.path.dirname(file_path), exist_ok=True)

  http = urllib3.PoolManager()
  response = http.request('GET', download_url)
  file = open(f'{file_path}{paper_name}.pdf', 'wb')
  file.write(response.data)
  file.close()
  print(f'Finished PDF download for {paper_name}')

def to_slug(title):
  # Remove special characters
  filename = ''.join(c if c.isalnum() else '_' for c in title)
  # delete duplicate underscores
  filename = '_'.join(list(filter(None, filename.split('_'))))
  return filename

if __name__=='__main__':
  main()



