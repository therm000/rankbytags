
from ExtractTags import Tags
from RankByTags import *
import copy
from PageRank import PageRank
from Utils import *


class TagRankExperiment:
    
    __monolitic_rank = None

    __exp_OR = False
    __exp_AND = True
    
    __exp_OSim = True
    __exp_KSim = True
    
    __offline_type = 'gold1' # or 'gold2'
    __exps_list = []

    def set_offline_type(self, type='gold1'):
        self.__offline_type = type

    def set_exps_list(self, list):
        self.__exps_list = list

    def set_and_exp(self, bool):
        self.__exp_AND = bool

    def set_or_exp(self, bool):
        self.__exp_OR = bool

    def set_osim(self, bool):
        self.__exp_OSim = bool

    def set_ksim(self, bool):
        self.__exp_KSim = bool

    def exp_comp_rank_or(self, ranker, tag1, tag2, bool1, bool2, rank1, rank2):
        # first compute offline rank
        tag_form = TagBooleanFormula()
        
        and1 = TagBooleanConjunction()
        and1.addAtom(TagBooleanAtom(bool1,tag1))
        tag_form.addTagAnd(and1)
        and2 = TagBooleanConjunction()
        and2.addAtom(TagBooleanAtom(bool2,tag2))
        tag_form.addTagAnd(and2)
    
        print str(tag_form)
        ranker.filter(tag_form)
        print 'NODES after filter with tags %s OR %s:  %d' % (tag1, tag2, len(ranker.get_nodes())) 
        ranker.rank(10)
        
        offline_rank = ranker.get_rank()
    
        online_rank = or_rank(rank1, rank2)
        
        return offline_rank, online_rank
    
    def and_rank0_gold1(self, tag1, tag2, ranker, bool1=True, bool2=True):
        return and_rank0_gold1([tag1, tag2], ranker)
        
#        # first compute offline rank
#        tag_form = TagBooleanFormula()
#        
#        and1 = TagBooleanConjunction()
#        and1.addAtom(TagBooleanAtom(bool1,tag1))
#        and1.addAtom(TagBooleanAtom(bool2,tag2))
#        tag_form.addTagAnd(and1)
#    
#        print str(tag_form)
#        ranker.filter(tag_form)
#        print 'NODES after filter with tags %s AND %s:  %d' % (tag1, tag2, len(ranker.get_nodes()))
#        if len(ranker.get_nodes()) > 0: 
#            ranker.rank(10)           
#            offline_rank = ranker.get_rank()
#        else:
#            offline_rank = []
#        return offline_rank

    def gold_standart2(self, bool1, bool2, tag1, tag2, ranker):
        
        return and_rank5_gold2([tag1, tag2], ranker)
        
