from pagerank import PageRank
from RankByTags import *

from pprint import pprint

def snd_cmp(A,B):
    ret = A[1] - B[1]
    if ret < 0:
        return -1
    elif ret > 0:
        return 1
    else:
        return 0

def not_rank(rank):
    notr = []
    for thing, float_rank in rank:
        notr.append((thing, 1-float_rank))
    notr.reverse()    
    return PageRank.normalize(notr)

def and_rank(r1, r2):
    
    t1s = map(lambda x: x[0], r1)
    t2s = map(lambda x: x[0], r2)
    intersec = set(t1s).intersection(set(t2s))
    map1, map2 = {}, {}
    for t1, fr1 in r1:
        map1[t1] = fr1
    for t2, fr2 in r2:
        map2[t2] = fr2

    newr = []        
    for t in intersec:
        newr.append((t,map1[t]*map2[t]))
        
#    newr = []
#    for t1, fr1 in r1:
#        for t2, fr2 in r2:
#            if t1 == t2:
#                newr.append((t1, fr1 * fr2))

    newr.sort(snd_cmp, None, True)
    #print str(newr)
    return PageRank.normalize(newr)

def and_rank2(r1, r2):
    
    t1s = map(lambda x: x[0], r1)
    t2s = map(lambda x: x[0], r2)
    intersec = set(t1s).intersection(set(t2s))
    map1, map2 = {}, {}
    for t1, fr1 in r1:
        map1[t1] = fr1
    for t2, fr2 in r2:
        map2[t2] = fr2

    newr = []        
    r1_int, r2_int = [], []
    for t in intersec:
        r1_int.append((t,map1[t]))
        r2_int.append((t,map2[t]))

    r1_int = PageRank.normalize(r1_int)
    r2_int = PageRank.normalize(r2_int)

    return and_rank(r1_int, r2_int)


def and_rank3(r1, r2):
    
    t1s = map(lambda x: x[0], r1)
    t2s = map(lambda x: x[0], r2)
    intersec = set(t1s).intersection(set(t2s))
    
    map1, map2 = {}, {}
    for t1, fr1 in r1:
        map1[t1] = fr1
    for t2, fr2 in r2:
        map2[t2] = fr2

    r1_i, r2_i = [], []
    for e in intersec:
        r1_i.append((e,map1[e]))        
        r2_i.append((e,map2[e]))
    r1_i.sort(snd_cmp)
    r2_i.sort(snd_cmp)

    sum_pos_rank = {}
    for e in intersec:
        sum_pos_rank[e] = 0.0
    for (e, pr), pos in zip(r1_i, range(1,len(r1_i)+1)):
        sum_pos_rank[e] += float(pos)
    for (e, pr), pos in zip(r2_i, range(1,len(r2_i)+1)):
        sum_pos_rank[e] += float(pos)

    final = []
    for e, val in sum_pos_rank.iteritems():
        final.append((e,val))
    final.sort(snd_cmp)
    final.reverse()
    return PageRank.normalize(final)

def and_rank4(r1, r2, ranker, tag, winners=None, iterations=100):
    r1 = r1[:winners]
    r2 = r2[:winners]
    t1s = map(lambda x: x[0], r1)
    t2s = map(lambda x: x[0], r2)
    intersec = set(t1s).intersection(set(t2s))
        
    ranker.filter_by_nodes_and_tag(intersec, tag)
    ranker.rank(iterations)
    return ranker.get_rank()

def and_rank6(r1, r2):
    
    t1s = map(lambda x: x[0], r1)
    t2s = map(lambda x: x[0], r2)
    intersec = set(t1s).intersection(set(t2s))
    map1, map2 = {}, {}
    for t1, fr1 in r1:
        map1[t1] = fr1
    for t2, fr2 in r2:
        map2[t2] = fr2

    newr = []        
    for t in intersec:
        newr.append((t,map1[t]*len(t1s)*map2[t]*len(t2s)))
        
#    newr = []
#    for t1, fr1 in r1:
#        for t2, fr2 in r2:
#            if t1 == t2:
#                newr.append((t1, fr1 * fr2))

    newr.sort(snd_cmp, None, True)
    #print str(newr)
    return PageRank.normalize(newr)


def and_rank0_gold1(tags, ranker):    
    # first compute offline rank
    tag_form = TagBooleanFormula()
    and1 = TagBooleanConjunction()
    for tag in tags:        
        and1.addAtom(TagBooleanAtom(True,tag))
    tag_form.addTagAnd(and1)    
    # filter graph by OR of tags    
    ranker.filter(tag_form)

    # first pagerank of union
    ranker.filter(tag_form)    
    if len(ranker.get_nodes()) > 0: 
        ranker.rank(10)           
        offline_rank = ranker.get_rank()
    else:
        offline_rank = []
    return offline_rank

