
from PageRank import PageRank


nodes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
edges = [('A', 'B'),('B', 'D'),('G', 'A'),('A','C'),('E','D'),('F','E'),('F','D')]
pagerank = PageRank(nodes, edges)

for node, rank in pagerank.ranking():
    print str((node,rank))
