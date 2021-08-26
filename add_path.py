#!/usr/bin/env python3

# reformat query -- replace file & filename with path and remove
import os, sys, csv, re

# Change parent path as needed
PREFIX='/path/to/parent/dir'

ipf = sys.argv[1]
if not os.path.isfile( ipf ):
    print( 'ERROR: file %s not found\n\n' % (ipf) )
    sys.exit(1)

with open( ipf, 'r' ) as tsvin:
    tsvin = csv.reader(tsvin, delimiter='\t')
    for row in tsvin:
        s = '\t'.join([ str(row[i]) for i  in range(len(row)) if i != 1 and i !=2 and i != 4 ])
        if re.search('project_id', row[0]):
            s = '\t'.join([ s, 'path'])
        else:
            fullpath = '/'.join([ PREFIX, row[1], row[2]])
            s = '\t'.join([ s, fullpath ])

        print(s)
