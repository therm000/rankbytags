
# thread imports
from threading import Thread

class NSEDThread(Thread):
    
   def __init__ (self, nsed, pairs, context=''):
       Thread.__init__(self)
       self.status = -1
       self.__nsed = nsed
       self.__pairs = pairs
       self.__context = context
       self.distances = {}
       
      
   def run(self):
      # now False, to not use threads.
      self.distances = self.__nsed.distances( self.__pairs, self.__context, False )


   
        
