#!/usr/bin/env python3
###############################################################################################
# Converts EasyChair "ACM data download" output to ACM Proceedings Enhanced CSV format
# Author: JP Navarro for PEARC'22
# Date: March 2022
#
# EasyChair data details:
#   Menu option "Premium" -> "ACM data download" generates XML
#        convert XML to JSON https://codebeautify.org/xmltojson or similar tool
#   Menu option "Status" -> "Reviewing data in Excel" (top right) includes missing Track details
#
# ACM Proceedings Enhanced CSV format details:
#   https://www.acm.org/publications/gi-proceedings-current
#   https://www.acm.org/binaries/content/assets/publications/taps/papertypes-csvfields.pdf
###############################################################################################

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
        parser.add_argument('-ea', '--easyacm', action='store', required=True, \
                            help='EasyChair ACM data in JSON')
        parser.add_argument('-er', '--easyrev', action='store', required=True, \
                            help='EasyChair Reviews data in CSV')
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
        self.filterTypes = ['Extended Abstract', 'Full Paper']
        self.track_section_map = {
            'Applications - Full Paper':    'Applications and Software - Full Paper',
            'Systems - Full Paper':         'Systems and System Software - Full Paper',
            'Workforce - Full Paper':       'Workforce Development, Training, Diversity, and Education - Full Paper',
            'Applications - Short Paper':   'Applications and Software - Short Paper',
            'Systems - Short Paper':        'Systems and System Software - Short Paper',
            'Workforce - Short Paper':      'Workforce Development, Training, Diversity, and Education - Short Paper'
        }
        self.proceedingID = '12342'
        self.section_sequence = {
            'Workforce Development, Training, Diversity, and Education - Full Paper': '1',
            'Applications and Software - Full Paper': '2',
            'Systems and System Software - Full Paper': '3',
            'Workforce Development, Training, Diversity, and Education - Short Paper': '4',
            'Applications and Software - Short Paper': '5',
            'Systems and System Software - Short Paper': '6'
        }
        self.out_csv = list()
        
    def Load(self):
        # Load EasyChair Reviews Data
        easyrev_path = os.path.abspath(self.args.easyrev)
        self.reviews = {} # Reviews hashed by Title
        try:
            with open(easyrev_path, 'r') as fd:
                dr = csv.DictReader(fd, delimiter=',', quotechar='"')
                for row in dr:
                    self.reviews[row['Title']] = row
        except ValueError as e:
            eprint('ERROR "{}" parsing EasyChair Reviews input={}'.format(e, easyrev_path))
            self.exit(1)

        if self.args.verbose:
            eprint('** EasyChair reviews = {}'.format(len(self.reviews)))
            
        # Load EasyChair ACM Data
        easyacm_path = os.path.abspath(self.args.easyacm)
        try:
            with open(easyacm_path, 'r') as fd:
                self.rawinput = json.load(fd)
        except ValueError as e:
            eprint('ERROR "{}" parsing EasyChair ACM input={}'.format(e, easyacm_path))
            self.exit(1)
       
        if type(self.rawinput['erights_record']['paper']) is not list or \
                len(self.rawinput['erights_record']['paper']) <= 0:
            eprint('ERROR input papers not found')
            self.exit(1)

        self.input_papers = self.rawinput['erights_record']['paper']
        self.papers = []
        self.typeCount = Counter()
        for paper in self.input_papers:
            self.typeCount.update({paper['paper_type']})
            if paper.get('paper_type', '') not in self.filterTypes:
                continue
            if paper.get('paper_title', '') not in self.reviews:
                eprint('WARNING: Ignoring paper with no review or known track: {}'.format(paper.get('paper_title')))
                continue
            # reviews are indexed by paper_title
            review = self.reviews.get(paper.get('paper_title', ''), '')
            track = review.get('Track', '')
            paper['section_title'] = self.track_section_map.get(track) or track
            self.papers.append(paper)

        if self.args.verbose:
            if self.filterTypes:
                eprint('** EasyChair papers included by filter: {}'.format(', '.join((self.filterTypes))))
            eprint('** EasyChair papers by type:')
            for c in self.typeCount:
                if c in self.filterTypes:
                    eprint('   {} = {}'.format(c, self.typeCount[c]))

        self.SORT = {}        # Used for sorting papers within a section
        for p in self.papers:
            SORT_GROUP = p['section_title']
            if SORT_GROUP not in self.SORT:
                self.SORT[SORT_GROUP] = {}
            if type(p['authors']['author']) is list:
                FIRST_AUTHOR = p['authors']['author'][0]
            else:
                FIRST_AUTHOR = p['authors']['author']
            if FIRST_AUTHOR['sequence_no'] != 1:
                eprint('ERROR: First author sequence not 1, unhandled, exiting')
                sys.exit(1)
            # This determines the order, name+paper#
            SORT_KEY = ','.join((FIRST_AUTHOR['last_name'], FIRST_AUTHOR['first_name'], FIRST_AUTHOR['middle_name'])).lower() + ':' + str(p['event_tracking_number'])
            self.SORT[SORT_GROUP][SORT_KEY] = p['event_tracking_number']
        self.PAPER_SEQ = {}
        for g in self.SORT:
            GROUP = self.SORT[g]
            seq = 0
            for p in sorted(GROUP):
                PAPERID = GROUP[p]
                seq += 1
                self.PAPER_SEQ[PAPERID] = seq
        print('foo')
        
    def Add_Author(self, apaper, anauthor):
        out = {}
        out['proceedingID'] = self.proceedingID
        out['event_tracking_number/theirnumber'] = str(apaper.get('event_tracking_number',''))
        out['paper_type'] = apaper.get('paper_type','').lower()
        out['theTitle'] = apaper.get('paper_title','')
        out['prefix'] = anauthor.get('prefix','')
        out['first_name'] = anauthor.get('first_name','')
        out['middle_name'] = anauthor.get('middle_name','')
        out['last_name'] = anauthor.get('last_name','')
        out['suffix'] = anauthor.get('suffix','')
        out['author_sequence_no'] = anauthor.get('sequence_no','0')
        if anauthor.get('contact_author').lower() in ('y', 'yes'):
            out['contact_author'] = 'yes'
        else:
            out['contact_author'] = 'no'
        out['orcid'] = anauthor.get('ORCID','')
        out['email'] = anauthor.get('email_address','')
        out['institution / AFFILIATION'] = anauthor.get('affiliations',{}).get('affiliation','')
        out['country'] = anauthor.get('country','')
        out['start_page'] = '1'
        out['section_title'] = apaper.get('section_title','')
        out['article_seq_no'] = apaper.get('sequence_no') or self.PAPER_SEQ.get(apaper.get('event_tracking_number'))
        out['section_seq_no'] = self.section_sequence.get(apaper.get('section_title',''), '')
        self.out_csv.append(out)

    def Convert(self):
        for paper in self.papers:
            if paper['paper_type'] not in self.filterTypes:
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
