
from distance import *
from networkx import *
#from pygraphviz import *
#import pylab
import time, os, math
import getopt, sys

def isInt(number):
    try:
        int_number = int(number)
        return True
    except:
        return False

def load_list(filepath):
    f = open(filepath, 'r')
    lines = f.readlines()
    str_list = []
    for l in lines:
        str_list.append(l.strip())
    return str_list

# distance >= ? is considered infinite and is filtered
def filter_infinite(list):
    ret = []
    for i in range(0,len(list)):
        # ? is infinit distance
        if list[i][2] < 0.80:
            ret.append(list[i])
    return ret

# XGraph has edge info
class DistanceGraph:

    # by default use the fastest, google
    # set to 0 for offline analysis, loading graphs from file.
    def __init__(self, distance=None):
        self.__distance = distance
#        self.__graph = XGraph()
        self.__graph = Graph()
        self.__file = 'nothing.graph'
        self.__node_weight = {}
        self.__node_hits = {}
        self.__results_total = None
        self.__base = None
        self.__context = ''
        if distance:
            self.__max_node_weight = math.log(distance.results_total()+2, distance.get_base())
            self.__base = distance.get_base()
            self.__distance.clear_failures()
        
    def set_base(self, base):
        self.__base = base

    def set_results_total(self, total_hits):
        self.__results_total = total_hits
        self.__max_node_weight = math.log(total_hits+2, self.__base)

    def set_context(self, context):
        self.__context = context
        if self.__distance:
            self.__distance.set_context(context)
            self.__max_node_weight = math.log(self.__distance.results_total()+2, self.__distance.get_base())

    def add_node(self, node, node_hits=None):
        self.__graph.add_node(node)
        # + 2, to have a weight of at least 1
        if self.__distance:
            hits = self.__distance.results(node, self.__context)
        else:
            hits = node_hits
        self.__node_weight[node] = math.log(hits, self.__base)
        self.__node_hits[node] = hits
    
    def add_nodes_from(self, node_list):
        for node, freq in node_list:
            self.add_node(node, freq)

    def add_edge(self, edge):
        raise 'Not implemented.'
    
    def add_edges_from(self, edge_list):
        self.__graph.add_edges_from(edge_list)
        self.__edges = self.__graph.edges(data=True)
    
    def update_distances_all(self, communities=False):

        nodes = sorted(self.__graph.nodes())
        for i in range(0,len(nodes)-1):
            node1 = nodes[i]
            pairs = []
            for node2 in nodes[i+1:len(nodes)]:
                pairs.append((node1,node2))
            edges_weights = self.__distance.distances(pairs, self.__context)
#             print 'sleep 10 seconds to bypass proxy'
#             time.sleep(10)    
            for n1,n2 in edges_weights.keys():
                self.__graph.add_edge(n1,n2,edges_weights[(n1,n2)])

        print 'FAILURES: %d' % self.__distance.get_failures()

        self.__nodes = sorted(self.__graph.nodes())
        self.__edges = self.__order_by_weight(self.__graph.edges(data=True))
        
        self.__edges = filter_infinite(self.__edges)
        self.set_fraction_edges(0)
        self.__graph.add_edges_from(self.__edges)

        if communities:
            self.communities()

    def __order_by_weight(self, edges):
        edges_ord = []
        for i in range(0,len(edges)-1):
            for j in range(i+1,len(edges)):
                # compare weight
                if edges[i][2] > edges[j][2]:
                    aux = edges[i]
                    edges[i] = edges[j]
                    edges[j] = aux

        return edges

    def get_graph(self):
        return self.__graph


    # exclude the weaker edges, exclude (1-fraction)
    # 0 =< fraction <= 1
    def set_fraction_edges(self, fraction):
        self.__graph.clear()
        self.__graph.add_nodes_from(self.__nodes)
        cut_point = int(len(self.__edges) * fraction)
        self.__graph.add_edges_from(self.__edges[cut_point:])
        #erase isolated nodes
