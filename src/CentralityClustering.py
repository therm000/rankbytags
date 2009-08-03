
from networkx import *
from Trie import Trie

from ExtractTags import Tags
from distancegraph import DistanceGraph
from Heap import Heap

import copy, pickle

class Degrees:
    
    def __init__(self, map_node_neigh):
        self.__map = map_node_neigh
        
    def remove_node(self, node):
        if node in self.__map.keys():
            neighs = self.__map[node]
            for neigh in neighs:
                self.__map[neigh].remove(node) 
            


class CentralityClustering:
    
    def __init__(self, nodes=[], edges=[]):
        
        self.__graph = DistanceGraph()
        self.__graph.set_base(2.0)
        self.__graph.add_nodes_from(nodes)
        self.__graph.add_edges_from(edges)
    
    def set_corpus_size(self, size):
        self.__graph.set_results_total(size)
    
    def save(self, filepath):
        self.__graph.save(filepath)
        
    def load(self, tag_graph_path):
        self.__graph.load(tag_graph_path)
        self.__tag_graph_path = tag_graph_path
        
    def build_tag_graph(self, tagged_graph_path, threshold=None):
        
        filename = tagged_graph_path
#    def __init__(self, filename, bound_tag_dist=None, calc_tag_distance=False):
        tags = Tags(filename, threshold, True)
        outfilename = filename + '.tags'
        tags.save_tag_freqs(outfilename)
        
        dist_dict = tags.get_tag_dist()
        tag_freq = tags.get_tag_freq()
        
        print 'tag set with distance: %d' % len(tags.get_tag_set())
        print 'tag edges with distance: %d' % len(dist_dict.keys())    
        
        nodes = []
        for node in tags.get_tag_set():
            nodes.append((node,tag_freq[node]))
            #print str((node,tag_freq[node]))
        
         
        dists = []
        for key, val in dist_dict.iteritems():
            dists.append(val)
        max_dist, min_dist = max(dists), min(dists)
        
        # use opposite distances as weights.        
        edges = []
        for key, val in dist_dict.iteritems():
            edges.append((key[0],key[1],(max_dist-val)/(max_dist-min_dist)))
        
        #edges.sort(thr_fst_cmp, None, True)

        self.__graph.add_nodes_from(nodes)
        self.__graph.add_edges_from(edges)
        
        self.set_corpus_size(tags.get_corpus_size())
        dist_graph_path = filename + '.tags.graph'
        self.save(dist_graph_path)
    
    
    def __strength(self, inverse=False, try_old=False):
        strength = {}
        
        try:            
            if not try_old:
                raise None
            f = open(self.__tag_graph_path+'.strength', 'r')
            lines = f.readlines()
            f.close()
            for line in lines:
                if line.strip() != '':
                    s = line.split(' ')
                    strength[s[0]] = float(s[1])
            print 'strength loaded from file'
        except:               
            edges = self.__graph.get_graph().edges(data=True)
            i = 0
            for a,b,weight in edges:
                if not a in strength.keys():
                    strength[a] = 0.0
                    if len(strength.keys()) % 1000 == 0:
                        print 'nodes added to strength %d of %d' % (len(strength.keys()),len(self.__graph.get_graph().nodes()))
                if not b in strength.keys():
                    strength[b] = 0.0
                strength[a] += weight
                strength[b] += weight
                if i % 10000 == 0:                
                    print 'edges processed to strength %d of %d' % (i,len(self.__graph.get_graph().edges()))
                i += 1
            print 'save strength to file.'
            f = open(self.__tag_graph_path+'.strength', 'w')
            for key,val in strength.iteritems():
                f.write('%s %f\n' % (key,val))
            f.close()
                

        return strength    
    
    def __split_by_float(self, strength_list):
        ret = {}
        ret_list = []
        if len(strength_list) == 0:
            return []
        
        last_node, last_flt = strength_list[0]
        batch = []
        for node, flt in strength_list:
            #print str((node,flt))
            if last_flt != flt:
                ret[last_flt] = batch
                ret_list.append(last_flt)
                last_node, last_flt = node, flt
                batch = [last_node]                
            else:
                batch.append(node)
        ret[last_flt] = batch
        ret_list.append(last_flt)
        return ret_list, ret
        
    def __node_strength(self, graph, node):
        
        edges = graph.edges(node, data=True)
        stren = 0
        for a,b,w in edges:
            stren += w
        return stren 
    
    # from paper Generalized Cores by Vladimir Batajelg and Matjaz Zaversnik
    # p dictionary is typically the degree of a node in a subgraph.
    def p_cores_centrality(self, p=None):
        
