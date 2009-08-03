
from PageRank import PageRank


nodes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
edges = [
	('A','B'),
	('A','C'),
	('B','C'),
	('B',		'D'),
	('C',		'D'),
	('D',		'C'),
	('E',		'D'),
	('F',		'D'),
	('E',		'F'),
	('F',		'E'),
	('G',		'A'),
	('A',		'G'),
	('C',		'G'),
	('B',		'G'),
	]
pagerank = PageRank(nodes, edges)

for node, rank in pagerank.ranking():
    print str((node,rank))
