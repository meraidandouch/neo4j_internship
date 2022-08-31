// Delete all relationships
CALL apoc.periodic.iterate(
'MATCH ()-[r]->() RETURN id(r) AS id', 
'MATCH ()-[r]->() WHERE id(r)=id DELETE r', 
{batchSize: 1000});

// Delete all nodes
CALL apoc.periodic.iterate(
'MATCH (n) RETURN id(n) AS id', 
'MATCH (n) WHERE id(n)=id DELETE n', 
{batchSize: 1000});

// Drops any constraints or indexes called in 
CALL apoc.schema.assert({}, {}); 

// indexes are created after loading the data 
CREATE CONSTRAINT sample_id ON (s:Sample) ASSERT (s.Name) IS UNIQUE;
CREATE CONSTRAINT url_id ON (s:Sample) ASSERT (s.URL) IS UNIQUE;
CREATE CONSTRAINT gene_id ON (g:Gene) ASSERT (g.gene) IS UNIQUE; 

CALL db.awaitIndexes()

LOAD CSV WITH HEADERS FROM "file:////Users/<user>/pathway/to/data/pathwayToNodes.csv" AS row
WITH row
CREATE (s:Sample)
SET s += row
RETURN count(s); 

MATCH(s:Sample) 
WITH collect(s.URL)[0] AS fileURLs
UNWIND fileURLs AS fileURL
CALL apoc.periodic.iterate(
'
CALL apoc.load.csv($url,{mapping: {read_count: {type: "float"}},header:true,quoteChar:"\u0000"}) YIELD map AS row
RETURN row
','
CREATE (g:Gene{gene:row.gene, gene_symbol:row.gene_symbol})
',
{batchSize:1000,parallel:true,params:{url:fileURL}}) 
YIELD batches, total
RETURN batches, total;

MATCH(s:Sample) 
WITH collect(s.URL) AS fileURLs
UNWIND fileURLs AS fileURL
CALL apoc.periodic.iterate(
'
CALL apoc.load.csv($url,{mapping: {read_count: {type: "float"}},header:true,quoteChar:"\u0000"}) YIELD map AS row
RETURN row
','
MATCH(s:Sample{URL:$url})
MATCH(g:Gene{gene:row.gene, gene_symbol:row.gene_symbol})
CALL apoc.create.relationship(s, "NUM_OF_OVERLAPS", {read_count:row.read_count}, g)
YIELD rel
return rel
',
{batchSize:1000,parallel:true,params:{url:fileURL}}) 
YIELD batches, total
RETURN batches, total;
