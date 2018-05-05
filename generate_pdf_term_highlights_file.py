# @author Daniel Vliegenthart
# Generate pdf term highlights JS file for papers

import argparse
import operator
import csv
import re
import urllib3
from operator import itemgetter
import os
from config import booktitles, ROOTPATH, PDFNLT_PATH, facets
import unidecode
import json
import pprint
from PIL import Image
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# TODO
# - Automatically copy generated highlights files to react app

file_names = []
file_names_title = []

def main():

  # ################### #
  #      SETUP ARGS     #
  # ################### #

  parser = argparse.ArgumentParser(description='Fetch all information for papers')
  parser.add_argument('database', metavar='Database', type=str,
                     help='database name of data collection')

  args = parser.parse_args()
  database = args.database
  
  term_highlights = []

  # ####################################### #
  #      CONVERT TERMS JSON TO REACT JS     #
  # ####################################### #

  for file_name in os.listdir(f'{ROOTPATH}/data/xhtml_enriched/'):
    if not file_name.endswith(".xhtml"): continue
    file_name = file_name.strip(".xhtml")

    file_names.append(file_name)

  papers_overview = read_overview_csv()
  papers_overview = [paper for paper in papers_overview if paper[0] in file_names]

  # Iterate over viewer XHTML files, extract name and open FILENAME_pdf_terms_pages.JSON
  for paper in papers_overview:

    file_name = paper[0]
    paper_title = paper[7].strip('\'')

    file_names_title.append({"pid": file_name, "title": paper_title})

    for facet in facets:
      booktitle = file_name.split("_")[1]
      json_path = f'{ROOTPATH}/data/{database}/{booktitle}/json'

      pdf_terms_pages = json.load(open(f'{json_path}/{facet}_{file_name}_pdf_terms_pages.json'))
      term_highlights += generate_term_highlights(pdf_terms_pages, paper, facet)
    
  write_highlights_js(term_highlights)
  write_papers_js(file_names_title)

# Generate array of terms meta-data like position, comment, content and id
def generate_term_highlights(pdf_terms, paper, facet):
  file_name = paper[0]
  paper_title = paper[7].strip('\'')

  highlights = []
  number_pages = len(pdf_terms)

  # Get pdf page width/height ratio
  with Image.open(f'{PDFNLT_PATH}/xhtml/images/{file_name}/{file_name}-01.png') as page:
    page_width, page_height = page.size
  
  for i1, page_terms in enumerate(pdf_terms):
    # if i1 > 0: break

    for i2, term in enumerate(page_terms):
      # if i2 > 2: continue

      words_processed = 1
      highlight = { 'content': {'text': term['text']}, 'position': { 'pageNumber': int(term['page_number']) + 1}, 'metadata': { 'text': '', 'facet': facet, 'type': 'generated', 'timestamp': int(time.time()) }, 'id': str(term['id']), 'pid': f'{file_name}', 'title': paper_title }

      # Calculate position boundingRect and word rects
      bdr = bdr_to_coord(term['pdf_words'][0]['bdr'].split(','), page_width, page_height)
      if not len(bdr) == 4: continue 

      rects = [{ 'x1': bdr[0], 'x2': bdr[2], 'y1': bdr[1], 'y2': bdr[3], 'width': page_width, 'height': page_height }]
      bounding_rect = rects[0].copy()

      if len(term['pdf_words']) > 1:
        for i3, word in enumerate(term['pdf_words']):
          if i3 is 0: continue

          bdr = bdr_to_coord(word['bdr'].split(','), page_width, page_height)

          if not len(bdr) == 4: continue 
          words_processed += 1;

          word_rect = { 'x1': bdr[0], 'x2': bdr[2], 'y1': bdr[1], 'y2': bdr[3], 'width': page_width, 'height': page_height }

          # Update bounding_rect
          if float(word_rect['x1']) < float(bounding_rect['x1']): bounding_rect['x1'] = word_rect['x1']
          if float(word_rect['x2']) > float(bounding_rect['x2']): bounding_rect['x2'] = word_rect['x2']
          if float(word_rect['y1']) < float(bounding_rect['y1']): bounding_rect['y1'] = word_rect['y1']
          if float(word_rect['y2']) > float(bounding_rect['y2']): bounding_rect['y2'] = word_rect['y2']

          # Update rects array (if y1 and y2 same value -> update rect x2, because adding word, if different -> add new rect for new line)
          prev_rect = rects[-1]
          word_rect2 = word_rect.copy()

          if float(prev_rect['y1']) == float(word_rect2['y1']) and float(prev_rect['y2']) == float(word_rect2['y2']):
            prev_rect['x2'] = word_rect2['x2']
          else:
            rects.append(word_rect2)

      highlight['position']['boundingRect'] = bounding_rect.copy()
      highlight['position']['rects'] = rects.copy()

      if len(term['pdf_words']) == words_processed:
        highlights.append(highlight)

  return highlights

# Convert bdr percentage to page coordinates
def bdr_to_coord(bdr, page_width, page_height):
  temp = bdr[:]
  if not len(temp) == 4: return temp

  temp[0] = float(temp[0]) * page_width
  temp[2] = float(temp[2]) * page_width
  temp[1] = float(temp[1]) * page_height
  temp[3] = float(temp[3]) * page_height
  return temp

# Write the array of highlights to ES6 JS file
def write_highlights_js(highlights):
  json_content = json.dumps(highlights, indent=2)
  file_content = f'// @flow \n\nconst termHighlights = {json_content};\n\nexport default termHighlights;\n'
  file_path = f'/data/highlight/term-highlights.js'
  os.makedirs(os.path.dirname(ROOTPATH + file_path), exist_ok=True)

  with open(ROOTPATH + file_path, 'w+') as file:
    file.write(file_content)

  len_highlights = len(highlights)
  
  print(f'Generated, concatenated and wrote {len_highlights} highlights (JS) to data/highlights/term-highlights.js for papers in data/xhtml_enriched/')

# Write the array of highlights to ES6 JS file
def write_papers_js(file_names):
  json_content = json.dumps(file_names, indent=2)
  file_content = f'// @flow \n\nconst papersList = {json_content};\n\nexport default papersList;\n'
  file_path = f'/data/highlight/papers-list.js'
  os.makedirs(os.path.dirname(ROOTPATH + file_path), exist_ok=True)

  with open(ROOTPATH + file_path, 'w+') as file:
    file.write(file_content)

  len_papers = len(file_names)
  
  print(f'Wrote list of papers of length {len_papers} to data/highlights/papers-list.js')

# Write the array of highlights to json file
def write_highlights_json(highlights, file_name):
  file_content = json.dumps(highlights, indent=2)
  file_path = f'/data/highlight/{file_name}-highlights.json'
  os.makedirs(os.path.dirname(ROOTPATH + file_path), exist_ok=True)

  with open(ROOTPATH + file_path, 'w+') as file:
    file.write(file_content)

  len_highlights = len(highlights)
  
  print(f'Generated {len_highlights} highlights (JSON) for {file_name}.pdf: {file_path}')

# Read papers and number entities overview file
def read_overview_csv():
  file_path = f'{ROOTPATH}/data/total/total/total_papers_has_pdf_v1.csv'
  csv_raw = open(file_path, 'r').readlines()
  csv_raw = [line.rstrip('\n').split(',') for line in csv_raw]
  csv_raw.pop(0) # Remove header column
  
  return csv_raw

if __name__=='__main__':
  main()

