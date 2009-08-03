
import math

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
    
     def __init__(self, nodes, edges, damping_factor=0.85):
         self.__nodes = nodes
         self.__edges = edges
         self.__damping = damping_factor
    
         # code into integers, to avoid use of dictionaries everywhere.
         map_node_int = {}
         map_int_node = {}     
         for i in range(len(nodes)):
             node = nodes[i]
             map_node_int[node] = i
             map_int_node[i] = node
    
         outbound = {}
         inbound = {}
         for n1, n2 in edges:
             n1 = map_node_int[n1]
             n2 = map_node_int[n2]
             if not n2 in inbound.keys():
                 inbound[n2] = [n1]
             else:
                 inbound[n2].append(n1)
             if not n1 in outbound.keys():
                 outbound[n1] = [n2]
             else:
                 outbound[n1].append(n2)
         self.__inbound = inbound
         self.__outbound = outbound
      
     def __initial(self):
         return [1.0/len(self.__nodes)] * len(self.__nodes)
    
     def __sparse_multiply(self, vector, convergence=0.0001, max_times=50):
         sinks = set(range(len(vector))).difference(self.__inbound.keys())
         t = 0
         norm2 = 1.0
         while t < max_times and norm2 >= convergence:

             norm2 = 0.0     
             
             # compute stochastic component
             prod_scalar = 0.0
             for k in range(len(vector)):
                 if k in sinks:
                     prod_scalar += vector[k] * self.__damping
             prod_scalar += 1.0 - self.__damping         
             stoch = [prod_scalar/len(vector)]*len(vector)
             
             # do sparse matrix multip
             new_vector = stoch
             for k in range(len(vector)):             
                 if k in self.__inbound:
                     for in_node in self.__inbound[k]:
                         new_vector[k] += vector[in_node] * self.__damping
    
                 norm2 += (new_vector[k] - vector[k]) * (new_vector[k] - vector[k])             
    
             t += 1
             norm2 = math.sqrt(norm2) / len(self.__nodes)
             vector = new_vector
            
         return vector

     def normalize(rank):
         sum = 0
         for name, flt in rank:
             sum += flt     
         i = 0
         for name, flt in rank:
             rank[i] = (name, flt/sum)         
             i += 1
         return rank
     normalize = staticmethod(normalize)     
      
     def ranking(self, convergence=-1.0, max_iterations=20):
         if convergence == -1.0:
             convergence = 1.0/len(self.__nodes) * 0.01
         pagerank = self.__initial()
         pagerank = self.__sparse_multiply(pagerank, convergence, max_iterations)
         pagerank = zip(self.__nodes,pagerank) 
         pagerank.sort(self.__snd_fst_cmp)
         pagerank = PageRank.normalize(pagerank)
         pagerank.reverse()
         return pagerank
