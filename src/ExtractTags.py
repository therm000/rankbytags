
from itertools import groupby
from cluster import KMeansClustering
import math
from Trie import Trie

class TagDistance:
  
    basic_tag_similarity = True
  
    def __init__(self, nodes, edges, bound=2):
        self.__nodes = nodes
        self.__edges = edges
        self.__reps_cache = {}
        self.__dist_cache = {}
        self.__map_tag_lines = {}
        
        # the corpus size is the number of tagged videos (or photos or whatever content is tagged)
        self.__corpus_size = len(edges)
        
        dist = {}
        tag_freq = {}
        tag_pair_strs = []
        
        #dist = {}
        pairs = 0
        for n1, n2, str_tags in edges:
            tags = str_tags.split('|')
            tags.sort()
            for i in range(len(tags)):
                # increment per tag freq
                if not tags[i] in tag_freq.keys():
                    tag_freq[tags[i]] =  1
                else:
                    tag_freq[tags[i]] = tag_freq[tags[i]] + 1                                            
                # add tag pair 
                for j in range(i+1, len(tags)):
                    tag_pair = [tags[i], tags[j]]
                    tag_pair = sorted(tag_pair)
                    tag_pair_str = tag_pair[0] + '|' +tag_pair[1]
                    tag_pair_strs.append(tag_pair_str)
                    if pairs % 100000 == 0:
                        print '%d tag pairs appended.' % pairs
                    pairs += 1
                    
        print 'sorting raw tag pairs.'
        tag_pair_strs.sort()
        
        print 'computing NGC from raw tag pairs corpus.'    
        last = ''       
        count = 1
        pairs = 0
        tag_set = set([])
        for tag_pair_str in tag_pair_strs:
            if last == tag_pair_str:
                count += 1
            else:
                if count >= bound:
                    tags = last.split('|')
                    if self.basic_tag_similarity:
                       dist[(tags[0], tags[1])] =  count
                    else:
                       dist[(tags[0], tags[1])] =  self.__NGD(tag_freq[tags[0]], tag_freq[tags[1]], count, self.__corpus_size)
                    tag_set.add(tags[0])
                    tag_set.add(tags[1])                   
                count = 1 
                last = tag_pair_str
            if pairs % 100000 == 0:
                print '%d tag pairs proccessed to compute NGD.' % pairs
            pairs += 1
                     
        if count > bound:
            tags = last.split('|')
            if self.basic_tag_similarity:
               dist[(tags[0], tags[1])] =  count
            else:
               dist[(tags[0], tags[1])] =  self.__NGD(tag_freq[tags[0]], tag_freq[tags[1]], count, self.__corpus_size)

	print dist                   
        self.__dist = dist
        self.__tag_set = tag_set
        self.__tag_freq = tag_freq 
        
    def get_dict(self):
        return self.__dist
    
    def get_tag_set(self):
        return self.__tag_set
    
    def get_tag_freq(self):
        return self.__tag_freq
    
    def get_corpus_size(self):
        return self.__corpus_size
    
    def __NGD(self, x_res, y_res, xy_res, total, base=2):
        
        if x_res==0 and y_res==0:
            return None
        if xy_res==0:
            return 2.00 # infinite
        # use base 2 logs to compute final value
        base = base
        numerator = max( math.log(x_res,base), math.log(y_res,base) ) - math.log(xy_res,base)
        denominator = math.log(total,base) - min( math.log(x_res,base), math.log(y_res,base) )

        ret = numerator / denominator
        return ret
                    
    def reps(self, tag):
        ret = 0
        for n1, n2, str_tag in edges:
            tags = map(int, str_tags.split('|'))
            if tag in tags:
                ret +=1
        return ret

    def reps2(self, tag1, tag2):
        ret = 0
        for n1, n2, str_tag in edges:
            tags = map(int, str_tags.split('|'))
            if tag1 in tags and tag2 in tags:
                ret +=1
        return ret
        
    def distance(self, tag1, tag2):
#        if not (tag1,tag2) in self.__dist.keys():
#            return 9999
#        else:
#            return self.__dist((tag1,tag2))
#        return 0

        if (tag1,tag2) in self.__dist_cache.keys() or (tag2,tag1) in self.__dist_cache.keys():
            return self.__dist_cache[(tag1,tag2)]
        if (tag2,tag1) in self.__dist_cache.keys():
            return self.__dist_cache[(tag2,tag1)]

        self.__base = 2
        self.__total = len(self.__edges)
        if tag1 in self.__reps_cache.keys():
            x_res = self.__reps_cache[tag1]
        else:
            x_res = self.reps(tag1)
            self.__reps_cache[tag1] = x_res
        if tag2 in self.__reps_cache.keys():
            y_res = self.__reps_cache[tag2]
        else:
            y_res = self.reps(tag2)
            self.__reps_cache[tag2] = y_res        
        # x,y results as a set, not concatenation
        xy_res = self.rep2(tag1, tag2)
        
        if x_res==0 and y_res==0:
            return None
        if xy_res==0:
            return 2.00 # infinite
        # use base 2 logs to compute final value
        base = self.__base
        numerator = max( math.log(x_res,base), math.log(y_res,base) ) - math.log(xy_res,base)
        denominator = math.log(self.__total,base) - min( math.log(x_res,base), math.log(y_res,base) )

        ret = numerator / denominator
        self.__dist_cache[(tag1,tag2)] = ret
        return ret


