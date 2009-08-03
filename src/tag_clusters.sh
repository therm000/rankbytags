echo "cat $1 | python Coocurrences.py > $1.tag_graph;"
cat $1 | python Coocurrences.py > $1.tag_graph;
echo "echo $1.tag_graph > infile.txt"
echo $1.tag_graph > infile.txt
echo "cat $1.tag_graph | python encode.py > $1.tag_graph.encoded;"
cat $1.tag_graph | python encode.py > $1.tag_graph.encoded;
echo "cat $1.tag_graph | python save_encode.py | sort -n > $1.tag_graph.encode;"
cat $1.tag_graph | python save_encode.py | sort -n > $1.tag_graph.encode;
echo "./comm.sh $1.tag_graph.encoded;"
./comm.sh $1.tag_graph.encoded;
echo "cat $1.tag_graph.encoded.tree | python commlevelall.py"
cat $1.tag_graph.encoded.tree | python commlevelall.py

