

class MergeDataSets:
    
    def __init__(self, tagged_graphs_filename_list, outpath):
        
        self.__paths_list = tagged_graphs_filename_list
        
        lines = []
        for path in self.__paths_list:
            f = open(path, 'r')
            lines += f.readlines()
            f.close
        
        lines = list(set(lines))
        
        f = open(outpath, 'w')
        for line in lines:
            f.write(line)
        f.close()
        

path_list = ['../data/jcl5m--39370.tagged_graph',
        '../data/DarthAbercrombie--50000.tagged_graph',
        '../data/catlovercaro--40000.tagged_graph',
        '../data/liloshortee--30000.tagged_graph'        
        ]
outpath = '../data/MIX.tagged_graph'
merge = MergeDataSets(path_list, outpath)