#         for n in self.__nodes:
#             if len(self.__graph.neighbors(n)) == 0 and len(self.__graph.nodes()) > 1:
#                 self.__graph.delete_node(n)

    def demo_block(self, cut_points, draw_func, draw_name, sleep_time, subdivision):
        segments = len(cut_points) - 1
        for i in cut_points:                
                self.set_fraction_edges(float(i)/subdivision)
                pylab.clf()
                draw_func(self.__graph)
                pylab.savefig("data/%s-%s-%f.ps" % (self.__file, draw_name, float(i)/subdivision))
                time.sleep(sleep_time)


    def demo(self, subdivision=10, segments=9):
        sleep_time = 0.005
        iterations = 1
        self.set_fraction_edges(0.0)
        draw(self.__graph)
        pylab.show()
        cut_points = range(subdivision-segments,subdivision+1)
        for k in range(0,iterations):

            draw_func = draw_circular
            draw_name = 'circular'
            cut_points.reverse()
            self.demo_block(cut_points, draw_func, draw_name, sleep_time, subdivision)
            cut_points.reverse()
            self.demo_block(cut_points, draw_func, draw_name, sleep_time, subdivision)

            draw_func = draw
            draw_name = 'normal'
            cut_points.reverse()
            self.demo_block(cut_points, draw_func, draw_name, sleep_time, subdivision)
            cut_points.reverse()
            self.demo_block(cut_points, draw_func, draw_name, sleep_time, subdivision)

            
    def draw(self):

        pylab.show()

    # run after update_edges
    def save(self, file_path):
        f = open(file_path, 'w')
        # save base
        #f.write('%d\n' % self.__base)
        # save total results
#        f.write('%d\n' % self.__results_total)
#        for n in self.__graph.nodes():
#            f.write('%s\n' % n )
#            f.write('%d\n' % self.__node_hits[n])
#        f.write('----\n')
        for e in self.__edges:
            f.write('%s %s %d\n' %  e )
            #f.write('%s\n' % e[1] )
            #try:
            #    f.write('%f\n' % e[2] )
            #except:
            #    print 'BUG: e[2] = %s' % str(e[2])
            #    f.write('2.00\n')

    def load(self, file_path):
        self.__file = file_path.split('/')[len(file_path.split('/'))-1]
        f = open(file_path, 'r')
        lines = f.readlines()
        f.close()
        self.__graph.clear()
        i = 0
        self.set_base(int(lines[i].strip()))
        i += 1
        self.set_results_total(int(lines[i].strip()))
        i += 1
        while lines[i].strip() != '----':
            n = lines[i].strip()
            i += 1
            hits = int(lines[i].strip())
            i += 1
            self.add_node(n, hits)
        i += 1
        while i < len(lines):
            n1 = lines[i].strip()
            i += 1
            n2 = lines[i].strip()
            i += 1
            dist = float(lines[i])
            i += 1
            if i % 10000 == 0:
                print '%d lines read.' % i            
            self.__graph.add_edge(n1,n2,dist)
            
        #self.__nodes = sorted(self.__graph.nodes())
        self.__nodes = self.__graph.nodes()
        #self.__edges = self.__order_by_weight(self.__graph.edges())
        self.__edges = self.__graph.edges()

        #self.__edges = filter_infinite(self.__edges)
        self.set_fraction_edges(0)
        self.__graph.add_edges_from(self.__edges)

    # update the node/edge weights, without adding new edges.
    def update(self, communities=False):
        self.set_base(self.__distance.get_base())
        self.set_results_total(self.__distance.results_total())
        for n in self.__nodes:
            self.__node_hits[n] = self.__distance.results(n, self.__context)
        pairs = []
        for e in self.__edges:
            pairs.append((e[0], e[1]))
        distances = self.__distance.distances(pairs, self.__context)
        for e, d in distances.iteritems():
            self.__graph.delete_edge(e[0], e[1])
            self.__graph.add_edge(e[0], e[1], d)
        self.__edges = self.__order_by_weight(self.__graph.edges())

        if communities:
            self.communities()

    def save_edges(self, weighted=False):
        nodes = self.__nodes
        edges = self.__edges
        
        outfilename = self.__file + '.edges'
        print 'writing %s' % outfilename
        out = open(outfilename, 'w')

        # map nodes to ints
        map = {}
        for i,node in zip(range(len(nodes)), nodes):
            map[node] = i + 1
            
        for n1,n2,w in edges:
            if not weighted:
                out.write('%d %d\n' % (map[n1], map[n2]))
            else:
                out.write('%d %d %f\n' % (map[n1], map[n2], w))
            
        print 'nodes: %d' % len(nodes)
        print 'edges: %d' % len(edges)
        
        out.close()
            
    def save_dot(self, communities=False, undirected=False):        
        g = AGraph(strict=True,directed = not undirected)        
        g.graph_attr['outputorder']="edgesfirst"
        
        g.add_nodes_from(self.__graph.nodes())

        g.node_attr['style']='filled'
        g.node_attr['shape']='circle'
        g.node_attr['fixedsize']='true'
        g.node_attr['fontcolor']='#aa0000' #'#008800'
        g.node_attr['fontsize']='%f' % (60.0/math.log(len(g.nodes()),2))

