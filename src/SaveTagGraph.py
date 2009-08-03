

from RankByTags import RankerByTags, TagBooleanFormula, TagBooleanConjunction, TagBooleanAtom
from ExtractTags import Tags


def main():

    # create and load
    ranker = RankerByTags()
    #filename = '../data/rpoland--1000.tagged_graph'
    #filename = '../data/rpoland--2000.tagged_graph'
    #filename = '../data/jcl5m--39370.tagged_graph'    
    #filename = '../data/MIX.tagged_graph'
    #filename = '../data/flickr.tagged_graph'
    #filename = '../data/jcl5m-cuantos.tagged_graph'
    #filename = '../data/flickr_med.tagged_graph'
    #filename = '../data/yt.tagged_graph'
    #filename = '../data/fr.tagged_graph'

    #filename = '../data/yt_nd.tagged_graph'
    filename = '../data/fr_nd.tagged_graph'

    top_tags_size = 20

    ranker.load(filename)
    
        # filter by tag boolean formula
    tag_form = TagBooleanFormula()
#    tag_form.run_tests()
#    and1 = TagBooleanConjunction()
#    and1.addAtom(TagBooleanAtom(True,'fun'))
#    tag_form.addTagAnd(and1)
#    and2 = TagBooleanConjunction()
#    and2.addAtom(TagBooleanAtom(True,'fun'))
#    tag_form.addTagAnd(and2)
    print str(tag_form)
    ranker.filter(tag_form)    

           
    # save new subgraph withou tags.
    #outfilename = filename + '-%s.graph' % str(tag_form)
    outfilename = filename
    #ranker.save(outfilename)
    ranker.save_edges(outfilename + '.edges')
    ranker.save_nwb(outfilename + '.nwb')
    
    # now save graphs of top tags
    tags = Tags(filename)
    top_tags = tags.get_top_tags(top_tags_size)
    #top_tags = map(lambda x: x[0], top_tags)
    #top_tags = ['music', 'funny']
    top_tags = ['blue', 'flower']

    for tag in top_tags:

            # filter by tag boolean formula
        tag_form = TagBooleanFormula()
    #    tag_form.run_tests()
        and1 = TagBooleanConjunction()
        and1.addAtom(TagBooleanAtom(True,tag))
        tag_form.addTagAnd(and1)
    #    and2 = TagBooleanConjunction()
    #    and2.addAtom(TagBooleanAtom(True,'fun'))
    #    tag_form.addTagAnd(and2)
        print str(tag_form)
        ranker.filter(tag_form)    
        # save new subgraph withou tags.
        #outfilename = filename + '-%s.graph' % str(tag_form)
        outfilename = filename
        #ranker.save(outfilename)
        ranker.save_edges(outfilename + '.'+ str(tag_form) + '.edges')
        ranker.save_nwb(outfilename + '.' + str(tag_form) + '.nwb')
    

    # now save graphs of top tags by pairs, ANDed.
    tags = Tags(filename)
    top_tags = tags.get_top_tags(top_tags_size)
    #top_tags = map(lambda x: x[0], top_tags)
    #top_tags = ['music', 'funny']
    top_tags = ['blue', 'flower']

    for tag1, i in zip(top_tags,range(len(top_tags))):
        for tag2 in top_tags[i+1:]:

	    # AND
                # filter by tag boolean formula
            tag_form = TagBooleanFormula()
        #    tag_form.run_tests()
            and1 = TagBooleanConjunction()
            and1.addAtom(TagBooleanAtom(True,tag1))
            and1.addAtom(TagBooleanAtom(True,tag2))
            tag_form.addTagAnd(and1)
#            and2 = TagBooleanConjunction()
#            and2.addAtom(TagBooleanAtom(True,tag2))
#            tag_form.addTagAnd(and2)
            print str(tag_form)
            ranker.filter(tag_form)    
            # save new subgraph withou tags.
            #outfilename = filename + '-%s.graph' % str(tag_form)
            outfilename = filename
            #ranker.save(outfilename)
            ranker.save_edges(outfilename + '.'+ str(tag_form) + '.edges')
            ranker.save_nwb(outfilename + '.' + str(tag_form) + '.nwb')
	    ranker.rank(10)
	    ranker.saveRank(outfilename + '.ranks/' + str(tag_form) + '.graph.rank' )
        
	    # OR
                # filter by tag boolean formula
            tag_form = TagBooleanFormula()
        #    tag_form.run_tests()
            and1 = TagBooleanConjunction()
            and1.addAtom(TagBooleanAtom(True,tag1))
	    tag_form.addTagAnd(and1)
            
            and2 = TagBooleanConjunction()
            and2.addAtom(TagBooleanAtom(True,tag2))
	    tag_form.addTagAnd(and2)
            
#	    and1.addAtom(TagBooleanAtom(True,tag2))
#            tag_form.addTagAnd(and1)
#            and2 = TagBooleanConjunction()
#            and2.addAtom(TagBooleanAtom(True,tag2))
#            tag_form.addTagAnd(and2)
            print str(tag_form)
            ranker.filter(tag_form)    
            # save new subgraph withou tags.
            #outfilename = filename + '-%s.graph' % str(tag_form)
            outfilename = filename
            #ranker.save(outfilename)
            ranker.save_edges(outfilename + '.'+ str(tag_form) + '.edges')
            ranker.save_nwb(outfilename + '.' + str(tag_form) + '.nwb')
	    ranker.rank()
	    ranker.saveRank(outfilename + '.ranks/' + str(tag_form) + '.graph.rank' )        
    
    print 'finish.'
    
if __name__ == "__main__":
    main()

