
from PageRank_publish import PageRank

import time

print time.gmtime()

size = 100000

nodes = []
for i in range(size):
    nodes.append(i)

# a ring    
edges = []
for i in range(size-1):
    edges.append((i,i+1))
edges.append((size-1,0))

pagerank = PageRank(nodes, edges)

ranks = pagerank.ranking()

#for node, rank in ranks:
#    print str((node,rank))

print 'nodes: %d' % len(nodes)
print 'edges: %d' % len(edges)

print time.gmtime()
