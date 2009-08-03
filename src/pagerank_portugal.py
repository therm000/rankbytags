
from PageRank import PageRank

nodes = ['A', 'B', 'C', 'D', 'E', 'F']
edges = [('A', 'B'),('B', 'C'),('C','D'),('D','C'),('E','D'),('F','E'),('E','F')]
pagerank = PageRank(nodes, edges)

for node, rank in pagerank.ranking():
    print str((node,rank))
