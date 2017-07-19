# PubChemID_scraper
Extract PubChem IDs for compounds in a MySQL database from [PubChem](http://pubchem.ncbi.nlm.nih.gov/).

### Arguments
* **db_host (-s)**: Host name or address for your MySQL database. Default='localhost'
* **db_name (-d)**: Database Name
* **db_user (-u)**: Username for database authentication
* **db_pswd (-p)**: Password for database authentication
* **output_file (-o)**: Name/location of output file. Default='compound_ids.csv'
* **verbose (-v)**: Option to output execution details to console
* **query (-q)**: Database query for compound selection. Column order: Compound ID, Common Name, SMILE. Default="SELECT SWID,common_name,smile FROM drc_info"

### Input
Input is a list of tuples resulting from a SELECT query. Each tuple should have the following format:

Private ID|Common Name|SMILE String
---|---|---
Your database-determined ID|The compounds common name|The compound structure as a SMILE string

### Output
Output is a CSV file with the following format:

Private ID|Common Name Private|PubChem ID|Common Name PC|Match Method
---|---|---|---|---
Your database-determined ID|The compounds common name from your database|The PubChem ID|The compound's common name from PubChem|The parameter used to find the PubChem ID (common name, SMILE, or None)

**NOTE:**
* Entries will be matched by common name first, if not found, they will be matched to the closest SMILE.
* If no entry is found, pubchem_id field will be set as *None* and common_name as your locally-defined smile
  * The SMILE allows you to identify the compounds manually


### Requirements
This script requires the following packages:
* mysql.connector
* argparse
* requests
* csv