#        # first compute offline rank
#        tag_form = TagBooleanFormula()
#        
#        and1 = TagBooleanConjunction()
#        and1.addAtom(TagBooleanAtom(bool1,tag1))
#        tag_form.addTagAnd(and1)
#        and1 = TagBooleanConjunction()        
#        and1.addAtom(TagBooleanAtom(bool2,tag2))
#        tag_form.addTagAnd(and1)
#        # filter graph by OR of tags
#        print str(tag_form)
#        ranker.filter(tag_form)
#        print 'NODES after filter with tags %s OR %s:  %d' % (tag1, tag2, len(ranker.get_nodes()))
#        if len(ranker.get_nodes()) > 0: 
#            ranker.rank(10)           
#            offline_rank = ranker.get_rank()
#            # now filter rank by intersection of tags            
#            tag_form = TagBooleanFormula()            
#            and1 = TagBooleanConjunction()
#            and1.addAtom(TagBooleanAtom(bool1,tag1))
#            and1.addAtom(TagBooleanAtom(bool2,tag2))
#            tag_form.addTagAnd(and1)
#            ranker.filter(tag_form)
#            intersec_nodes = ranker.get_nodes()
#            final_offline_rank = []
#            for name, pagerank in offline_rank:
#                if name in intersec_nodes:
#                    final_offline_rank.append((name, pagerank))
#            final_offline_rank = PageRank.normalize(final_offline_rank)
#        else:
#            final_offline_rank = []
#        return final_offline_rank
    
    def exp_comp_rank_and(self, ranker, tag1, tag2, bool1, bool2, rank1, rank2, online_type='1'):
        
        if self.__offline_type == 'gold1':
            offline_rank = self.gold_standart1(tag1, tag2, ranker, bool1, bool2)
        elif self.__offline_type == 'gold2':
            offline_rank = self.gold_standart2(bool1, bool2, tag1, tag2, ranker)
    
        if online_type == '1':
            online_rank = and_rank(rank1, rank2)
        elif online_type == '2':
            online_rank = and_rank2(rank1, rank2)
        elif online_type == '3':
            online_rank = and_rank3(rank1, rank2)
        elif online_type == '4':
            online_rank = and_rank4(rank1, rank2, ranker)
        elif online_type == 'mono':
            online_rank = and_rank_mono(tag1, tag2, ranker)
        else:
            raise Exception('Unknown online_type: %s' % str(online_type))
        
        return offline_rank, online_rank
    
    
    def get_tag_ranks(self, ranker, top_tags):
        
        ranks, monolitic_ranks = {}, {}
        for tag in top_tags:
            
            tag_form = TagBooleanFormula()
            
            and1 = TagBooleanConjunction()
            and1.addAtom(TagBooleanAtom(True,tag))
            tag_form.addTagAnd(and1)
        
            print str(tag_form)
            ranker.filter(tag_form)
            print 'NODES after filter with tag %s:  %d' % (tag,len(ranker.get_nodes())) 
            ranker.rank(10) 
            
            ranks[(True,tag)] = ranker.get_rank()
            tag_nodes = set(map(lambda (x,y): x, ranks[(True,tag)]))
    
     
            if not self.__monolitic_rank and 'mono' in self.__exps_list:
                tag_form = TagBooleanFormula()
                
        #        and1 = TagBooleanConjunction()
        #        and1.addAtom(TagBooleanAtom(True,tag))
        #        tag_form.addTagAnd(and1)
            
                print str(tag_form)
                ranker.filter(tag_form)
                print 'NODES after filter with no tags: %d' % len(ranker.get_nodes())
                ranker.rank(10) 
    
                self.__monolitic_rank = ranker.get_rank()
                ranker.saveRank(self.__filename + '-.graph.rank')
            else:
                self.__monolitic_rank = []
            
            mono_tag_rank = []
            for name, pagerank in self.__monolitic_rank:
                if name in tag_nodes:
                    mono_tag_rank.append((name, pagerank))
            monolitic_ranks[(True,tag)] = mono_tag_rank 
    
    
    
    #        tag_form = TagBooleanFormula()
    #        
    #        and1 = TagBooleanConjunction()
    #        and1.addAtom(TagBooleanAtom(False,tag))
    #        tag_form.addTagAnd(and1)
    #    
    #        print str(tag_form)
    #        ranker.filter(tag_form)
    #        ranker.rank(10) 
    #        
    #        ranks[(False,tag)] = ranker.get_rank()
            
        return monolitic_ranks, ranks
    
    
    def experiment_details(self, top_tags, tag_ranks, ranker, bool_pairs, exp_or_filename, exp_and_filename, begin_top_many_users, end_top_many_users, step_top_many_users, online_type='1'):
        
        if self.__exp_OR:
            if self.__exp_OSim:
                exp_or_osim = open(exp_or_filename + '.osim', 'w')
            if self.__exp_KSim:
                exp_or_ksim = open(exp_or_filename + '.ksim', 'w')
        if self.__exp_AND:
            if self.__exp_OSim:
                exp_and_osim = open(exp_and_filename + '.osim', 'w')
            if self.__exp_KSim:
                exp_and_ksim = open(exp_and_filename + '.ksim', 'w')            
        
        rank_comps_or = []
        rank_lens_or = []
        rank_comps_and = []
        rank_lens_and = []
        or_empties = 0
        and_empties = 0
        for tag1 in top_tags:
             for tag2 in top_tags:
                 if tag1 < tag2:
                     
                    for bool1, bool2 in bool_pairs: 

                        if self.__exp_OR:
                           offline_rank, online_rank = self.exp_comp_rank_or(ranker, tag1, tag2, bool1, bool2, tag_ranks[(bool1,tag1)], tag_ranks[(bool2,tag2)])
                           print 'OR len offline_rank: %d   len online_rank: %d' % (len(offline_rank),len(online_rank))
                       
                           for top_many_users in [step_top_many_users**i for i in range(begin_top_many_users,end_top_many_users)]:
                           
                               if self.__exp_OSim:
                                   rank_comp, intersec_len = rank_dist_osim(offline_rank, online_rank, top_many_users)
                                   if intersec_len >= 0:
                                       rank_comps_or.append(rank_comp)
                                       rank_lens_or.append(intersec_len)
                                       if top_many_users <= len(offline_rank):
                                           exp_or_osim.write('%d %d %f \n' % (top_many_users, len(offline_rank), rank_comp))
                                   if intersec_len == -1:
                                       or_empties += 1
                               if self.__exp_KSim:
                                   rank_comp, intersec_len = rank_dist_ksim(offline_rank, online_rank, top_many_users)
                                   if intersec_len >= 0:
                                       rank_comps_or.append(rank_comp)
                                       rank_lens_or.append(intersec_len)
                                       if top_many_users <= len(offline_rank):
                                           exp_or_ksim.write('%d %d %f \n' % (top_many_users, len(offline_rank), rank_comp))
                                   if intersec_len == -1:
                                       or_empties += 1
            
                        if self.__exp_AND:   
                                 offline_rank, online_rank = self.exp_comp_rank_and(ranker, tag1, tag2, bool1, bool2, tag_ranks[(bool1,tag1)], tag_ranks[(bool2,tag2)], online_type)
                                 print 'AND len offline_rank: %d   len online_rank: %d' % (len(offline_rank),len(online_rank))
                                
                                 for top_many_users in [step_top_many_users**i for i in range(begin_top_many_users,end_top_many_users)]:

                                     if self.__exp_OSim:                                   
                                         rank_comp, intersec_len = rank_dist_osim(offline_rank, online_rank, top_many_users)
                                         if intersec_len >= 0:
                                             rank_comps_and.append(rank_comp)
                                             rank_lens_and.append(intersec_len)
                                             if top_many_users <= len(offline_rank):
                                                 exp_and_osim.write('%d %d %f \n' % (top_many_users, len(offline_rank), rank_comp))
                                         if intersec_len == -1:
                                             and_empties += 1
                                     if self.__exp_KSim:                                   
                                         rank_comp, intersec_len = rank_dist_ksim(offline_rank, online_rank, top_many_users)
                                         if intersec_len >= 0:
                                             rank_comps_and.append(rank_comp)
                                             rank_lens_and.append(intersec_len)
                                             if top_many_users <= len(offline_rank):
                                                 exp_and_ksim.write('%d %d %f \n' % (top_many_users, len(offline_rank), rank_comp))
                                         if intersec_len == -1:
                                             and_empties += 1
                                             
        if self.__exp_OR:
            print '--------RANKINGS ERRORS OFFLINE vs ONLINE(OR)------------'
            for pair in zip(rank_comps_or, rank_lens_or):
                print str(pair)
            print '--------AVERAGE RANKING ERRORS OFFLINE vs ONLINE(OR)--------------------'
            if len(rank_comps_or) == 0:
                print 'no rankings with intersec > 0'
            else:
                print 'the average ranking error is %f' % (sum(rank_comps_or) / len(rank_comps_or)) 
                #print 'and the average ranking len is %f' % (sum(rank_lens_or) / len(rank_lens_or)) 
                #print 'quotient %f' % ((sum(rank_comps_or) / len(rank_comps_or))/(sum(rank_lens_or) / len(rank_lens_or))) 
            print 'or bad ranks --> %d  versus not (or) bad ranks --> %d' % (or_empties,len(rank_lens_or))
            print 'bad fraction/quotient is %f' % (float(or_empties)/(len(rank_lens_or)+or_empties))
            if self.__exp_OSim:
                exp_or_osim.close()
            if self.__exp_KSim:
                exp_or_ksim.close()
        
        print
        if self.__exp_AND:
            print '--------RANKINGS ERRORS OFFLINE vs ONLINE(AND)------------'
            for pair in zip(rank_comps_and, rank_lens_and):
                print str(pair)
            print '--------AVERAGE RANKING ERRORS OFFLINE vs ONLINE(AND)--------------------'
            if len(rank_comps_or) == 0:
                print 'no rankings with intersec > 0'
            else:
                print 'the average ranking error is %f' % (sum(rank_comps_and) / len(rank_comps_and)) 
                #print 'and the average ranking len is %f' % (sum(rank_lens_and) / len(rank_lens_and)) 
                #print 'quotient %f' % ((sum(rank_comps_and) / len(rank_comps_and))/(sum(rank_lens_and) / len(rank_lens_and))) 
            print 'and bad ranks --> %d  versus not (and) bad ranks --> %d' % (and_empties,len(rank_lens_and))
            print 'bad fraction/quotient is %f' % (float(and_empties)/(len(rank_lens_and)+and_empties))
            if self.__exp_OSim:
                exp_and_osim.close()
            if self.__exp_KSim:
                exp_and_ksim.close()
    
    
    def run(self, filename, top_many_tags=20):
        tags = Tags(filename)
        top_tags = tags.get_top_tags(top_many_tags)
        
        ranker = RankerByTags()
        ranker.load(filename)
        self.__filename = filename
        
        # add goldstarndart to filename
        filename += '.' + self.__offline_type
        
        top_tags = map(lambda x: x[0], top_tags)
        monolitic_tag_ranks, online_tag_ranks = self.get_tag_ranks(ranker, top_tags)
        
        bool_pairs = [(True,True)] #,(False,True),(True,False),(False,False)]
        #bool_pairs = [(True,True)]
        
        begin_top_many_users = 1
        end_top_many_users = 10
        # exponential step 2, 4 ,8 16
        step_top_many_users = 2

        if 'online1' in self.__exps_list:
            print
            print '-------------------------------------------------------------------------'
            print ' OFFLINE VERSUS ONLINE (EXPERIMENT)'
            or_filename = filename + '.tags-%d.online_vs_offline_or.txt' % top_many_tags
            and_filename = filename + '.tags-%d.online_vs_offline_and.txt' % top_many_tags
            tag_ranks = online_tag_ranks
            self.experiment_details(top_tags, tag_ranks, ranker, bool_pairs, or_filename, and_filename, begin_top_many_users, end_top_many_users, step_top_many_users)

        if 'online2' in self.__exps_list:        
            print
            print '-------------------------------------------------------------------------'
            print ' OFFLINE VERSUS ONLINE2 (EXPERIMENT)'
            or_filename = filename + '.tags-%d.online2_vs_offline_or.txt' % top_many_tags
            and_filename = filename + '.tags-%d.online2_vs_offline_and.txt' % top_many_tags
            tag_ranks = online_tag_ranks
            self.experiment_details(top_tags, tag_ranks, ranker, bool_pairs, or_filename, and_filename, begin_top_many_users, end_top_many_users, step_top_many_users, '2')

        if 'online3' in self.__exps_list:
            print
            print '-------------------------------------------------------------------------'
            print ' OFFLINE VERSUS ONLINE3 (EXPERIMENT)'
            or_filename = filename + '.tags-%d.online2_vs_offline_or.txt' % top_many_tags
            and_filename = filename + '.tags-%d.online3_vs_offline_and.txt' % top_many_tags
            tag_ranks = online_tag_ranks
            self.experiment_details(top_tags, tag_ranks, ranker, bool_pairs, or_filename, and_filename, begin_top_many_users, end_top_many_users, step_top_many_users, '3')
        
        if 'online4' in self.__exps_list:
            print
            print '-------------------------------------------------------------------------'
            print ' OFFLINE VERSUS ONLINE4 (EXPERIMENT)'
            or_filename = filename + '.tags-%d.online4_vs_offline_or.txt' % top_many_tags
            and_filename = filename + '.tags-%d.online4_vs_offline_and.txt' % top_many_tags
            tag_ranks = online_tag_ranks
            self.experiment_details(top_tags, tag_ranks, ranker, bool_pairs, or_filename, and_filename, 
                                    begin_top_many_users, end_top_many_users, step_top_many_users, '4')
        
        if 'mono' in self.__exps_list:        
            print
            print '-------------------------------------------------------------------------'
            print ' OFFLINE VERSUS MONOLITIC (EXPERIMENT)'
            or_filename = filename + '.tags-%d.mono_vs_offline_or.txt' % top_many_tags
            and_filename = filename + '.tags-%d.mono_vs_offline_and.txt' % top_many_tags
            tag_ranks = monolitic_tag_ranks
            self.experiment_details(top_tags, tag_ranks, ranker, bool_pairs, or_filename, 
                                    and_filename, begin_top_many_users, end_top_many_users, step_top_many_users, 'mono')
        
        
if __name__=='__main__':
    
    exp = TagRankExperiment()
    
    #filename = '../data/ejemplo.tagged_graph'
    filename = '../data/rpoland--2000.tagged_graph'
    #filename = '../data/jcl5m--39370.tagged_graph'
    #filename = '../data/jcl5m--11603.tagged_graph'
    #filename = '../data/MIX.tagged_graph'
    top_many_tags = 20
    
    exp.set_and_exp(True) 
    exp.set_or_exp(False) # no OR experiments now.    
    exp.set_osim(True)
    exp.set_ksim(True)
    exp.set_offline_type('gold2') # or 'gold1'
    #exp_list = ['mono', 'online1', 'online3', 'online4']
    exp_list = ['mono']
    exp.set_exps_list(exp_list)
    exp.run(filename, top_many_tags)

    
