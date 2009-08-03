
#from PageRankNumarray import PageRankNumarray
from pagerank import PageRank
from ExtractTags import Tags
from DumpUtils import dump_obj, load_obj

import os, time

class TagBooleanAtom:
    
    def __init__(self, bool, tag):
        self.__bool = bool
        self.__tag = tag
    
    def set(self, bool, tag):
        self.__bool = bool
        self.__tag = tag

    def get(self):
        return self.__bool, self.__tag

    def match(self, tag_list):
        and_p = self.__bool, self.__tag        
        ret = False
        for tag in tag_list:
            if tag == and_p[1]:
                return and_p[0] ^ False
        return and_p[0] ^ True


class TagBooleanConjunction:
    
    def __init__(self):
        self.__atomList = []

    def __str__(self):
        ret = ''
        for i in range(len(self.__atomList)):
            atom = self.__atomList[i]
            a = atom.get()[1]
            if atom.get()[0]:
                ret += a
            else: 
                ret += 'not_' + a
            if i < len(self.__atomList) - 1:
                ret += '_and_'
        return ret
    
    # an atom is  a pair (Boolean, StringTag)
    def addAtom(self, booleanTagAtom):
        self.__atomList.append(booleanTagAtom)

    def match(self, tag_list):
        or_p = self.__atomList
        and_v = True
        for and_p in or_p:
            and_v = and_v and and_p.match(tag_list)
        return and_v
    
    
class TagBooleanFormula:
    
    def __init__(self):
        self.__conjuntionList = []

    def __str__(self):
        ret = ''
        for i in range(len(self.__conjuntionList)):
            conj = self.__conjuntionList[i]
            ret += str(conj)
            if i < len(self.__conjuntionList) - 1:
                ret += '_Or_'
        return ret
    
    # an atom is  a pair (Boolean, StringTag)
    def addTagAnd(self, booleanTagAnd):
        self.__conjuntionList.append(booleanTagAnd)

    def match(self, tag_list):
        tag_prop = self.__conjuntionList
        if len(tag_prop) == 0:
            return True
        or_v = False
        for or_p in tag_prop:
            or_v = or_v or or_p.match(tag_list)
        return or_v

    def run_tests(self):            
        # filter by tag boolean formula
        tag_form = TagBooleanFormula()
        and1 = TagBooleanConjunction()
        and1.addAtom(TagBooleanAtom(True,'music'))
        tag_form.addTagAnd(and1)
        and2 = TagBooleanConjunction()
        and2.addAtom(TagBooleanAtom(False,'rock'))
        tag_form.addTagAnd(and2)
        if not tag_form.match(['bla','music','bli']):
            raise Exception('unit test failed')
        if tag_form.match(['bla','rock','bli']):
            raise Exception('unit test failed')
        if not tag_form.match(['bla']):
            raise Exception('unit test failed')
        if not tag_form.match([]):
            raise Exception('unit test failed')


