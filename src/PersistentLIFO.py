
import os

class PersistentLIFO:
    
    def __init__(self, name, per_file=1024, folder='./stacks' ):
        self.__name = name
        self.__folder = folder
        
        self.__per_file = per_file            
        self.__file = 0
        self.__offset = 0
        self.__pop_file = 0
        self.__pop_offset = 0
        self.__create_file()
            
    def __save_info(self):            
        f = open('%s/%s.stack_info' % (self.__folder,self.__name), 'w')
        f.write('%d\n' % self.__per_file)
        f.write('%d\n' % self.__file)
        f.write('%d\n' % self.__offset)
        f.write('%d\n' % self.__pop_file)
        f.write('%d\n' % self.__pop_offset)
        f.close()            
        
    def __create_file(self):
        file = '%s/%s-%d.stack_data' % (self.__folder,self.__name,self.__file)
        try:        
            os.remove(file)
        except:
            pass
        f = open(file, 'w')        
        #f.write('\n')
        f.close()
            
    def size(self):
        return (self.__file - self.__pop_file) * self.__per_file + self.__offset - self.__pop_offset
            
    # str(item) must not have newlines.
    def push(self, item):
        f = open('%s/%s-%d.stack_data' % (self.__folder,self.__name,self.__file), 'a')
        f.write('%s\n' % str(item))        
        f.close()
        
        self.__offset += 1
        if self.__offset == self.__per_file:
            self.__offset = 0
            self.__file += 1
            self.__create_file()
        self.__save_info()
            
    # str(item) must not have newlines.
    def pop(self):        
        
        if self.size() < 1:
            raise Exception('the PersistentLIFO is empty, trying to pop!')
        
        f = open('%s/%s-%d.stack_data' % (self.__folder,self.__name,self.__pop_file), 'r')
        lines = f.readlines()
        f.close()
        
        self.__save_info()
        if self.size() == 0:
            self.__create_file()
            
        self.__pop_offset += 1
        if self.__pop_offset == self.__per_file:
            self.__pop_offset = 0
            self.__pop_file += 1            
            
        return lines[self.__pop_offset].strip()
    
    def has(self, item):        

        if self.size() < 1:
            return False

        f = open('%s/%s-%d.stack_data' % (self.__folder,self.__name,self.__pop_file), 'r')
        lines = f.readlines()
        f.close()
        for i in range(self.__pop_offset, self.__per_file):
            line = lines[i].strip()            
            if line == item:
                return True 
        
        for file in range(self.__pop_file + 1, self.__file-1):
            f = open('%s/%s-%d.stack_data' % (self.__folder,self.__name,file), 'r')
            lines = f.readlines()
            f.close()
            for i in range(self.__per_file):
                line = lines[i].strip()            
                if line == item:
                    return True 
                
        f = open('%s/%s-%d.stack_data' % (self.__folder,self.__name,self.__file), 'r')
        lines = f.readlines()
        f.close()
        for i in range(self.__offset):
            line = lines[i].strip()            
            if line == item:
                return True
             
        return False
    
if __name__ == "__main__":    
    
    fifo = PersistentLIFO('test', 2)
        
    fifo.push('jajaj')
    fifo.push('jiji')
    fifo.push('zarasazarasa')
    fifo.push('blubluuuuuuuuuuuu')
    
    print 'must say True --> %s' % str(fifo.has('jiji'))    
    
    print fifo.pop()
    print fifo.pop()
    print fifo.pop()
    print 'must say False --> %s' % str(fifo.has('jiji'))
    print fifo.pop()
    print

    fifo.push('jajaj')
    fifo.push('jiji')
    fifo.push('zarasazarasa')
    fifo.push('blubluuuuuuuuuuuu')
    
    print fifo.pop()
    print fifo.pop()
    print fifo.pop()
    print fifo.pop()
    print
    
    
    
    
        
        
        