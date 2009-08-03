
from EggOMatic import EggOMatic
from ExtractTags import Tags
from RankByTags import RankerByTags

from Utils import rank_dist_ksim, rank_dist_osim

class EggOMaticExperiments:

    __exp_OSim = True
    __exp_KSim = True
    
    __offline_list = ['offline1'] # or 'gold2'
    __online_list = ['online1']
    __top_tags = 20
    
    __begin_top_many_users = 1
    __end_top_many_users = 10
    # exponential step 2, 4 ,8 16
    __step_top_many_users = 2

    def set_top_tags(self, top_tags=20):
        self.__top_tags = top_tags

    def set_forb_tags(self, forb_tags):
        self.__forb_tags = forb_tags

    def set_offline_list(self, type=['offline1']):
        self.__offline_list = type

    def set_online_list(self, list):
        self.__online_list = list

    def set_error_list(self, list=['osim','ksim']):
        self.__error_list = list

    def __init__(self, dataset, compute_ranks=True,  compute_mono_rank=True, build_index=True, max_per_rank=10000000000, top_tags=None):
        self.__dataset = dataset
        self.__eggomatic = EggOMatic(dataset, compute_ranks, compute_mono_rank, build_index, max_per_rank, top_tags)
        
    def __calc_error_save(self, offline_type, online_type, type_rank, error_type):
        f = open(self.__dataset + '.' + offline_type + '_VS_' + online_type + '.' + error_type, 'a')
        print 'writing ' + self.__dataset + '.' + offline_type + '_VS_' + online_type + '.' + error_type
        
        offline_rank = type_rank[offline_type]
        online_rank = type_rank[online_type]
        for top_many_users in [self.__step_top_many_users**i for i in range(self.__begin_top_many_users,self.__end_top_many_users)]:
            float_error, info_val = eval('rank_dist_%s(offline_rank, online_rank, top_many_users)' % error_type)
            if info_val >= 0: 
                f.write('%d %d %f \n' % (top_many_users, len(offline_rank), float_error))

    def __empty_result_files(self):        
        for offline_type in self.__offline_list:            
            for online_type in self.__online_list:                
                for error_type in self.__error_list:
                    f = open(self.__dataset + '.' + offline_type + '_VS_' + online_type + '.' + error_type, 'w')
                    f.close()
        
    def run(self):
        filename = self.__dataset + '.tagged_graph'
        tags_filename = filename + '.ranks/all.tags'
        f = open(tags_filename)
        lines = []
        for i in range(self.__top_tags + 1000):
            lines.append(f.readline())
        f.close()
        top_tags = map(lambda line: line.strip().split(' ')[0], lines)
        top_tags = filter(lambda x:not x in self.__forb_tags, top_tags)[0:self.__top_tags]
        #top_tags = tags.get_top_tags(self.__top_tags)
        #top_tags = map(lambda x: x[0], top_tags)
        
        self.__ranker = RankerByTags()
        self.__ranker.load(filename)

#        tag_sets = []
#        for i in range(len(top_tags)):
#	    tag1 = top_tags[i]
#            for tag2 in top_tags[:i-1]:
#                tag_sets.append((tag1, tag2))

        # empty result files
        self.__empty_result_files()

	count = 0
        nro_exps = len(top_tags)*(len(top_tags)-1) / 2
        len_top_tags = len(top_tags)
        for i in range(1,len(top_tags)):
	    tag1 = top_tags[i]
            for tag2 in top_tags[:i]:
                ranks = self.__eggomatic.rank_by_tags([tag1, tag2])
                type_rank = {}
                type_rank['offline1'] = ranks[0]                 
                type_rank['mono'] = ranks[1]
                type_rank['online1'] = ranks[2]
                type_rank['online2'] = ranks[3]
                type_rank['online3'] = ranks[4]
                type_rank['online4'] = ranks[5]
                type_rank['offline2'] = ranks[6]
                type_rank['online6'] = ranks[7]
		if (tag1=='portugal' and tag2=='music') or (tag2=='portugal' and tag1=='music'):
			f = open('ranks.txt','w')
			for trank, rank in type_rank.iteritems():
				f.write('----------------------------------------\n')
				f.write('%s\n' % trank)
				for t in rank:
					f.write('%s\n' % str(t))
			f.close()
                for offline_type in self.__offline_list:                
                    for online_type in self.__online_list:                    
                        for error_type in self.__error_list:
                            print 'for tags: %s %s' % (tag1,tag2)
                            self.__calc_error_save(offline_type, online_type, type_rank, error_type)
                count += 1
                print 'NUMBER OF EXPERIMENTS/PAIRS COMPLETED: %d of %d' % (count, nro_exps)
            print 'EXPERIMENTS COMPLETED FOR THE TOP %d of %d TAGS (all pairs)' % (i,len_top_tags)
            
        
if __name__ == '__main__':
    
    #dataset = '../data/ejemplo'        
    #dataset = '../data/rpoland--2000'
    #dataset = '../data/jcl5m--39370'
    #dataset = '../data/MIX'
    #dataset = '../data/flickr_med'
    #dataset = '../data/youtube'
    #dataset = '../data/yt_nd'
    #dataset = '../data/fr_nd'
    #dataset = '../data/webist'
    dataset = '../data/yt_nd_mini'

    forb_tags = ['abigfave', 'diamondclassphotographer', 'aplusphoto', 'anawesomeshot', 'superbmasterpiece', 'nikon', 'canon', 'goldstaraward', 'blueribbonwinner', 'platinumphoto', 'supershot', 'theperfectphotographer', 'impressedbeauty', 'naturesfinest', 'theunforgettablepictures', 'flickrdiamond', 'superaplus', 'to', 'you', 'video', 'youtube']
    
    compute_ranks = True
    compute_mono_rank = True
    build_index = False
    top_tags = 2
    top_tags_all_ranks = top_tags + len(forb_tags)
    max_rank = 128


    exps = EggOMaticExperiments(dataset, compute_ranks, compute_mono_rank, build_index, max_rank)
    exps.set_error_list(['osim', 'ksim'])    
    exps.set_offline_list(['offline1', 'offline2'])
    exps.set_online_list(['online1','mono','online3','online4']) #,'online6'])
    exps.set_top_tags(top_tags)
    exps.set_forb_tags(forb_tags)    
    exps.run()
