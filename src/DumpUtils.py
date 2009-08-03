
import pickle

def dump_obj(filename, obj):    
    f = open(filename, 'w')
    pickle.dump(obj, f)
    f.close()

def load_obj(filename):
    f = open(filename, 'r')
    obj = pickle.load(f)
    f.close()
    return obj

