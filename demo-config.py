'''
@author: daniel
'''

## mongoDB
mongoDB_IP = '127.0.0.1'
mongoDB_Port = 27017  # default local port. change this if you use SSH tunneling on your machine (likely 4321 or 27017).
mongoDB_db = 'pub'

## conferences we analysed
booktitles = ['ACL', 'JCDL','SIGIR','ECDL','TPDL','TREC', 'ICWSM', 'ESWC', 'ICSR','WWW', 'ICSE', 'HRI', 'VLDB', 'ICRA', 'ICARCV']
facets = ['dataset', 'method']
use_in_viewer = ['ACL', 'VLDB', 'WWW', 'ICWSM']

min_ne_threshold = 16
nr_top_papers = 6
nr_top_papers_cited = 50

seedsize = 50
iteration = 0

# Root paths
ROOTPATH='<ROOTPATH PROJECT FOLDER>'
PDFNLT_PATH = '<RELATIVE PATH TO PDFNLT FOLDER>'

scholar_query_limit = 65

