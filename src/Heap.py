class Heap:

    def __init__(self, compare=cmp):
        """\
Set a new heap.  If COMPARE is given, use it instead of built-in comparison.

COMPARE, given two items, should return negative, zero or positive depending
on the fact the first item compares smaller, equal or greater than the
second item.
"""
        self.compare = compare
        self.array = []
        self.pos = {}

    def __call__(self):
        """\
A heap instance, when called as a function, return all its items.
"""
        return self.array

    def __len__(self):
        """\
Return the number of items in the current heap instance.
"""
        return len(self.array)

    def __getitem__(self, index):
        """\
Return the INDEX-th item from the heap instance.  INDEX is usually zero.
"""
        return self.array[index]

    def push(self, item):
        """\
Add ITEM to the current heap instance.
"""
        array = self.array
        compare = self.compare
        array.append(item)
        self.pos[item] = len(array) - 1
        high = len(array) - 1
        while high > 0:
            low = (high-1)/2
            if compare(array[low], array[high]) <= 0:
                break
            self.pos[array[high]] = low
            self.pos[array[low]] = high
            array[low], array[high] = array[high], array[low]
            high = low

    def pop(self):
        """\
Remove and return the smallest item from the current heap instance.
"""
        array = self.array
        item = array[0]        
        if len(array) == 1:
            del array[0]
        else:
            compare = self.compare
            del self.pos[array[0]]            
            array[0] = array.pop()
            self.pos[array[0]] = 0
            low, high = 0, 1
            while high < len(array):
                if ((high+1 < len(array)
                     and compare(array[high], array[high+1]) > 0)):
                    high = high+1
                if compare(array[low], array[high]) <= 0:
                    break
                self.pos[array[high]] = low
                self.pos[array[low]] = high                
                array[low], array[high] = array[high], array[low]
                low, high = high, 2*high+1
        return item

    def pop_item(self, item):        
        return self.pop_pos(self.pos[item])

    def pop_pos(self, pos=0):
        """\
Remove and return the smallest item from the current heap instance.
"""
        array = self.array
        item = array[pos]
        if len(array) == 1:
            del array[pos]
        else:
            compare = self.compare
            del self.pos[array[pos]]
            if pos == len(array) - 1:
                array.pop()                
            else:
                array[pos] = array.pop()            
                self.pos[array[pos]] = pos
            low, high = pos, pos*2 + 1
            while high < len(array):
                if ((high+1 < len(array)
                     and compare(array[high], array[high+1]) > 0)):
                    high = high+1
                if compare(array[low], array[high]) <= 0:
                    break
                self.pos[array[high]] = low
                self.pos[array[low]] = high
                array[low], array[high] = array[high], array[low]
                low, high = high, 2*high+1
        return item

def test(n=2000):
    heap = Heap()
    for k in range(n-1, -1, -1):
        heap.push(k)
    for k in range(n):
        assert k+len(heap) == n
        assert k == heap.pop()

def test2(n=2000):
    heap = Heap()
    for k in range(n-1, -1, -1):
        heap.push(k)
    for k in range(n):
        assert k+len(heap) == n
        item = heap.pop_item(k)
        assert k == item

def main():
    test(10000)
    test2(10000)

if __name__ == "__main__":
    main()
