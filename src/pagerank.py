# PageRank.py, a pure python implementation of PageRank
# using sparse matrices on memory
# based on paper
# http://www.internetmathematics.org/volumes/1/3/Langville.pdf
# http://meyer.math.ncsu.edu/Meyer/PS_Files/DeeperInsidePR.pdf
#Copyright (C) 2008  termo
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math, time, os

class PageRank:

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

    
     def __init__(self, nodes, edges, native=True, damping_factor=0.85):

         self.__nodes = nodes
         self.__edges = edges
         self.__native = True
         self.__damping = damping_factor


         if native:
              print '                         USE NATIVE PAGERANK'
              f = open('../data/__aux__.nodes','w')
              for node in nodes:
                   f.write('%s\n' % node)
              f.close()
              f = open('../data/__aux__.edges','w')
              for edge in edges:
                   f.write('%s %s\n' % edge)
              f.close()
              return
    
         print '                              USE PYTHON PAGERANK'
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
             n1 = map_node_int[n1]
             n2 = map_node_int[n2]
             inbound[n2].append(n1)
             outbound[n1].append(n2)

         # remove components of size two.
#         rem_nodes = []
#         for node in self.__nodes:
#             if outbound[node]

         
         self.__inbound = inbound
         self.__outbound = outbound
        
      
     def __initial(self):
         return [1.0/len(self.__nodes)] * len(self.__nodes)
    
     def __sparse_multiply(self, vector, convergence=0.0001, max_times=50):
#         sinks = set(range(len(vector))).difference(self.__inbound.keys())
	 sinks = []
	 for i in range(len(self.__nodes)):
	 	if self.__outbound[i] == []:
			sinks.append(i)
	 sinks = set(sinks)
         t = 0
         norm2 = 1.0
         while t < max_times and norm2 >= convergence:

#             print 'PageRank iteration #%d' % t
#             print 'norm2: %f stop when less than %f' % (norm2, convergence)
    
             norm2 = 0.0     
             
             # compute stochastic component
             prod_scalar = 0.0
             for k in range(len(vector)):
                 #vector[k] *= self.__damping
                 if k in sinks:
                     prod_scalar += vector[k] * self.__damping
             prod_scalar += 1.0 - self.__damping         
             stoch = [prod_scalar/len(vector)]*len(vector)
             
             # do sparse matrix multip
             new_vector = stoch
             for k in range(len(vector)):  
		 if k%1000 == 0:
                      pass
#		    print 'node %d of %d in iteration matrix mult: %s' % (k, len(vector), str(time.gmtime()))
           
#                 if k in self.__inbound:
                 for in_node in self.__inbound[k]:
                     new_vector[k] += vector[in_node] / len(self.__outbound[in_node]) * self.__damping
    
                 norm2 += (new_vector[k] - vector[k]) * (new_vector[k] - vector[k])             
    
             t += 1
             norm2 = math.sqrt(norm2) / len(self.__nodes)
             vector = new_vector
            
         return vector
    
    
     def __sparse_multiply_hackish(self, vector, convergence=0.0001, max_times=50):
         sinks = len(self.__nodes) - len(self.__outbound.keys())
         t = 0
         norm2 = 1.0
         while t < max_times and norm2 >= convergence:         
             norm2 = 0.0     
             i = 0
             #print 'PageRank iteration #%d' % t
             #print 'norm2: %f stop when less than %f' % (norm2, convergence)
             for node in range(len(self.__nodes)):
		 if node%1000 == 0:
		    print 'node %d of %d in iteration' % (node, len(self.__nodes))
                 new = 0
                 # inbound nodes
                 if node in self.__inbound.keys():
                    for inbound_node in self.__inbound[node]:
                        new += (self.__damping/len(self.__outbound[inbound_node])+(1.0-self.__damping)/len(self.__nodes)) \
                                * vector[inbound_node]                      
                 # sink nodes, for those assume PR is 1.0 (heuristic optimization)
                 new += float(sinks) / len(self.__nodes)
                 # random surfing from nodes that are not sink and are not in inbound , for those assume PR is 1.0 (heuristic optimization)
                 if not node in self.__inbound.keys(): # is source
                     new += ((len(self.__nodes) - sinks) * (1.0 - self.__damping)) / len(self.__nodes)                 
                 else:
                     new += ((len(self.__nodes) - sinks - len(self.__inbound[node])) * (1.0 - self.__damping)) / len(self.__nodes)                                   
                 # save
                 norm2 += (new - vector[i]) * (new - vector[i])
                 vector[i] = new
                 i += 1         
             t += 1
             norm2 = math.sqrt(norm2) / len(self.__nodes)
         return vector

     def normalize(rank):
	 if len(rank) == 0:
		return rank
         sum = 0
         for name, flt in rank:
             sum += flt     
	 if sum == 0.0:
		return rank
         i = 0
         for name, flt in rank:
             rank[i] = (name, flt/sum)         
             i += 1
         return rank
     normalize = staticmethod(normalize)     
      
     def ranking(self, convergence=-1.0, max_iterations=20):

         if self.__native:# C++ version
              os.system('./pagerank __aux__')
              f = open('../data/__aux__.rank')
              lines = f.readlines()
              f.close()
              rank = []
              for line in lines:
                   if line.strip() == '':
                        continue
                   s = line.strip().split(' ')
                   rank.append((s[0],float(s[1])))
              return rank

         # Python version     
         if len(self.__nodes)==0:
             return []
         if convergence == -1.0:
             convergence = 1.0/len(self.__nodes) * 0.01
         pagerank = self.__initial()
         pagerank = self.__sparse_multiply(pagerank, convergence, max_iterations)
         pagerank = zip(self.__nodes,pagerank) 
         pagerank.sort(self.__snd_fst_cmp)
         pagerank = PageRank.normalize(pagerank)
         pagerank.reverse()
         return pagerank