def and_rank5_gold2(tags, ranker):
    # first compute offline rank
    # OR tag formula
    tag_form = TagBooleanFormula()
    for tag in tags:
        and1 = TagBooleanConjunction()
        and1.addAtom(TagBooleanAtom(True,tag))
        tag_form.addTagAnd(and1)    
    # filter graph by OR of tags
    ranker.filter(tag_form)    
    if len(ranker.get_nodes()) > 0: 
        ranker.rank(10)           
        offline_rank = ranker.get_rank()
    else:
        offline_rank = []
    
    # AND tag formula
    and_nodes = set([])
    for tag in set(tags):
        ranker.filter_one_tag(tag)
        if tag == list(set(tags))[0]:
            and_nodes = ranker.get_nodes()
        else:
            and_nodes = and_nodes.intersection(ranker.get_nodes())
        
    # now filter by intersection
    ret = []
    for name, pagerank in offline_rank:
        if name in and_nodes:
            ret.append((name, pagerank))
    return PageRank.normalize(ret)



def or_rank(r1, r2):    
#    ret = not_rank(and_rank(not_rank(r1), not_rank(r2)))
#    ret = ret.sort(snd_cmp, None, True)
#    return ret    

    t1s = map(lambda x: x[0], r1)
    t2s = map(lambda x: x[0], r2)
    
    newr = []
    for t1, fr1 in r1:
        for t2, fr2 in r2:
            if t1 == t2:
                newr.append((t1, fr1 + fr2 - fr1 * fr2))
                
    diff12 = set(t1s).difference(set(t2s))
    diff21 = set(t2s).difference(set(t1s))
    for ent1 in diff12:
        for ent1_aux, float_rank in r1:
            if ent1 == ent1_aux:
                newr.append((ent1, float_rank))
    for ent2 in diff21:
        for ent2_aux, float_rank in r2:
            if ent2 == ent2_aux:
                newr.append((ent2, float_rank))
                    
    newr.sort(snd_cmp, None, True)
    #print str(newr)
    return PageRank.normalize(newr)

# ranks should have the same elements 
def rank_dist_ksim(r1, r2, top=None):
    if not top:
        top = min(len(r1),len(r2))
    if len(r1) < top or len(r2) < top or top==0:
        return 1, -1
    r1 = r1[:top]
    r2 = r2[:top]

    t1s = map(lambda x: x[0], r1)
    t2s = map(lambda x: x[0], r2)
    intersec = set(t1s).intersection(set(t2s))
    t1_diff_t2 = set(t1s).difference(set(t2s))
    t2_diff_t1 = set(t2s).difference(set(t1s))
    
    # build complete lists.
    r1_prima = t1s
    for e2 in t2s:
        if e2 in t2_diff_t1:
            r1_prima.append(e2)
             
    r2_prima = t2s
    for e1 in t1s:
        if e1 in t1_diff_t2:
            r2_prima.append(e1) 
            
     # precompute positions.       
    pos1 = {}
    for i, e in zip(range(len(r1_prima)), r1_prima):
        pos1[e] = i
    pos2 = {}
    for i, e in zip(range(len(r2_prima)), r2_prima):
        pos2[e] = i

    sum = 0
    for i in range(len(r1_prima)):
        a = r1_prima[i]    
        for j in range(i+1,len(r1_prima)):
            b = r1_prima[j]            
            if (pos1[a] - pos1[b] > 0 and pos2[a] - pos2[b] < 0) \
               or (pos1[a] - pos1[b] < 0 and pos2[a] - pos2[b] > 0):
                sum += 1
    return float(sum)*2.0 / (len(r1_prima)*(len(r1_prima)-1)), len(intersec)


# ranks should have the same elements in the top N elements 
def rank_dist_osim(r1, r2, top=None):
    if not top:
        top = min(len(r1),len(r2))
    if len(r1) < top or len(r2) < top or top==0:
        return 1, -1
    r1 = r1[:top]
    r2 = r2[:top]
    t1s = map(lambda x: x[0], r1)
    t2s = map(lambda x: x[0], r2)
    intersec = set(t1s).intersection(set(t2s))
    return 1 - float(len(intersec)) / top, len(intersec) 


if __name__=='__main__':
    
    r1 = [('tito', 0.5), ('bob', 0.2), ('eve', 0.7),]
    r2 = [('tito', 0.2), ('bob', 0.3), ('eve', 0.8),]
    
    print and_rank3(r1, r2)
