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
  # UPDATE TO CONFIG FACETS AFTER DONE TESTING
  facets = ['method']

  # ####################################### #
  #      CONVERT TERMS JSON TO REACT JS     #
  # ####################################### #

  # Iterate over viewer XHTML files, extract name and open FILENAME_pdf_terms_pages.JSON
  for file_name in os.listdir(f'data/xhtml_enriched/'):
    for facet in facets:
      file_name = file_name.strip(".xhmtl")
      booktitle = file_name.split("_")[1]
      json_path = f'data/{database}/{booktitle}/json'

      pdf_terms_pages = json.load(open(f'{json_path}/{facet}_{file_name}_pdf_terms_pages.json'))
      term_highlights = generate_term_highlights(pdf_terms_pages, file_name, facet)
      write_highlights_js(term_highlights, file_name)

# Generate array of terms meta-data like position, comment, content and id
def generate_term_highlights(pdf_terms, file_name, facet):
  highlights = { f'{file_name}.pdf': []}
  number_pages = len(pdf_terms)

  # Get pdf page width/height ratio
  with Image.open(f'{PDFNLT_PATH}/xhtml/images/{file_name}/{file_name}-01.png') as page:
    page_width, page_height = page.size
  
  for i1, page_terms in enumerate(pdf_terms):
    # if i1 > 0: break

    for i2, term in enumerate(page_terms):
      # if i2 > 2: continue

      words_processed = 1
      highlight = { 'content': {'text': term['text']}, 'position': { 'pageNumber': int(term['page_number']) + 1}, 'comment': { 'text': '', 'facet': facet}, 'id': term['id'], 'type': 'automatic' }

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
        highlights[f'{file_name}.pdf'].append(highlight)

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
def write_highlights_js(highlights, file_name):
  file_content = f'// @flow \n\nconst termHighlights = {json.dumps(highlights, indent=2)};\n\nexport default termHighlights;\n'
  file_path = f'/data/highlight/{file_name}-highlights.js'
  os.makedirs(os.path.dirname(ROOTPATH + file_path), exist_ok=True)

  with open(ROOTPATH + file_path, 'w+') as file:
    file.write(file_content)

  len_highlights = len(highlights[f'{file_name}.pdf'])
  
  print(f'Generated {len_highlights} highlights (JS) for {file_name}.pdf: {file_path}')

# Write the array of highlights to json file
def write_highlights_json(highlights, file_name):
  file_content = json.dumps(highlights, indent=2)
  file_path = f'/data/highlight/{file_name}-highlights.json'
  os.makedirs(os.path.dirname(ROOTPATH + file_path), exist_ok=True)

  with open(ROOTPATH + file_path, 'w+') as file:
    file.write(file_content)

  len_highlights = len(highlights[f'{file_name}.pdf'])
  
  print(f'Generated {len_highlights} highlights (JSON) for {file_name}.pdf: {file_path}')

if __name__=='__main__':
  main()

