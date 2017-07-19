import mysql.connector
import argparse
import requests
import csv

# Define command line arguments
ap = argparse.ArgumentParser()
ap.add_argument('-s','--db_host',default='localhost',help='Host name or address for your mysql database (server)')
ap.add_argument('-d','--db_name',help='Database Name', required=True)
ap.add_argument('-u','--db_user',default=None,help='Username for database authentication')
ap.add_argument('-p','--db_pswd',default=None,help='Password for database authentication')
ap.add_argument('-o','--output_file',default='compound_ids.csv',help='Name/location of output file')
ap.add_argument('-v','--verbose',action='store_true',help='Output execution details to console')
ap.add_argument('-q','--query',default="SELECT SWID,common_name,smile FROM drc_info",help='Database query for compound selection. Column order: Compound ID, Common Name, SMILE')
args = vars(ap.parse_args())

# Connect to MySQL database
# conn = mysql.connector.connect(host='localhost',database='murics',user='root',password='/7HW_98$-d6p/')
conn = mysql.connector.connect(host=args['db_host'],database=args['db_name'],user=args['db_user'],password=args['db_pswd'])
if not conn.is_connected():
    if args['verbose']:
        print ('not connected')
    quit()

# Execute Query
cursor = conn.cursor()
cursor.execute(args['query'])
row = cursor.fetchone()
if args['verbose']:
    print('Query Executed')

# Iterate and save results
output = []
while row is not None:
    if args['verbose']:
        print('Looping: %s' % row[0])
    outputRow = []
    if row[1] is not None:
        req = requests.get("https://pubchem.ncbi.nlm.nih.gov/ngram?q=[display(cmpdname,cid,mw,mf,cmpdiupacname)].from(pccompound_main).usingschema(/schema/pccompound_main).matching(text==%%22%s%%22).start(0).limit(1)" % row[1])
        if 200 == req.status_code:
            resp = req.json()
            if 'ngout' in resp:
                data = resp['ngout']['data']
                if data['totalCount'] > 0:
                    data = data['content'][0]
                    outputRow = [data['cid'],data['cmpdname'],'Compound Name']
    if len(outputRow)==0 and row[2] is not None:
        req = requests.get("https://pubchem.ncbi.nlm.nih.gov/ngram?q=[display(cmpdname,cid,mw,mf,cmpdiupacname)].from(pccompound_main).usingschema(/schema/pccompound_main).matching(/fn/similarity({%%22type%%22:%%22similarity%%22,%%22parameter%%22:[{%%22name%%22:%%22SMILES%%22,%%22string%%22:%%22%s%%22}]})).start(0).limit(1)" % row[2])
        if 200 == req.status_code:
            resp = req.json()
            if 'ngout' in resp:
                data = resp['ngout']['data']
                if data['totalCount'] > 0:
                    data = data['content'][0]
                    cmpdname = data['cmpdname'] if 'cmpdname' in data else data['cmpdiupacname']
                    outputRow = [data['cid'],cmpdname,'SMILE']
    if len(outputRow)==0 :
        outputRow = [None,row[2],'None']

    output.append( [row[0],row[1]]+ outputRow )
    row = cursor.fetchone()

conn.close()

if args['verbose']:
    print('Loop Ended')

# Export output
with open(args['output_file'],'w',newline='') as csvfile:
    # fwriter = csv.writer(csvfile,delimiter=',',quotechar="'", quoting=csv.QUOTE_MINIMAL)
    fwriter = csv.writer(csvfile,dialect='excel')
    fwriter.writerow(['SWID','common_name_SW','pubchem_id','common_name_PC','match_method'])
    fwriter.writerows(output)

if args['verbose']:
    print('File Exported: %s' % args['output_file'])