class RankerByTags:

    # without extension 
    def load(self, filename):        
        f = open(filename, 'r')
        self.__tags = Tags(filename)
        outfilename = filename + '.ranks/all.tags'
        # save new subgraph withou tags.
        try:
            os.mkdir(filename + '.ranks')
            pass
        except:
            pass
        self.__tags.save_tag_freqs(outfilename)            
        self.__lines = f.readlines()
        self.__filename = filename
        f.close()

    def best_tag(self, tag):
        return self.__tags.best_tag(tag)

    def tag_weight(self, tag):
        return self.__tags.tag_weight(tag)

    def __filter_two_sized_comp(self, nodes, edges):
	 return nodes, edges
         # filter nodes and edges for 2-sized components.
         # code into integers, to avoid use of dictionaries everywhere.
         #print 'mapping nodes to integers'

         print 'Before filtering!!!'
	 print 'Nodes: %d' % len(nodes)
	 print 'Edges: %d' % len(edges)

         
         nodes = list(nodes)
         
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

         removable_nodes, removable_edges = [], []
         for n1, n2 in edges:
             n1 = map_node_int[n1]
             n2 = map_node_int[n2]
	     if len(inbound[n1])==0 and len(outbound[n2])==0:
                  removable_nodes.append(map_int_node[n1])
                  removable_nodes.append(map_int_node[n2])
                  removable_edges.append((map_int_node[n1],map_int_node[n2]))
         nodes, edges = set(nodes), set(edges)
         nodes = nodes.difference( set( removable_nodes ) )
         edges = edges.difference( set( removable_edges ) )

	 print 'After filtering!!!'
	 print 'Nodes: %d' % len(nodes)
	 print 'Edges: %d' % len(edges)


         return nodes, list(edges)

    def filter_one_tag(self, tag):
        nodes = set([])
        edges = set([])
        
        tag_lines = self.__tags.get_lines(tag)
        if not tag_lines:
            raise Exception("no tagged graph loaded!")
        
        for line in tag_lines:
            cols = line.split('\t\t')
            if len(cols) < 3:
                continue
            src = cols[0]
            dst = cols[1]
            tags = cols[2].strip().lower().split('|')
            
            if tag in tags:            
                nodes.add(src)
                nodes.add(dst)
                edges.add((src,dst))
                
        nodes,edges = self.__filter_two_sized_comp(nodes, edges)

        self.__nodes = nodes
        self.__edges = edges

    def filter_by_nodes(self, filter_nodes, tags=None):
        nodes = set([])
        edges = set([])
        
        if not self.__lines:
            raise Exception("no tagged graph loaded!")
        
        for line in self.__lines:
            cols = line.split('\t\t')
            if len(cols) < 3:
                continue
            src = cols[0]
            dst = cols[1]
            #tags = cols[2].strip().lower().split('|')
            
            if src in filter_nodes and dst in filter_nodes:
                #nodes.add(src)
                #nodes.add(dst)
                edges.add((src,dst))
                
        nodes = filter_nodes
        nodes,edges = self.__filter_two_sized_comp(nodes, edges)

        self.__nodes = nodes
        self.__edges = edges

    def filter_by_nodes_and_tag(self, filter_nodes, tag=None):
        nodes = set([])
        edges = set([])
        
        if not self.__lines:
            raise Exception("no tagged graph loaded!")
        
        for line in self.__lines:
            cols = line.split('\t\t')
            if len(cols) < 3:
                continue
            src = cols[0]
            dst = cols[1]
            tags = cols[2].strip().lower().split('|')
            
            if src in filter_nodes and dst in filter_nodes and (not tag or tag in tags):
                #nodes.add(src)
                #nodes.add(dst)
                edges.add((src,dst))
                
        nodes = filter_nodes
        nodes,edges = self.__filter_two_sized_comp(nodes, edges)

        self.__nodes = nodes
        self.__edges = edges

    # a tag proposition
    def filter(self, tag_prop):
        nodes = set([])
        edges = set([])
        
        if not self.__lines:
            raise Exception("no tagged graph loaded!")
        
        for line in self.__lines:
            cols = line.split('\t\t')
            if len(cols) < 3:
                continue
            src = cols[0]
            dst = cols[1]
            tags = cols[2].strip().lower().split('|')
            
            if tag_prop.match(tags):
                nodes.add(src)
                nodes.add(dst)
                edges.add((src,dst))
                
        nodes,edges = self.__filter_two_sized_comp(nodes, edges)


        self.__nodes = nodes
        self.__edges = edges
     
    # a tag proposition
    def filter_save(self, tag_prop, save_file):
        nodes = set([])
        edges = set([])
        
        sf = open(save_file, 'w')
        
        if not self.__lines:
            raise Exception("no tagged graph loaded!")
        sa
        for line in self.__lines:
            cols = line.split('\t\t')
            if len(cols) < 3:
                continue
            src = cols[0]
            dst = cols[1]
            #tags = cols[2].strip().lower().split('|')
            
            if tag_prop.match(tags):
                sf.write(line)
                
        self.__nodes = nodes
        self.__edges = edges
     
    def get_nodes(self):
        return self.__nodes
     
    # save graph after filtering
    def save(self, outfilename):
        nodes = self.__nodes
        edges = self.__edges

        print 'writing %s, nodes: %d, edges: %d' % (outfilename, len(nodes), len(edges))
        out = open(outfilename, 'w')
        
        out.write('2\n')
        out.write('0\n')
        for n in nodes:
            out.write('%s\n' % n)
            out.write('2\n')
        out.write('----\n')
        for n1,n2 in edges:
            out.write('%s\n' % n1)
            out.write('%s\n' % n2)
            out.write('2\n')
        
        out.close()
           

    # save graph after filtering
    def save_edges(self, outfilename):
        nodes = self.__nodes
        edges = self.__edges

	print 'Before saving method save_edges!!!'
	print 'Nodes: %d' % len(nodes)
	print 'Edges: %d' % len(edges)

        
        print 'writing %s' % outfilename
        out = open(outfilename, 'w')

        # map nodes to ints
        map = {}
        for i,node in zip(range(len(nodes)), nodes):
            # begin counting in 1
            map[node] = i + 1
            
        for n1,n2 in edges:
	    try:
	            out.write('%d %d\n' % (map[n1], map[n2]))
            except:
		    pass
        out.close()
            
        print 'nodes: %d' % len(nodes)
        print 'edges: %d' % len(edges)

    # save graph after filtering
    def save_nwb(self, outfilename):
        nodes = self.__nodes
        edges = self.__edges
        
        print 'writing %s' % outfilename
        out = open(outfilename, 'w')

        # map nodes to ints
        map = {}
        for i,node in zip(range(len(nodes)), nodes):
            # begin counting in 1
            map[node] = i + 1

        out.write('*Nodes        %d\n' % len(nodes))
        out.write('id*int      label*string\n')
        for node, int_val in map.iteritems():
            out.write(' %d "%d"                      \n' % (int_val, int_val))
        out.write('*DirectedEdges\n')
        out.write('source*int      target*int\n')           

        for n1,n2 in edges:
	    try:
                out.write(' %d %d\n' % (map[n1], map[n2]))
            except:
                pass
        
        out.close()
            
        print 'nodes: %d' % len(nodes)
        print 'edges: %d' % len(edges)

    def __snd_cmp(self,A,B):
        ret = A[1] - B[1]
        if ret < 0:
            return -1
        elif ret > 0:
            return 1
        else:
            return 0

    def rank(self, iterations=50, damping_factor=0.85, accurate=False):
