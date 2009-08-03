
import sys

nodes = set([])
encoding = {}

for line in sys.stdin:
	
	if 'tag pairs appended' in line or 'sorting raw tag' in line or 'tag pairs proccessed' in line or 'corpus.' in line:
		continue


	line_s = line.split()
	src, dst = line_s[0], line_s[1]

	if not src in nodes:
		nodes.add(src)
		src_cod = len(encoding)
		encoding[src] = src_cod
	else:
		src_cod = encoding[src]		
		
	if not dst in nodes:
		nodes.add(dst)
		dst_cod = len(encoding)
		encoding[dst] = dst_cod
	else:
		dst_cod = encoding[dst]		
	
for data, cod in encoding.iteritems():
	sys.stdout.write('%d\t%s\n' %  (cod, data) )
	

