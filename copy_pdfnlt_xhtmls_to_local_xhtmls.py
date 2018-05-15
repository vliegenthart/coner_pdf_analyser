# @author Daniel Vliegenthart

# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import re
import statistics
from config import ROOTPATH, PDFNLT_PATH, facets
import os
from shutil import copyfile, rmtree

def main():

  # ################### #
  #      SETUP ARGS     #
  # ################### #

  # TODO:
  # For multi-file input support check PDFNLT main.py

  parser = argparse.ArgumentParser(description='Annotate xhtml file with term set')

  parser.add_argument('database', metavar='Database', type=str,
                     help='database name of data collection')
  
  args = parser.parse_args()
  database = args.database


  # ######################################## #
  #      COPY XHTMLS FROM PDFNLT TO LOCAL    #
  # ######################################## #
      

  xhtml_raw = f'{ROOTPATH}/data/xhtml_raw/'
  xhtml_enriched = f'{ROOTPATH}/data/xhtml_enriched/'

  try:
    rmtree(xhtml_raw)
  except:
    pass

  try:
    rmtree(xhtml_enriched)
  except:
    pass

  os.makedirs(os.path.dirname(xhtml_raw), exist_ok=True)
  os.makedirs(os.path.dirname(xhtml_enriched), exist_ok=True)

  for file_name in os.listdir(f'{ROOTPATH}/data/viewer_pdfs/'):
    if not file_name.endswith(".pdf"): continue

    pdf_name = file_name.strip(".pdf")
    booktitle = file_name.split("_")[1].lower()

    src = f'{PDFNLT_PATH}/xhtml/{pdf_name}.xhtml'
    copyfile(src, f'{xhtml_raw}{pdf_name}.xhtml')
    copyfile(src, f'{xhtml_enriched}{pdf_name}.xhtml')

if __name__=='__main__':

  main()