#        print 'computing node strength.'
#        strength_list = []         
#        for node, str in self.__strength().iteritems():
#            strength_list.append((node,str))

#        print 'sorting by node strength.'
#        strength_list.sort(snd_fst_cmp)
#        print 'splitting by node strength'
#        strength_list, per_strength = self.__split_by_float(strength_list)
#        
#        if strength_list == []:
#            return []
#        
#        p_cores = {}
#        last_core = []
#        last_strength = per_strength[0][0]
#        while len(per_strength) > 0:
#            node = per_strength[0][1].pop(0)
#            strength = per_strength[0][0]
#            if len(per_strength[0][1]) == 0:
#                per_strength.pop(0)
#            if strength != last_strength:
#                p_cores.append((last_strength, last_core))
#                last_strength = strength
#                last_core = [node]
#            else:
#                pass
 
        C_graph = copy.deepcopy(self.__graph.get_graph())
 
        print 'computing node strength min_queue.'   
        min_queue = Heap(snd_fst_cmp)
        strength = self.__strength()
        for node, stre in strength.iteritems():            
            min_queue.push((node,stre))
            if len(min_queue) % 1000 == 0:
                print 'nodes added to min_queue %d' % len(min_queue)  

            
        if len(min_queue) == 0:
            return []       
 
        print 'computing p-coreness per-se'
        core = {}
        while len(min_queue) > 0:          
            if len(min_queue) % 1000 == 0:
                print 'remaining %d nodes' % len(min_queue)  
            top,stren = min_queue.pop()
            core[top] = stren
            neighs = C_graph.neighbors(top)
            C_graph.delete_node(top)
            del strength[top]
            for v in neighs:
                min_queue.pop_item((v,strength[v]))
                strength[v] = max(stren, self.__node_strength(C_graph, v))
                min_queue.push((v,strength[v]))
        return core

    # remove and returns the first remaining centrality layer.
    # a layer are all the nodes with the same centrality
    # first layer NOT already assigned
    def __first_layer(self, cent_list, assigned=set([]), clust_max_size=50):
        layer = []        
        if len(cent_list) == 0:
            return [], []
        while len(cent_list) > 0 and cent_list[0][0] in assigned:
            cent_list.pop(0)
        if len(cent_list) == 0:
            return [], []
        
        the_val = cent_list[0][1]
        drop = 0
        for node, val in cent_list:
            if the_val == val and not node in assigned and len(layer) < clust_max_size:
                layer.append(node)
            else:
                break
            drop += 1
        cent_list = cent_list[drop:]
        return layer, cent_list

    def __layer_components(self, layer):
        graph = self.__graph.get_graph()
        if len(layer) == 0:
            return []

        comps = []        
        while len(layer) > 0:
            first_comp_node = layer.pop()
            # bfs with intersection
            queue = [first_comp_node]
            comp = []
            while len(queue) > 0:                        
                node = queue.pop(0)
                comp.append(node)            
                neighs = graph.neighbors(node)
                intersec_neighs = list(set(neighs).intersection(set(layer)))
                queue += intersec_neighs
                layer = list(set(layer).difference(set(intersec_neighs)))
            comps.append(comp)            
        return comps

    # types are exists_geq, all_geq, exists_greater, all_greater
    def __comp_dec_boundary(self, comp, centrality, type):
        boundary = self.__graph.get_graph().node_boundary(comp)
        neigh_map = {}
        dec_boundary = set([])
        for boundary_node in boundary:
            comp_nodes = set(comp).intersection(set(self.__graph.get_graph().neighbors(boundary_node)))
            if type=='exists_geq':
                for comp_node in comp_nodes:                
                    if centrality[comp_node] >= centrality[boundary_node]:
                        dec_boundary.add(boundary_node)
                        break
            elif type=='exists_greater':
                for comp_node in comp_nodes:                
                    if centrality[comp_node] > centrality[boundary_node]:
                        dec_boundary.add(boundary_node)
                        break
            elif type=='all_geq':
                all = True
                for comp_node in comp_nodes:                
                    all = all and centrality[comp_node] >= centrality[boundary_node]
                if all:
                    dec_boundary.add(boundary_node)                            
            elif type=='all_greater':
                all = True
                for comp_node in comp_nodes:                
                    all = all and centrality[comp_node] > centrality[boundary_node]
                if all:
                    dec_boundary.add(boundary_node)                            
                    
        return list(dec_boundary)

    # types are exists_geq, all_geq, exists_greater, all_greater
    def __comps_dec_boundary(self, layer_comps, centrality, type):
        comps_neighs = []
        for comp in layer_comps:
            comps_neighs.append(self.__comp_dec_boundary(comp, centrality, type))
        return comps_neighs        

    def __comps_boundary(self, layer_comps):
        comps_neighs = []
        for comp in layer_comps:
            comps_neighs.append(self.__graph.get_graph().node_boundary(comp))
        return comps_neighs        

    def centrality_clustering(self, centrality, clust_size_limit=50, dec_type='all_geq'):
                    
        cent_list = []
        for key, val in centrality.iteritems():
            cent_list.append((key,val))            
        cent_list.sort(snd_fst_cmp)        
        cent_list.reverse()
        
        clusters = []
        assigned = set([])
        old_layers = []
        while len(cent_list) > 0:
            layer, cent_list = self.__first_layer(cent_list, assigned, 1)
            print 'layer extracted size %d' % len(layer)
            print 'nodes remaining: %d' % len(cent_list)
            print '-'*30
            assigned = assigned.union(set(layer))                    
            layer_comps = self.__layer_components(layer)            
            comps_neighs = self.__comps_dec_boundary(layer_comps, centrality, dec_type)
            # while there are non-empty neighbors
            while filter(lambda x:x!=[], comps_neighs) != []:
                i = 0
                for layer_comp, comp_neighs in zip(layer_comps, comps_neighs):
                    if len(comp_neighs) > clust_size_limit:
                        comps_neighs[i] = []
                    elif comp_neighs != []:
                        layer_comps[i] = layer_comp + comp_neighs                        
                        assigned = assigned.union(set(comp_neighs))
                        comps_neighs[i] = self.__comp_dec_boundary(layer_comps[i], centrality, dec_type)
                    i += 1
            for layer_comp in layer_comps:
                print 'cluster added with size %d' % len(layer_comp)
                print layer_comp
                print '-'*70
            print 'nodes remaining %d' % len(cent_list)
            clusters += map(lambda x:set(x),layer_comps)
        return clusters
        


    def centrality_clustering2(self, centrality):
                    
        cent_list = []
        assigned = set([])
        for key, val in centrality.iteritems():
            cent_list.append((key,val))            
        cent_list.sort(snd_fst_cmp)
        cent_list.reverse()
        
        clusters = []
        while len(cent_list) > 0:
            layer = self.__first_layer(cent_list)
            assigned.union(set(layer))                    
            layer_comps = self.__layer_components(layer)
            comps_neighs = self.__comps_neighbors(layer_comps)            
         
            # assigning nodes neighboring the clusters
            assignations = self.__assign_nodes(layer_comps, comps_neighs)
        
        
        
