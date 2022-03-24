#!/usr/bin/env python3
# Paper example:
{'authors': {'author': {'ACM_client_no': '',
                        'ACM_profile_id': '',
                        'ORCID': '',
                        'affiliations': {'affiliation': 'Lawrence Berkeley '
                                                        'National Laboratory'},
                        'contact_author': 'Y',
                        'country': 'USA',
                        'email_address': 'SHAHZEBSIDDIQUI@LBL.GOV',
                        'first_name': 'Shahzeb',
                        'last_name': 'Siddiqui',
                        'middle_name': '',
                        'prefix': '',
                        'sequence_no': 1,
                        'suffix': ''}},
 'end_page': '',
 'event_tracking_number': 5791630,
 'paper_title': 'Tutorial: Testing your HPC system with buildtest',
 'paper_type': 'Tutorial',
 'published_article_number': '',
 'section_title': '',
 'sequence_no': '',
 'start_page': ''}

import argparse
import csv
from collections import Counter
from datetime import datetime
import json
import os
import sys
import pdb

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class ACM_Convert():
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('file', type=str, nargs='?')
#        parser.add_argument('-c', '--config', action='store', default='./batch_dbload.conf', \
#                            help='Configuration file default=./batch_dbload.conf')
        parser.add_argument('-e', '--easychair', action='store', required=True, \
                            help='EasyChair input data in JSON')
        parser.add_argument('--verbose', action='store_true', \
                            help='Verbose output')
        parser.add_argument('--pdb', action='store_true', \
                            help='Run with Python debugger')
        self.args = parser.parse_args()

        if self.args.pdb:
            pdb.set_trace()

#        config_path = os.path.abspath(self.args.config)
#        try:
#            with open(config_path, 'r') as cf:
#                self.config = json.load(cf)
#        except ValueError as e:
#            eprint('ERROR "{}" parsing config={}'.format(e, config_path))
#            self.exit(1)

    def Setup(self):
        self.out_fields = ['proceedingID','event_tracking_number/theirnumber','paper_type','theTitle','prefix','first_name','middle_name','last_name','suffix','author_sequence_no','contact_author','ACM_profile_id','ACM_client_no','orcid','email','department_school_lab','institution / AFFILIATION','city','state_province','country','secondary_department_school_lab','secondary_institution','secondary_city','secondary_state_province','secondary_country','section_title','section_seq_no','published_article_number','start_page','end_page','article_seq_no']
        self.out_csv = list()
        
    def Load(self):
        input_path = os.path.abspath(self.args.easychair)
        try:
            with open(input_path, 'r') as fd:
                self.rawinput = json.load(fd)
        except ValueError as e:
            eprint('ERROR "{}" parsing input={}'.format(e, input_path))
            self.exit(1)
       
        if type(self.rawinput['erights_record']['paper']) is not list or \
                len(self.rawinput['erights_record']['paper']) <= 0:
            eprint('ERROR input papers not found')
            self.exit(1)
            
        self.papers = self.rawinput['erights_record']['paper']
        self.types = Counter()
        for paper in self.papers:
            self.types.update({paper['paper_type']})
        
    def Add_Author(self, apaper, anauthor):
        out = {}
        out['event_tracking_number/theirnumber'] = str(apaper.get('event_tracking_number',''))
        out['paper_type'] = apaper.get('paper_type','').lower()
        out['theTitle'] = apaper.get('paper_title','')
        out['prefix'] = anauthor.get('prefix','')
        out['first'] = anauthor.get('first_name','')
        out['middle'] = anauthor.get('middle_name','')
        out['last'] = anauthor.get('last_name','')
        out['suffix'] = anauthor.get('suffix','')
        out['author_sequence_no'] = anauthor.get('sequence_no','0')
        if anauthor.get('contact_author').lower in ('y', 'yes'):
            out['contact_author'] = 'yes'
        else:
            out['contact_author'] = 'no'
        out['orcid'] = anauthor.get('ORCID','')
        out['email'] = anauthor.get('email_address','')
        out['institution / AFFILIATION'] = anauthor.get('affiliations',{}).get('affiliation','')
        out['country'] = anauthor.get('country','')
        out['start_page'] = '1'
        out['article_seq_no'] = apaper.get('sequence_no','')
        self.out_csv.append(out)

    def Convert(self):
        for paper in self.papers:
            if paper['paper_type'] not in ('Full Paper', 'Short Paper'):
                continue
            if type(paper['authors']['author']) is dict:
                self.Add_Author(paper, paper['authors']['author'])
            else:
                for author in paper['authors']['author']:
                    self.Add_Author(paper, author)
        
    def Print(self):
        output = csv.writer(sys.stdout, delimiter=',', quotechar='"')
        output.writerow(self.out_fields)
        for row in self.out_csv:
            output.writerow([row.get(f) for f in self.out_fields])
    
    def exit(self, rc = 0):
#        print('ROWS: {}'.format(self.ROWS_AFTER))
#        print('STATUS: {}'.format(rc))
        sys.exit(rc)

if __name__ == '__main__':
    me = ACM_Convert()
    me.Setup()
    me.Load()
    me.Convert()
    me.Print()
    me.exit(0)
