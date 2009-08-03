from nsed import NSED
import time

# Fotolog Harvester
class Fotolog(NSED):

    def __fotolog_strip(self, match):
                return match.group()[len('www.fotolog.com/'):-len('/"')].replace(',','')

    def __init__(self):
        url = 'ff.fotolog.com'
        get = '/all.html?'
        params = {}
        qparam = 'u'
        regex = 'www.fotolog.com\/[a-z0-9_-]+\/"'
        strip = self.__fotolog_strip
        super(Fotolog,self).__init__(url, get, regex, strip, params, qparam)
        self.__failures = 0

    def neightbors(self, flog):

        ns = []
        page_param = 'p'
        page = 1
        self.update_params(page_param, page)
        matches = self.matches_query(flog)[1:]
        while len(matches) > 0 and not matches[0] in ns and page < 4:
            for m in matches:
                if not m in ns:
                    ns.append(m)
            page += 1
            self.update_params(page_param, page)
            matches = self.matches_query(flog)[1:]
        return ns

    def harvest(self, seeds, max_nodes=3 ):

        failures = 0
        adj = {}
        stack = seeds
        n = len(adj.keys())
        while n < max_nodes and len(stack) > 0:            
            node = stack.pop(0)
            print 'size harvested -> %d' % len(adj.keys())
            if not node in adj.keys():
                adj[node] = []
            else:
                continue
            n = len(adj.keys())
            if n >= max_nodes:
                break
            neighs= []
            try:
                neighs = self.neightbors(node)
            except:
                failures += 1
                print 'FAILURE: #%d at %d people' % (failures, n)
                if failures >= 100:
                    print 'breaking at 100 failures'
                    break
                else:
                    print 'sleep 20 seconds after failure'
                    time.sleep(20)
            for neigh in neighs:
                if not neigh in adj[node] and (not neigh in adj.keys() or not node in adj[neigh]):
                    adj[node].append(neigh)
                    if not neigh in adj.keys():
                        stack.append(neigh)
            n = len(adj.keys())

        for k in adj.keys():
            for ad in adj[k]:
                if not ad in adj.keys() or not k in adj[ad]:
                    adj[k].remove(ad)
            if len(adj[k])==0:
                del adj[k]

        self.__adj = adj

    # run after update_edges
    def save_custom(self, file_path):
        f = open(file_path, 'w')
        # save base
        f.write('%d\n' % self.get_base())
        # save total results
        f.write('%d\n' % self.results_total())
        for n in self.__adj.keys():
            f.write('%s\n' % n )
            f.write('%d\n' % 1)
        f.write('----\n')
        for n in self.__adj.keys():
            for neigh in self.__adj[n]:
                if neigh in self.__adj.keys():
                    e = (n, neigh, 0.5)
                    f.write('%s\n' % e[0] )
                    f.write('%s\n' % e[1] )
                    try:
                        f.write('%f\n' % e[2] )
                    except:
                        print 'BUG: e[2] = %s' % str(e[2])
                        f.write('2.00\n')
        f.close()

    def tests(self):
        """
>>> from fotolog import Fotolog
>>> f = Fotolog()
a  
FAILURE!!!
0
>>> f.harvest(['campooooo'],1)
>>> print f.harvest(['campooooo'],1)
None
>>> print f.harvest(['campooooo'],2)
campooooo
campooooo
campooooo
campooooo
None
>>> print f.neightbors('campooooo')
campooooo
campooooo
campooooo
campooooo
['mokosita', 'soy_tu_inocencia', 'sakadisiimaa', 'dooriii', 'todalanochedjs', 'noe_electronik', 'darkclowndam', 'viciousrocker', 'ladyblue_x4', 'princesa_69', 'amelitas', 'rubiezzitaglamm', 'ooraaleee', 'l0ve_of_h0rse', 'uplifting_way', 'ninia_veneno', 'flopiiitaa_a', 'hallus', 'caballos_110', 'anisssssssssssss', 'llena_tu_alma', 'electronicachica', 'complicada__', 'laura_ms', 'como_perraygata', 'see_you_wherever', 'touch_the_sun', 'annnnie', 'panzaa', 'electrica', 'snow_whiteequeen', 'cybertronix', 'lucycamaleona', 'romizz', 'sweet_spices', 'yosoytone', 'soydmn', 'florciz_06', 'le_team', 'horsesflog', 'miss_heart', 'zinti', 'japangirl', 'joachimm', 'cream_clubland7', 'jav_meeeee', 'chuky_chan', 'marinx', 'colour_me_blind', 'blondieliciouus', 'muralla22', 'batidodecereza', 'sweetindiference', 'maruflores', 'mind_over_matter', 'poshitas', 'errrick', 'darioef2', 'estrellasenmi', 'blind_limon']
>>> 
        """
        pass

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
#    _test()

    f = Fotolog()

    u = 'florkey'
    max_nodes = 500

    f.harvest([u], max_nodes)
    f.save_custom('data/%s-%d-.graph' % (u,max_nodes))