def thr_fst_cmp(A, B):     
     ret = A[2] - B[2]
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

def snd_fst_cmp(A, B):     
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


        
def main():
    
    
    
    # tagged graphs to build tag graph
    #filename = '../data/rpoland--2000.tagged_graph'
    #filename = '../data/rpoland--1000.tagged_graph'
    #filename = '../data/jcl5m--100000.tagged_graph'
    #repetitions_threshold = 10
    #filename = '../data/jcl5m--39370.tagged_graph' 
    #filename = '../data/MIX.tagged_graph'
    
    # DFS
    #filename = '../data/jcl5m--593.tagged_graph'
    # BFS
    #filename = '../data/jcl5m--600.tagged_graph'
    filename = '../data/yt_nd_mini.tagged_graph'
	

    clust = CentralityClustering()
    coincidences_to_link = 2
    clust.build_tag_graph(filename, coincidences_to_link)
    clust.save(filename + '.tag_graph')


    # tag graphs, already built
#    filename += '.tags.graph'
#    clust = CentralityClustering()
#    clust.load(filename)
#    node_core = clust.p_cores_centrality()
#    cluster_size_limit = 5
#    clusters = clust.centrality_clustering(node_core, cluster_size_limit, 'all_greater')
    
#    clusters_filename = filename + ('.%d.clusters' % cluster_size_limit)
#    f = open(clusters_filename, 'w')
#    for cluster in clusters:
#        pickle.dump(cluster,f)
#        f.write('-'*80 + '\n')
#    f.close()
    
    print 'the end.'
    
    
    


if __name__ == "__main__":
    main()


