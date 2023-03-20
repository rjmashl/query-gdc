#!/usr/bin/env python3

# 8/24-8/26/21
import os, sys, csv, re, requests, json


cases_endpt = 'https://api.awg.gdc.cancer.gov/cases/'   # must include trailing slash
files_endpt = 'https://api.awg.gdc.cancer.gov/files/'
TOKEN_FILE_PATH = '/home/rmashl/tokens/mytoken.txt'

#cases_endpt = 'https://api.gdc.cancer.gov/cases/'   # must include trailing slash
#files_endpt = 'https://api.gdc.cancer.gov/files/'


# Pass list of file ids
fileID_list_file = sys.argv[1]
if not os.path.isfile(fileID_list_file):
    print( 'ERROR: file %s not found\n\n' % (fileID_list_file) )
    sys.exit(1)

# Preload metadata
sample2specimen = dict()
with open( 'sample.tsv', 'r' ) as tsvin:
    tsvin = csv.reader(tsvin, delimiter='\t')
    for row in tsvin:
        if re.search('project_id', row[0]):
            continue
        row = [ s.strip() for s in row ]

        sample_id           = row[ 3]
        sample_submitter_id = row[ 4]
        preservation_method = row[25]
        sample_type         = row[26]
        sample2specimen[ sample_id ] = {'preservation_method': preservation_method, 'sample_type': sample_type,
                                        'sample_submitter_id': sample_submitter_id }

alq2sample = dict()
with open( 'aliquot.tsv', 'r' ) as tsvin:
    tsvin = csv.reader(tsvin, delimiter='\t')
    for row in tsvin:
        if re.search('project_id', row[0]):
            continue
        row = [ s.strip() for s in row ]

        project_id          = row[0]
        sample_id           = row[3]
        sample_submitter_id = row[4]
        aliquot_id          = row[9]

        alq2sample[ aliquot_id ] = {
            'project_id':          project_id,
            'sample_id':           sample_id,
            'sample_submitter_id': sample_submitter_id,
            'preservation_method': sample2specimen[ sample_id ]['preservation_method'],
            'sample_type':         sample2specimen[ sample_id ]['sample_type'],
            'sample_submitter_id': sample2specimen[ sample_id ]['sample_submitter_id'],
        }



with open( TOKEN_FILE_PATH, 'r') as token:
    token_string = str(token.read().strip())

# Note: tokens appear required for AWG endpoints but not GDC endpoints. X-Auth-Token needed not to be commented out in testing.
headers = {
    'X-Auth-Token': token_string,
    'Content-Type': 'application/json',
}

fields = [
    'cases.submitter_id',
    'cases.aliquot_ids',
    'cases.analyte_ids',
    'cases.case_id',
    'cases.sample_ids',
    'cases.portion_ids',
    'data_type',
    'file_id',
    'file_size',
    'data_format',
    'cases.samples.portions.analytes.aliquots.aliquot_id',
    'file_name',
    'experimental_strategy',
    'data_category',
    'cases.samples.preservation_method',
    'cases.samples.sample_type',
    'data_format',
    'md5sum',
    'state',
]
fields = ','.join(fields)

params = {
    'fields': fields,
#    'format': 'TSV',  # JSON is default
    'size': '100'
    }


print( '\t'.join( ['project_id', 'file_id', 'file_name', 'submitter_id', 'aliquot_id_list', 'sample_name_list', 'sample_type_list', 'preservation_method_list', 'data_category', 'data_type', 'caller', 'call_format', 'experimental_strategy' ] ))
with open( fileID_list_file ) as f:
    for line in f:
        file_id = line.rstrip()

        # example: raw_simple_somatic.WXS
        #fileID = 'ba34d55f-c1f8-4789-bc1f-d7697bb7f157'
        print( '#file = ' + file_id )

        response = requests.post( files_endpt + file_id , json = params, headers=headers)
        h = json.loads(response.content.decode('utf-8'))

        if 'data' not in h:
            continue

        # print table
        file_name = h['data']['file_name']

        # caller
        caller = 'undefined'
        if re.search( 'arriba', file_name, re.IGNORECASE):
            caller = 'Arriba'
        elif re.search( 'star_fusion', file_name, re.IGNORECASE):
            caller = 'STAR-Fusion'
        elif re.search( 'ASCAT', file_name):
            caller = 'ASCAT'
        elif re.search( 'BRASS', file_name):
            caller = 'BRASS'
        elif re.search( '.SomaticSniper.', file_name, re.IGNORECASE):
            caller = 'SomaticSniper'
        elif re.search( '.MuSE.', file_name, re.IGNORECASE):
            caller = 'MuSE'
        elif re.search( '.MuTect2.', file_name, re.IGNORECASE):
            caller = 'MuTect2'
        elif re.search( '.Pindel.', file_name, re.IGNORECASE):
            caller = 'Pindel'
        elif re.search( '.VarScan2.', file_name, re.IGNORECASE):
            caller = 'VarScan2'
        elif re.search('.gatk4_mutect2.', file_name, re.IGNORECASE):
            caller = 'GATK4_MuTect2'
        elif re.search('star_', file_name, re.IGNORECASE):
            caller = 'STAR'

        call_format = 'undefined'
        if re.search(r'.vcf.gz$', file_name, re.IGNORECASE):
            call_format = 'VCF'
        elif re.search(r'.maf.gz$', file_name, re.IGNORECASE):
            call_format = 'MAF'
        elif re.search(r'.bedpe$', file_name, re.IGNORECASE):
            call_format = 'BEDPE'
        elif re.search(r'.txt$', file_name, re.IGNORECASE):
            call_format = 'TXT'
        elif re.search(r'.bam$', file_name, re.IGNORECASE):
            call_format = 'BAM'
        elif re.search(r'.tsv.gz$', file_name, re.IGNORECASE):
            call_format = 'TXT/TSV'


        data_type             = h['data']['data_type']
        data_category         = h['data']['data_category']
        experimental_strategy = h['data']['experimental_strategy']
        for c  in h['data']['cases']:
            # should only be single case
            if len( h['data']['cases']) > 1:
                print('ERROR: more than one case found')
                sys.exit(1)
            case_id = c['case_id']
            submitter_id = c['submitter_id']

            # get all aliquots of samples
            alq_list = []
            for s in c['samples']:
                for p in s['portions']:
                    for  a in p['analytes']:
                        for alq in a['aliquots']:
                            alq_list.append( alq['aliquot_id'] )
            alq_list_str = ','.join( alq_list )


            sample_type_list  = []   # get sample types
            preservation_list = []   # get preservation methods
            sample_name_list  = []   # get sample submitter names
            project_id_list   = []
            project_id_list_h = dict()
            for al in alq_list:
                sample_type_list.append( alq2sample[al]['sample_type'] )
                preservation_list.append( alq2sample[al]['preservation_method'] )
                sample_name_list.append( alq2sample[al]['sample_submitter_id'] )
                project_id_list_h[ alq2sample[al]['project_id']] = 1

            sample_type_list_str  = ','.join( sample_type_list )
            preservation_list_str = ','.join( preservation_list )
            sample_name_list      = ','.join( sample_name_list )
            project_id_list       = ','.join( project_id_list_h.keys() )

            print( '\t'.join( [ project_id_list, file_id, file_name, submitter_id, alq_list_str, sample_name_list,  sample_type_list_str, preservation_list_str, data_category, data_type, caller, call_format, experimental_strategy ]))
