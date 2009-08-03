
import sys

infile = open('infile.txt').read().strip()

map_inverse = open(infile+'.encode').readlines()
map_inverse = [l.strip().split()[1] for l in map_inverse]

for line in sys.stdin:
	s = line.split()
	src = int(s[0])
	dst = int(s[1].strip())
	sys.stdout.write('%s %s\n' % ( dst, map_inverse[src]))



