# neo4j_internship 


#### preprocess_expdata.py
- pratice dataset is a GTEX RNA-Seq raw read count file (56382 genes x 8555 samples) that is too large for neo4j to handle in one batch. This script partitions the data into 8555 seperate files where each file represents a sample and its corresponding gene and gene counts. 

#### make_exp_filepathways.py 
- python script that creates a csv of the partitioned data file names and pathways that is used to iterate and load data in load_exp_data.cql

#### load_exp_data.cql 
- cypher script to load in partitioned data in batches into a neo4j database 

#### app.py
- flask api application that handles the back end for the database and client communication 

#### how_to_run.txt
- a text file explaining how to run scripts using unix in a VM 

#### DandouchMerai_InternshipReport.pdf
- a report explaining my learning experience as a neo4j intern for the BU Neuromics Lab