#         g.node_attr['fixedsize']='true'

        node_weight = self.__node_weight
#        max_w = self.__max_node_weight
        max_w = max(node_weight.values()) * 2

 	for i in g.nodes():
 	    n=g.get_node(i)
            color = (float(node_weight[i])/(max_w))*16*16
            if color < 0:
                color = 0
            if color > 256:
                color = 256
 	    n.attr['fillcolor']='#ffffff' #"#22bbbb"
            size = float(node_weight[i])/max_w+0.35
            if size < 0.30:
                size = 0.30
    	    n.attr['height']="%f"%(float(size)/math.log(len(g.nodes()),2))
            n.attr['width']="%f"%(float(size)/math.log(len(g.nodes()),2))
            
#    	    n.attr['height']="0.1"
#            n.attr['width']="0.1"

        for e in self.__graph.edges():
            g.add_edge(e[0],e[1])
            e2 = g.get_edge(e[0],e[1])
            width = e[2]*10
            if width < 0:
                width = 0
            if width > 9:
                width = 9
            e2.attr['style'] = "setlinewidth(%f)" % ((10-width)/math.log(len(g.nodes()),2))
            color = e[2]*256
            if color < 0:
                color = 0
            if color > 150:
                color = 150
            e2.attr['color'] = "#22bb%2x" % (color)
            e2.attr['label'] = ""
            e2.attr['arrowsize'] = "0.25"

        if communities:
            self.save2ints()
            self.read_communities()
            for bs in self.__comm_bridges:
                for b in bs:
                    n=g.get_node(b)
                    n.attr['fillcolor']="#cccccc"
                    n.attr['shape']="triangle"                
            for l in self.__comm_leader:
                n=g.get_node(l)
                h = n.attr['height']
                w = n.attr['width']
                n.attr['shape']="box"                
                n.attr['height'] = h
                n.attr['width'] = w

            for comm in self.__comms:
                comm_color = random.randint(0,2**16-1)
                for comm_elem in comm:
                    n=g.get_node(comm_elem)
                    n.attr['fillcolor']="#00%4x" % comm_color
                            
        g.layout() # layout with default (neato)
 	g.write("%s.dot" % self.__file) # write to simple.dot
 	print "Wrote bla.dot"
