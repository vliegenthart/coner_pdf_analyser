# @author Daniel Vliegenthart

import os
import time
import csv
from config import ROOTPATH, PDFNLT_PATH, facets, max_entity_words, tse_ner_conferences, iteration, nr_top_papers_cited, min_doubly_threshold
from shutil import copyfile, rmtree

viewer_papers = ['conf_www_SawantC13', 'conf_vldb_WeberSB98', 'conf_www_TitovM08', 'conf_vldb_BamfordAP99', 'conf_icwsm_KulshresthaZNGG15', 'conf_www_KulkarniAPS15', 'conf_vldb_ChakrabartiRS02', 'conf_icwsm_BeigiTL16', 'conf_sigir_TrevisiolABB15', 'conf_vldb_ShenZHSZ07', 'conf_www_BhaduryCZL16', 'conf_sigir_ZhangWCL10', 'conf_www_ShuaiSYLLYC16', 'conf_vldb_ChakrabartiRS02', 'conf_vldb_ChakrabartiSST00', 'conf_vldb_PapadomanolakisDA07', 'conf_vldb_SubramanianBLLSSTYW07', 'conf_vldb_OzsuVU98', 'conf_vldb_DeRoseSCDR07', 'conf_sigir_ColettoLOP16', 'conf_jcdl_KleinS13', 'conf_jcdl_HolzmannR14', 'conf_jcdl_SandersonS10', 'conf_www_BakshyEB14', 'conf_www_RuanFP13', 'conf_vldb_ShaoGBBCYS07', 'conf_sigir_RoyGCL12', 'conf_vldb_DyresonBJ99', 'conf_www_YuHYVD15', 'conf_www_DemaineHMMRSZ14', 'conf_vldb_AltinelF00']


base_entity_set_path = f'{ROOTPATH}/data/entity_sets'
database = 'tse_ner'

def main():
  # clean_entity_sets()

  find_doubly_entities(iteration)


def find_doubly_entities(iteration):
  filter = 'majority'
  iteration = 0

  for facet in facets:
    facet_result = []

    total_filt_ent = read_entity_list(f'{ROOTPATH}/data/smartpub_files/{facet}_filtered_entities_{filter}_{iteration}.txt')

    for paper in viewer_papers:
      conf = paper.split("_")[1] 
      file_path = f'data/entity_sets/entity_set_{facet}_{conf}__{paper}__{iteration}.txt'
      extract_list = read_entity_list(file_path)
      filter_list = [entity for entity in extract_list if entity in total_filt_ent]
      facet_result += filter_list

      file_path2 = file_path.split("/")[0] + "/entity_sets_majority/" + file_path.split("/")[2]
      write_entity_set_file(file_path2, filter_list)

    facet_result = sorted(list(set(facet_result)))
    file_path3 = f'data/smartpub_files/{facet}_50_filtered_entities_{filter}_ner.txt'
    
    write_entity_set_file(file_path3, facet_result)

    print(facet, len(facet_result))


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