#        pagerank = PageRankNumarray(list(self.__nodes), self.__edges)
#        self.__pagerank = pagerank.rank()
        use_native = len(self.__edges) > 0
        pagerank = PageRank(list(self.__nodes), self.__edges, use_native, damping_factor)
        self.__pagerank = pagerank.ranking(-1, iterations)      


    def get_rank(self, many=None):
        if many:
            return self.__pagerank[:many]
        else:
            return self.__pagerank
        

    def saveRank(self, outfilenamerank):
        pagerank = self.__pagerank
        print 'writing %s' % outfilenamerank
        f = open(outfilenamerank, 'w')

        for t in pagerank:
            f.write( '%s %.24f\n' % t )

        f.close()
        
    def all_ranks(self, filename, compute_ranks, compute_mono_rank, top_tags=None):
        #self.load(filename)               
        tag_freqs = self.__tags.get_top_tags(top_tags)

        # save new subgraph withou tags.
        try:
            os.mkdir(filename + '.ranks')
            pass
        except:
            pass

        if compute_ranks:	
            try:
                os.mkdir(filename + '.ranks')
            except:
                pass
            i = 0
            secs = time.time()            	       
            for tag, tag_freq in tag_freqs:
                print '%d tags of %d' % (i,len(tag_freqs))
                i += 1 	
                if len(tag) > 0:
    
                    #print tag
                    self.filter_one_tag(tag)    
                    
                    # save new subgraph withou tags.

                    outfilename = filename + '.ranks/%s.graph' % tag
                    #self.save(outfilename)        
                    #   	     self.save_edges(outfilename + '.edges')
                
                    # compute rank
                    print 'compute rank: %s' % tag
                    max_iters = 10
                    self.rank(10)
            
                    # save rank
                    outfilenamerank = outfilename + '.rank'
                    if len(tag) < 64:
                        self.saveRank(outfilenamerank)
            secs = time.time() - secs
            open('log.txt','aw').write('faceted singleton ranks, %f seconds, dataset %s\n' % (secs, filename))

            
    
        if compute_mono_rank:
        
            
        
            # compute monolitic rank of the graph
            print 'computing monolitic rank'
            # filter by tag boolean formula
            tag_form = TagBooleanFormula()
            self.filter(tag_form)    
       
            outfilename = filename + '.ranks/.graph' + '.rank'        
            #outfilename = filename + '-.graph.rank'
            # compute rank
            print 'compute rank: complete graph'
            max_iters = 10
            
            secs = time.time()                      
            self.rank(10)
            secs = time.time() - secs
            open('log.txt','aw').write('single rank, %f seconds, dataset %s\n' % (secs, filename))
            
            
            # save rank
            print 'saving monolitic rank'
            self.saveRank(outfilename)
            
        
        print 'finish.'
    


def main():

    # create and load
    ranker = RankerByTags()
    #filename = '../data/ejemplo.tagged_graph'
    #filename = '../data/rpoland--1000.tagged_graph'
    filename = '../data/rpoland--2000.tagged_graph'
    #filename = '../data/jcl5m--39370.tagged_graph'    
    #filename = '../data/MIX.tagged_graph'
    #filename = '../data/jcl5m-cuantos.tagged_graph'
    #filename = '../data/flickr_med.tagged_graph'

    ranker.all_ranks(filename)


    #ranker.all_ranks(filename)

    
if __name__ == "__main__":
    main()

