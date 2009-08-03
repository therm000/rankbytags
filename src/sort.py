import networkx as nx

import sys, os

#col = int(open('sort_col.txt').read().strip())
col = -1

def sort_func(x,y):
	if float(x[col]) < float(y[col]):
		return -1
	elif float(x[col]) > float(y[col]):
		return 1
	else:
	     return 0


algorithms = [line.strip() for line in open('algorithms.txt').readlines()]

names = {}
for i in range(len(algorithms)):
	names[i] = algorithms[i]

col = 0
for alg in algorithms:
   for col2 in range(len(algorithms)):
	alg2 = names[col2]

	if col == col2 or alg=='nodes' or alg2=='nodes':
		continue
	infile = open('infile.txt').read().strip()

	rows = open('%s.all_merge'%(infile)).readlines()
	rows = [[y.strip() for y in x.split('\t')] for x in rows]
	rows.sort(sort_func)

	pinfile = '%s.all_merge.%s'%(infile,alg)
	ofile = open(pinfile, 'w')
	for row in rows:
		outrow = ''
		for j in range(len(row)):
			outrow += row[j] + '\t'	
		ofile.write(outrow[:-1] + '\n')
	ofile.close()

	pfilen = '%s.all_merge.%s-%s.plot'%(infile,alg,alg2)
	pfile = open(pfilen, 'w')
	if 'cores' in alg or 'nodes'in alg or 'clust' in alg or 'knn' in alg or 'degree' in alg:
		pfile.write('set log x\n')
	if 'cores' in alg2 or 'nodes'in alg2 or 'clust' in alg2 or 'knn' in alg2 or 'degree' in alg2:
		pfile.write('set log y\n')
	pfile.write('set xlabel "%s"\n' % names[col])
	pfile.write('set ylabel "%s"\n' % names[col2])
	pfile.write('plot "%s" using %d:%d \n' % (pinfile,col+1,col2+1))
	pfile.write('set terminal postscript color dashed enhanced "Times-Roman" 20\n')
	pfile.write('set output "%s.ps"\n' % pfilen)
	pfile.write('replot\n')
	pfile.write('set terminal x11\n') 	
	pfile.close()

	os.system('gnuplot %s' % pfilen)

   col += 1

