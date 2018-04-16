# @author Daniel Vliegenthart

# Enable imports from modules in parent directory
import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import re
from class_definitions import Entity, PDFTerm, PDFWord
from lib.sliding_window import sliding_window
import statistics

# all occurences of 1 entity in 1 documents are pdfterms under that entity: entity.pdf_terms
# Each term consists of it's subwords in the document
# Wrote description of classes, sent_list etc

# TODO
# - Set max_number_words dynamically depending in term set max terms words occurance?

max_entity_words = 4
tag_attrs = { 'class': '', 'id': '', 'data-bdr': '', 'data-ftype': '', 'data-space': ''}
word_split_pattern = r'([` \t\=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?])'
error_sents = []
number_entities_rejected = 0

def read_entity_set(file_path):
  global number_entities_rejected
  entity_set_text = list(set(open(file_path, 'r').readlines()))
  entity_set = []

  for entity in entity_set_text:
    entity_temp = entity.rstrip('\n')
    if len(entity_temp.split(' ')) <= max_entity_words:
      entity_set.append(Entity(entity_temp.lower()))
    else:
      number_entities_rejected+=1

  return entity_set

# Process and create list of sentences with meta-data
def process_sentences(file_path, pdf_name):
  sent_list_raw = open(file_path, 'r').readlines()
  sent_list_raw = [sent.rstrip('\n') for sent in sent_list_raw]
  sent_list_raw.pop(0) # Remove header column
  sent_list = []
  sent_obj = {}

  for sent in sent_list_raw:
    sent_split = sent.lower().split("\t")
    if len(sent_split) < 4:
      error_sents.append(sent_split)
      continue

    sent_id = sent_split.pop(0)
    sect_name = sent_split.pop(0)
    box_name = sent_split.pop(0)
    word_ids = sent_split.pop().split(",")
    word_array_spaces = re.split(word_split_pattern, " ".join(sent_split))
    word_array = [x for x in word_array_spaces if x not in [" ", "\t", ""]]
    sent_obj_obj = { 'sent_id': sent_id, 'sect_name': sect_name, 'box_name': box_name, 'text': " ".join(sent_split), 'word_array': word_array, 'word_ids': word_ids }

    # Filter out & ignore incorrectly split sentences by PDFNLT (incorrect word displayed in XHTML)
    if len(word_array) != len(word_ids):
      error_sents.append(sent_obj_obj)

    # Add extra metadata to word-array adn add sentence to list and object
    else:
      word_array_info = []
      # word_set = []
      for i, word in enumerate(word_array):
        temp_word = { 'text': word, 'word_id': word_ids[i] }
        word_array_info.append(temp_word)
        # word_set.append(word)

      sent_obj_obj['word_array_info'] = word_array_info
      # print(sent_obj_obj['word_array_info'])

      sent_list.append(sent_obj_obj)
      sent_obj[sent_id] = sent_obj_obj

  # Add some sentence split processing stats
  statistics.init()
  statistics.log_stat(f'{pdf_name.lower()}: # sentences incorrectly split by PDFNLT: {len(error_sents)}/{len(sent_list)}')
  statistics.log_stat(f'{pdf_name.lower()}: # entities rejected because entity.number_words > max_entity_words ({max_entity_words}): {number_entities_rejected}')

  # print(sent_obj['s-3-1-0-2']['word_array_info'])
  return sent_list, sent_obj, error_sents

# Create the set of PDFTerms occurances in PDf from Entity set
def create_terms_info(entity_set, sent_list, sent_obj):

  # Entity to sentence match possible cases:
  # - 1 word entity
  # - multi-word entity
  # - partly match, but not entity
  # - muliple occurance of entity

  for entity in entity_set:
    for sent in sent_list:
      if entity.text in sent['text']:
        
        # Check for each term words length
        for word_length in range(max_entity_words):
          # Sliding array length cannot be larger than sentence number of words
          if len(sent['word_array_info']) > word_length:
            # Sliding window over array of sentence text
            chunks = sliding_window(sent['word_array_info'],word_length+1)
            
            # Match sliding window chunk with entity
            for chunk in chunks:
              chunk_words = ' '.join(word_info['text'] for word_info in chunk)
              if entity.text == chunk_words:

                pdf_term = PDFTerm(sent['sent_id'], entity.id)
                for word in chunk:
                  pdf_term.pdf_words.append(PDFWord(word['text'], word['word_id'], pdf_term.id))

                entity.pdf_terms.append(pdf_term)

  return entity_set


# Find Entities with associated pdf_terms and pdf_words in the {pdf_name}.sent.tsv file
def find_pdf_terms_in_sent_tsv(database, facet, pdf_name, booktitle):

  # ############################ #
  #      FIND TERMS FOR XHTML    #
  # ############################ #

  # print("Analysing & processing sentences...")

  entity_set = read_entity_set(f'data/{database}/{booktitle.lower()}/entity_set/{facet}_{pdf_name}_entity_set_0.txt')

  sent_list, sent_obj, error_sents = process_sentences(f'../PDFNLT/pdfanalyzer/text/{pdf_name}.sent.tsv', pdf_name)

  pdf_term_info_list = create_terms_info(entity_set, sent_list, sent_obj)

  return pdf_term_info_list

