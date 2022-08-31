import pandas as pd
from flask import Flask
from flask import render_template
from flask import request
from neo4j.exceptions import ServiceUnavailable
from neo4j import GraphDatabase
import logging 
import csv

with open("cred.txt") as f1:
        data=csv.reader(f1,delimiter=",")
        for row in data:
                id = row[0]
                pwd=row[1]

class Connection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_query(self, command):
        with self.driver.session() as session:
            result = session.write_transaction(self.run_command, command)
        return result

    @staticmethod
    def run_command(tx, command):
        result = tx.run(command)
        try:
            return result.data()
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
            query=command, exception=exception))
            raise
    
    def create_table_query(self, command, tissue_name, gene_sym, read_count):
        with self.driver.session() as session:
            result = session.write_transaction(self.run_table_query, command, tissue_name, gene_sym, read_count)
        return result

    @staticmethod
    def run_table_query(tx, command, tissue_name, gene_sym, read_count):
        result = tx.run(command, tissue_name=tissue_name, gene_sym=gene_sym, value=read_count)
        try:
            return result.data()
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
            query=command, exception=exception))

# flask stuff 
app=Flask(__name__)
@app.route("/")
def index():
    tissue = [""]
    gene =[""]
    query = ("MATCH(s:Sample) "
            "RETURN DISTINCT s.tissue; ")
    connect = Connection("neo4j://localhost:7687", id, pwd)
    results = connect.create_query(query)   
    for record in results:
        for value in record.values():
            tissue.append(value)
    query = ("MATCH(g:Gene) "
            "RETURN DISTINCT g.gene_symbol limit 50; ")
    connect = Connection("neo4j://localhost:7687", id, pwd)
    results = connect.create_query(query)   
    for record in results:
        for value in record.values():
            gene.append(value)
    return render_template("index.html", tissue=tissue, gene=gene)

@app.route("/", methods=["GET", "POST"])
def graph():
    if request.method == "POST":
        if request.form["submit_button"] == "return_result": 
            tissue_val = request.form.get("tissue", None)
            gene_sym = request.form.get("gene", None)
            read_sym = request.form.get("read_count", None)
            read_val = request.form.get("readcount_textbox", '' )
            if tissue_val != None:
                if read_sym == 'NA' or read_val == '' and read_sym == 'NA': 
                    query = (
                        "MATCH (s:Sample { tissue: $tissue_name }) "
                        "MATCH (g:Gene { gene_symbol: $gene_sym }) " 
                        "MATCH (s)-[r:NUM_OF_OVERLAPS]-(g) " 
                        "RETURN s.Name, s.tissue, g.gene, g.gene_symbol, r.read_count; ")
                if read_sym == '>':
                    read_val = int(read_val)
                    query = (
                            "MATCH (s:Sample { tissue: $tissue_name }) "
                            "MATCH (g:Gene { gene_symbol: $gene_sym }) " 
                            "MATCH (s)-[r:NUM_OF_OVERLAPS]-(g) " 
                            "WHERE r.read_count > $value "
                            "RETURN s.Name, s.tissue, g.gene, g.gene_symbol, r.read_count; ")
                if read_sym == '<': 
                    read_val = int(read_val)
                    query = (
                            "MATCH (s:Sample { tissue: $tissue_name }) "
                            "MATCH (g:Gene { gene_symbol: $gene_sym }) " 
                            "MATCH (s)-[r:NUM_OF_OVERLAPS]-(g) " 
                            "WHERE r.read_count < $value "
                            "RETURN s.Name, s.tissue, g.gene, g.gene_symbol, r.read_count; ")
                if read_sym == '<=': 
                    read_val = int(read_val)
                    query = (
                            "MATCH (s:Sample { tissue: $tissue_name }) "
                            "MATCH (g:Gene { gene_symbol: $gene_sym }) "  
                            "MATCH (s)-[r:NUM_OF_OVERLAPS]-(g) " 
                            "WHERE r.read_count <= $value "
                            "RETURN s.Name, s.tissue, g.gene, g.gene_symbol, r.read_count; ")
                if read_sym == '>=': 
                    read_val = int(read_val)
                    query = (
                            "MATCH (s:Sample { tissue: $tissue_name }) "
                            "MATCH (g:Gene { gene_symbol: $gene_sym }) " 
                            "MATCH (s)-[r:NUM_OF_OVERLAPS]-(g) " 
                            "WHERE r.read_count >= $value "
                            "RETURN s.Name, s.tissue, g.gene, g.gene_symbol, r.read_count; ")
                if read_sym == '=':
                    read_val = int(read_val)
                    query = (
                            "MATCH (s:Sample { tissue: $tissue_name }) "
                            "MATCH (g:Gene { gene_symbol: $gene_sym }) " 
                            "MATCH (s)-[r:NUM_OF_OVERLAPS]-(g) " 
                            "WHERE r.read_count = $value "
                            "RETURN s.Name, s.tissue, g.gene, g.gene_symbol, r.read_count; ")
                if read_sym == '!=': 
                    read_val = int(read_val)
                    query = (
                            "MATCH (s:Sample { tissue: $tissue_name }) "
                            "MATCH (g:Gene { gene_symbol: $gene_sym }) " 
                            "MATCH (s)-[r:NUM_OF_OVERLAPS]-(g) " 
                            "WHERE NOT r.read_count = $value "
                            "RETURN s.Name, s.tissue, g.gene, g.gene_symbol, r.read_count; ")
                connect = Connection("neo4j://localhost:7687", id, pwd)
                results = connect.create_table_query(query, tissue_val, gene_sym, read_val)
                df = pd.DataFrame(results)
                return render_template('results.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
            else: 
                error = "Something didn't work!"
                return render_template('index.html',  error=error)