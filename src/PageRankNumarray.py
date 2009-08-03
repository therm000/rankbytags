
from numpy import *

def pageRankGenerator(
    At = [array((), int32)], 
    numLinks = array((), int32),  
    ln = array((), int32),
    alpha = 0.85, 
    convergence = 0.01, 
    checkSteps = 10,
    maxSteps = 50
    ):
    """
    Compute an approximate page rank vector of N pages to within some convergence factor.
    @param At a sparse square matrix with N rows. At[ii] contains the indices of pages jj linking to ii.
    @param numLinks iNumLinks[ii] is the number of links going out from ii. 
    @param ln contains the indices of pages without links
    @param alpha a value between 0 and 1. Determines the relative importance of "stochastic" links.
    @param convergence a relative convergence criterion. smaller means better, but more expensive.
    @param checkSteps check for convergence after so many steps
    @param maxSteps stop after so many steps
    """

    # the number of "pages"
    N = len(At)

    # the number of "pages without links"
    M = ln.shape[0]

    # initialize: single-precision should be good enough
    iNew = ones((N,), float32) / N
    iOld = ones((N,), float32) / N

    done = False
    totalSteps = 0
    while not done and totalSteps < maxSteps:

        # normalize every now and then for numerical stability
        iNew /= sum(iNew)
    
        for step in range(checkSteps):

            # swap arrays
            iOld, iNew = iNew, iOld

            # an element in the 1 x I vector. 
            # all elements are identical.
            oneIv = (1 - alpha) * sum(iOld) / N

            # an element of the A x I vector.
            # all elements are identical.
            oneAv = 0.0
            if M > 0:
                oneAv = alpha * sum(iOld.take(ln, axis = 0)) * M / N
        
            # the elements of the H x I multiplication
            ii = 0 
            while ii < N:
                page = At[ii]
                h = 0
                if page.shape[0]:
                    h = alpha * dot(
                        iOld.take(page, axis = 0),
                        1. / numLinks.take(page, axis = 0)
                        )
                iNew[ii] = h + oneAv + oneIv
                ii += 1
                
            print 'pagerank total steps: %d' % totalSteps
            totalSteps += 1
        
        diff = iNew - iOld
        error = sqrt(dot(diff, diff)) / N
        done = (error < convergence)
        print 'error: %f convergence when error less than %f' %  (error, convergence)
        
        yield iNew


def transposeLinkMatrix(
    outGoingLinks = [[]]
    ):
    """
    Transpose the link matrix. The link matrix contains the pages each page points to.
    But what we want is to know which pages point to a given page, while retaining information
    about how many links each page contains (so store that in a separate array),
    as well as which pages contain no links at all (leaf nodes).

    @param outGoingLinks outGoingLinks[ii] contains the indices of pages pointed to by page ii
    @return a tuple of (incomingLinks, numOutGoingLinks, leafNodes)
    """

    nPages = len(outGoingLinks)
    # incomingLinks[ii] will contain the indices jj of the pages linking to page ii
    incomingLinks = [[] for ii in range(nPages)]
    # the number of links in each page
    numLinks = zeros(nPages, int32)
    # the indices of the leaf nodes
    leafNodes = []

    for ii in range(nPages):
        if len(outGoingLinks[ii]) == 0:
            leafNodes.append(ii)
        else:
            numLinks[ii] = len(outGoingLinks[ii])
            # transpose the link matrix
            for jj in outGoingLinks[ii]:
                incomingLinks[jj].append(ii)
    
    incomingLinks = [array(ii) for ii in incomingLinks]
    numLinks = array(numLinks)
    leafNodes = array(leafNodes)

    return incomingLinks, numLinks, leafNodes
                

def pageRank(
    linkMatrix = [[]],
        alpha = 0.85, 
    convergence = 0.01, 
    checkSteps = 10
        ):
    """
    Convenience wrap for the link matrix transpose and the generator.

    @see pageRankGenerator for parameter description
    """
    incomingLinks, numLinks, leafNodes = transposeLinkMatrix(linkMatrix)

    for gr in pageRankGenerator(incomingLinks, numLinks, leafNodes, alpha = alpha, convergence = convergence, checkSteps = checkSteps):
            final = gr

    return final
    
    
class PageRankNumarray:
    
    def __init__(self, nodes, edges):
         
         self.__nodes = nodes         
    
         # code into integers, to avoid use of dictionaries everywhere.
         print 'mapping nodes to integers'
         map_node_int = {}
         map_int_node = {}     
         for i in range(len(nodes)):
             node = nodes[i]
             map_node_int[node] = i
             map_int_node[i] = node
    
         print 'extracting output neighbors per node'
         outbound = {}
         for n1, n2 in edges:
             n1 = map_node_int[n1]
             n2 = map_node_int[n2]
             if not n1 in outbound.keys():
                 outbound[n1] = [n2]
             else:
                 outbound[n1].append(n2)
         self.__outbound = outbound
         
         print 'building neighbor list per node.'
         self.__links = []
         for node in range(len(nodes)):
             if not node in self.__outbound.keys():
                 self.__links.append([])
             else:
                 self.__links.append(self.__outbound[node])
             
    def rank(self):
        ranking = pageRank(self.__links)
        final_rank = zip(self.__nodes, ranking)
        return final_rank
    
if __name__=='__main__':
    
    size = 100000
    nodes = range(size)
    edges = [(ii,ii+1) for ii in range(size-1)]
    edges.append((size-1,0))
    pr = PageRankNumarray(nodes, edges)
    
    import time
    print 'ring size %d' % size
    print "starting"
    print time.gmtime()
    
    ranking = pr.rank()
    
    print "stopping"
    print time.gmtime()
    