# 	g.draw('circo.svg',prog="circo") # draw to png using circo
        g.draw('%s.ps' % self.__file,prog="neato") # draw to png using neato
 	print "Wrote %s.dot and %s.ps" % (self.__file, self.__file)

    def communities(self):
        filepath = self.save2ints()
        print 'filepath' + filepath
        os.system('cp %s Tp3Ej1.in' % filepath)
        os.system('./correr')
        os.system('cp comm.out %s.comm' % self.__file)

    def read_communities(self):
        try:
            f = file('%s.comm' % self.__file,'r')
        except:
            self.communities()
            f = file('%s.comm' % self.__file,'r')
        lines = f.readlines()
        line_num = 0
        self.__comms = []
        self.__comm_leader = []
        self.__comm_bridges = []
        line = lines[line_num].strip()
        while not isInt(line.strip()):
            print line.strip()
            if line.split(' ')[0].strip() == 'CantidadDeComunidades:':
                comm_num = int(line.split(' ')[1])
                print 'comm_num: %d' % comm_num
            line_num += 1
            line = lines[line_num].strip()
        while line_num < len(lines):
            line = lines[line_num].strip()
            while not isInt(line.split('\t')[0].strip()):
                line_num += 1
                line = lines[line_num].strip()
            comm_size = int(line.strip())
            print 'comm_size %d' % comm_size
            line_num += 1
            line = lines[line_num].strip()
            comm = []
            for i in range(comm_size):
                comm.append(self.__map[int(line.split('\t')[0])])
                line_num += 1
                line = lines[line_num].strip()
            print 'comm: %s' % str(comm)
            self.__comms.append(comm)
            # read leader
            leader = self.__map[int(line.split(' ')[1])]
            print 'leader: %s' % leader
            line_num += 1
            # read bridges
            line = lines[line_num].strip()
            bridges = map(lambda x: self.__map[x], map(int,line.split(' ')[1:]))
            self.__comm_leader.append(leader)
            print 'bridges: %s' % str(bridges)
            self.__comm_bridges.append(bridges)
            line_num += 2


    def save2ints(self):

        max_int_weight = 10000
        count = 0
        _map = {}
        _imap = {}
        for node in self.__nodes:
            _map[count] = node
            _imap[node] = count
            count += 1
        
        filepath = '../data/%s.ints2' % self.__file
        o = file(filepath, 'w')
        # wieght is float
        for n1,n2,w in self.__edges:
            o.write('%d\t%d\t%f\n' % (_imap[n1],_imap[n2],w))
        o.close()

        filepath = '../data/%s.ints3' % self.__file
        o = file(filepath, 'w')
        # wieght is float
        for n1,n2,w in self.__edges:
            o.write('%d\t%d\t%f\n' % (_imap[n1],_imap[n2],w*100))
        o.close()

        filepath = '../data/%s.ints' % self.__file
        o = file(filepath, 'w')
        # wieght is float
        for n1,n2,w in self.__edges:
            o.write('%d\t%d\t%d\n' % (_imap[n1],_imap[n2],int(max_int_weight*w)))
        o.close()

        self.__map = _map
        self.__imap = _imap
        return filepath
    

    def plot(self):
        pass

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:c:udone", ["help", "input=", "context=", "update", "draw", "communities", "undirected", "save_edges"])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    _input = None
    context = ''
    update = False
    draw = False
    comm = False
    undirected = False
    save_edges = False
    for o, a in opts:
        if o == "-u":
            update = True
        if o == "-d":
            draw = True
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-i", "--input"):
            _input = a
        if o in ("-c", "--context"):
            context = a
        if o in ("-o", "--communities"):
            comm = True
        if o in ("-n", "--undirected"):
            undirected = True
        if o in ("-e", "--save_edges"):
            save_edges = True
    # ...


#    dataset = 'corelabs'
    dataset = _input
    in_file = '../data/%s.nodes' % dataset
    out_file = '../data/%s-%s.graph' % (dataset,context.replace(' ','_'))

    if update: # update existant graph from file
        print 'updating..'
        # compute distances and save
        dg = DistanceGraph(NGD())
        dg.set_context(context)
        out_file = '../data/%s-%s.graph' % (dataset,'')
        dg.load(out_file)
        out_file = '../data/%s-%s.graph' % (dataset,context.replace(' ','_'))
        dg.update(comm)
        dg.save(out_file)


    elif draw: # only plot graph to file
        print 'drawing..'
        dg = DistanceGraph()
        dg.load(out_file)
        dg.save_dot(comm, undirected)

    elif save_edges: # just save graph edges to file
        print 'save edges..'
        dg = DistanceGraph()
        dg.load(out_file)
        dg.save_edges(True)

    elif comm: # only compute communities graph to file
        print 'computing communities..'
        dg = DistanceGraph()
        dg.load(out_file)
        dg.communities()

    else: # compute from node list and save to file
        print 'computing from list..'
        dg = DistanceGraph(NGD())
        dg.set_context(context)
        nodes = load_list(in_file)
        dg.add_nodes_from(nodes)
        dg.update_distances_all(comm)
        dg.save(out_file)


if __name__=='__main__':
    main()


