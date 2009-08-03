
import re
from itertools import groupby

path = 'index.hep-th.txt'
f = open(path,'r')
lines = f.readlines()
f.close()

def extract_tags(title):
    #forb_regexs = ['\$[^\n\$]+\$']
    forb_tags = ['the', 'and', 'their', 'at', 'is', 'in', 'of', 'a', 'on', 'for', 'an', 'with']
    title = title.replace('?','').replace('--', ' ').replace(',','')
    tags = title.split(' ')
    tags = map(lambda x: x.lower(), tags)
    tags = filter(lambda x: x not in forb_tags, tags)
    return tags

# make a graph for a list of tags.
filter_tags = ['walls']
filt_f = open('../data/' + path+'-'+'-'.join(filter_tags)+'.graph', 'w')
filt_f.write('2\n')
filt_f.write('0\n')


nodes = []
edges = []

def sublist(list1, list2):
    _subList = True
    for e in list1:
        _subList = _subList and e in list2
        if not _subList:
            return False
    return True

def or_list(list1, list2):
    for e in list1:
        if e in list2:
            return True
    return False

total_tags = []
for line in lines:
#for i in range(100):
#    line = lines[i]
    cols = line.split('::')
    cols = map(lambda x: x.strip(), cols)
    title = cols[1].split(':')[1].strip()
#    print title
    tags = extract_tags(title)
#    print tags
    total_tags += tags
    
    authors = cols[2].split(':')[1].strip()    
    # remove universities between parenthesis
    authors = re.sub('\([^\n\)]+\)', '', authors)
    # correct ill-formed ', and'
    authors = authors.replace(', and', ' and')
    authors = authors.split(',')
    authors = map( lambda x: x.split(' and '), authors)
    aux = []
    for auth in authors:
        aux += auth
    authors = aux
    authors = map( lambda x: x.strip(), authors)
    authors = filter(lambda x: len(x)>0, authors)
#    print authors

    if or_list(filter_tags, tags):
        print title
        print tags
        print authors
        print ''
        for auth in authors:
            nodes.append(auth)
        for i in range(len(authors)):
            for j in range(i+1,len(authors)):
                edges.append((authors[i],authors[j]))
    

freqs = [(k, len(list(g))) for k, g in groupby(sorted(total_tags))]
print str(freqs)
total_tags = list(set(total_tags))
#print total_tags
f = open(path + '.tags', 'w')
for t in total_tags:
    f.write('%s\n' % t)
f.close()
    

nodes = list(set(nodes))
edges = list(set(edges))

for n in nodes:
    filt_f.write('%s\n' % n)
    filt_f.write('1\n')
filt_f.write('----\n')
for n1,n2 in edges:
    filt_f.write('%s\n' % n1)
    filt_f.write('%s\n' % n2)
    filt_f.write('0.5\n')

filt_f.close()




#     9208004 ::Title: The $D\to 2$ Limit of General Relativity ::Authors: R.B. Mann and S.F. Ross
# 9208005 ::Title: Nonlinear Noise in Cosmology ::Authors: Salman Habib and Henry E. Kandrup
# 9208006 ::Title: Stochastic Inflation:The Quantum Phase Space Approach ::Author: Salman Habib
# 9208007 ::Title: There is no $R^3 X S^1$ vacuum gravitational instanton ::Authors: Niall \'O Murchadha and Hugh Shanahan

