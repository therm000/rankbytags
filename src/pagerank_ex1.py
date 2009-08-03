
from PageRank import PageRank

nodes = ['A', 'B', 'C', 'D']
edges = [('A', 'B'),('B', 'D'),('D', 'C'),('C', 'A')]
pagerank = PageRank(nodes, edges)

for node, rank in pagerank.ranking():
    print str((node,rank))