class Tags:

    def __freq_cmp(self,A,B):
        return A[1] - B[1]

    
    def __init__(self, filename, bound_tag_dist=None, calc_tag_distance=False):
        
        self.__map_tag_lines = {}
        
        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
                    
        nodes = set([])
        edges = set([])
        
        total_tags = []
        pairs = 0
        
        for line in lines:
            cols = line.split('\t\t')
            if len(cols) < 3:
                continue
            src = cols[0]
            dst = cols[1]
            cols[2] = cols[2].strip().lower()
            tags = cols[2].split('|')
            total_tags += tags

            if calc_tag_distance:
                pairs += len(tags) * (len(tags)-1) / 2
                nodes.add(src)
                nodes.add(dst)
                edges.add((src,dst, cols[2].strip()))
            
            for tag in tags:
                if not tag in self.__map_tag_lines:
                    self.__map_tag_lines[tag] = []
                self.__map_tag_lines[tag].append(line)

        freqs = [(k, len(list(g))) for k, g in groupby(sorted(total_tags))]
        freqs.sort(self.__freq_cmp)
        freqs.reverse()

        
        if calc_tag_distance:
            # try log bound_tag_dist
            if not bound_tag_dist:
                bound_tag_dist = int(math.log(len(edges))) / 2
                if bound_tag_dist < 2:
                    bound_tag_dist = 2
            print 'bound_tag_dist = %f' % bound_tag_dist
            self.__tagDistance = TagDistance(nodes, edges, bound_tag_dist)
                
            print 'total with reps: %d' % len(total_tags)                    
            print 'total no reps: %d' % len(freqs)
            print 'total raw tag pairs: %d' % pairs

                        
        
        total_tags = list(set(total_tags))
        print 'total number of tags: %d' % len(total_tags)
        
        self.__freqs = freqs
        self.__tags = total_tags        
        self.__nodes = nodes
        self.__edges = edges
        self.__len_edges = len(lines)
      
    def __prefix_dist(self, tag1, tag2):
        ret = 0
        for c1, c2 in zip(tag1, tag2):
            if c1 == c2:
                ret += 1
            else:
                break
        return max(len(tag1),len(tag2)) - ret
      
    def best_tag(self, tag):
        closest_tag, closest_dist = '', len(tag)
        for tag2 in self.__tags:
            tag2_dist = self.__prefix_dist(tag, tag2)
            if tag2_dist < closest_dist:
                closest_tag, closest_dist = tag2, tag2_dist 
        return closest_tag  
      
    def tag_weight(self, tag):
        part = float(len(self.__map_tag_lines[tag])) / self.__len_edges
        return part * math.log(len(self.__tags)) * math.log(len(self.__tags))
        
    def get_lines(self, tag):
        return self.__map_tag_lines[tag]
        
    def get_top_tags(self, many=None):
        if many:
            return self.__freqs[:many]
        else:
            return self.__freqs
        
    def save_tag_freqs(self, outfilename):
        print 'writing %s' % outfilename
        f = open(outfilename, 'w')
        
        for freq in self.__freqs:
	    if freq[0] != '':
	            f.write('%s %d\n' % (freq))
        
        f.close()

    def cluster(self, clusters):
        """
        clusters is the final numbers of clusters
        """
        cl = KMeansClustering(map(lambda x: (x), range(len(self.__tags))), self.__tagDistance)
        self.__clusters = cl.getclusters(clusters)
        return self.__clusters

    def get_tag_dist(self):
        return self.__tagDistance.get_dict()

    def get_tag_set(self):
        return self.__tagDistance.get_tag_set()

    def get_tag_freq(self):
        return self.__tagDistance.get_tag_freq()

    def get_corpus_size(self):
        return self.__tagDistance.get_corpus_size()

def main():
    
    #filename = '../data/ejemplo.tagged_graph'
    #filename = '../data/rpoland--2000.tagged_graph'
    #filename = '../data/jcl5m--100000.tagged_graph'
    #filename = '../data/flickr.tagged_graph'
    filename = '../data/webist.tagged_graph'
    
    cluster = Tags(filename)
    outfilename = filename + '.ranks/all.tags'
    cluster.save_tag_freqs(outfilename)
    
    #clusters = cluster.cluster(2)
    print '-------------------'
    #for c in clusters:
    #    print 'CLUSTER'
    #    print str(c)
        
    #cl = KMeansClustering([(1,1), (2,1), (5,3)])
    #clusters = cl.getclusters(2)
    #print str(clusters)


if __name__ == "__main__":
    main()

