import pandas as pd 

file_collection = {}
file = {}
file_df = pd.read_csv('/Users/meraidandouch/Desktop/NeuromicsLab/bb_graph_load/load_exp_data/gene_data/GTEx_Analysis_v6_RNA-seq_RNA-SeQCv1.1.8_gene_reads.csv', skiprows = 2, sep='\t')
samples = file_df.columns.values.tolist()
print(samples)

for i in range(2, len(samples)):
   gene_id = file_df.iloc[:, 0]
   gene_sym = file_df.iloc[:,1]
   counts = file_df.iloc[:,i]
   file = {'gene':gene_id, 'gene_symbol':gene_sym, 'read_count':counts}
   file_collection[samples[i]] = pd.DataFrame(file)

for keys, values in file_collection.items():
    df = file_collection[keys]
    df.to_csv('/Users/meraidandouch/Desktop/NeuromicsLab/bb_graph_load/load_exp_data/data/'+ keys +".csv",  sep=',', index = False, header = True)
    
