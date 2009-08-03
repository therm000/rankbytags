


import math, time, os

class RemoveDangling:

     def __snd_fst_cmp(self, A, B):     
         ret = A[1] - B[1]
         if ret < 0:
             return -1
         elif ret > 0:
             return 1
         else:         
             if A[0] > B[0]:
                 return -1
             elif A[0] < B[0]:
                 return 1
             else:
                 return 0

     def __load_tagged_graph(self, dataset):
	self.__dataset = dataset
	lines = open('../data/%s.tagged_graph' % dataset).readlines()
	nodes = set([])
	edges = []
	map_edge_tags = {}
	for line in lines:
		if line.strip() == '':
			continue
		s = line.strip().split('\t\t')	
		nodes.add(s[0])
		nodes.add(s[1])
		edges.append((s[0],s[1]))
		if len(s) > 2:
			map_edge_tags[(s[0],s[1])] = s[2]
	self.__nodes, self.__edges, self.__map_edge_tags = list(nodes), edges, map_edge_tags

    
     def __init__(self, dataset):

	 self.__load_tagged_graph(dataset)
	 nodes, edges = self.__nodes, self.__edges
    
         # code into integers, to avoid use of dictionaries everywhere.
         #print 'mapping nodes to integers'
         map_node_int = {}
         map_int_node = {}     
         for i in range(len(nodes)):	  
             node = nodes[i]	  
             map_node_int[node] = i
             map_int_node[i] = node

         outbound = []
         inbound = []
	 for i in range(len(nodes)):
	         outbound.append([])
	         inbound.append([])
         #print 'extracting output neighbors per node'
         for n1, n2 in edges:
             i_n1 = map_node_int[n1]
             i_n2 = map_node_int[n2]
             inbound[i_n2].append(i_n1)
             outbound[i_n1].append(i_n2)
         self.__inbound = inbound
         self.__outbound = outbound
	 self.__map_node_int = map_node_int

     def __remove_danglings(self):
	dangs = []
	for node in self.__nodes:
		node_int = self.__map_node_int[node]
#		print
#		print node_int
#		print 'inbound %d   outbound %d' % (len(self.__inbound[node_int]),len(self.__outbound[node_int]))
		if len(self.__inbound[node_int]) == 1 and len(self.__outbound[node_int]) == 0:
			dangs.append(node)
#			print 'dangling: %s' % node
	self.__dangs = set(dangs)

     def save_no_danglings(self):
	
	self.__remove_danglings()
	out = open('../data/%s_nd.tagged_graph' % self.__dataset, 'w')
	for (a,b) in self.__edges:
		if not b in self.__dangs and (a,b) in self.__map_edge_tags:	
			out.write('%s\t\t%s\t\t%s\n' % (a,b,self.__map_edge_tags[(a,b)]))
		if b in self.__dangs:		
			print b
	out.close()      


if __name__ == '__main__':
	
	rem = RemoveDangling('youtube')
	rem.save_no_danglings()
