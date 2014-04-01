"""
environment is 3.3

implementation of a Page class and a BTree class
"""
from bs4 import BeautifulSoup

import pickle
import copy
import re

#  BTree order (M) => M - 1 keys per node
BTORDER = 1000
p = re.compile(r'[^;.,!:\&\-\"\/\/]')   # remove punctuation marks
js = re.compile(r'\bvar |\bfunction\(') # remove javascript

class Entry(object):
    def __init__(self):
        self.key = 'word'     # a word
        self.values = set()   # a set of urls
        self.next = None      # a key-value or key-next pair

class Page(object):
    """
    page: a node in the BTree
    """
    def __init__(self, bottom, pagenum):
        self.bottom = bottom               # True: page is external
        self.keylist = [None] * BTORDER    # stores up to M - 1 key
        self.m = 0                         # number of keys stored on page
        self.name = 'BTreeNode' + str(pagenum) + '.txt'

    def close(self):
        """
        write a page in memory to disk
        """
        with open(self.name, 'wb') as fp:
            pickle.dump(self, fp)

    def addValue(self, key, value):
        for e in self.keylist[:self.m]:
            if e.key == key:
                e.values.add(value)

    def add(self, key, value, nextpage):
        """
        key-value: invoked by an external page
        key-next: invoked by an internal page
        maintains sorted order
        """
        t = Entry()
        t.key = key
        if value:
            t.values.add(value)
        else:
            t.next = nextpage

        # insert t into keylist
        if self.m == 0:
            self.keylist[0] = t
        else:
            self._insert(t)
        self.m += 1

    def _insert(self, entry):
        def binary_search(entry):
            lo = 0
            hi = self.m - 1
            while lo <= hi:
                mid = lo + (hi - lo) // 2
                if entry.key < self.keylist[mid].key:
                    hi = mid - 1
                elif entry.key > self.keylist[mid].key:
                    lo = mid + 1
                else:
                    return mid
            return lo
        i = binary_search(entry)

        # shift to right
        for j in range(self.m, i, -1):
            self.keylist[j] = self.keylist[j - 1]
        # insert here
        self.keylist[i] = entry

    def isExternal(self):
        """
        True if self is external, False otherwise
        """
        return self.bottom

    def contains(self, key):
        """
        True if page isExternal and page contains key
        False otherwise
        """
        for e in self.keylist[:self.m]:
            if key == e.key:
                return True
        return False

    def getNext(self, key):
        """
        returns the root page of the subtree that could contain key
        returns an internal page one level lower in the tree
        """
        for i in range(self.m):
            if i + 1 == self.m or key < self.keylist[i + 1].key:
                pagename = self.keylist[i].next.name
                return openPage(pagename)
        return

    def isFull(self):
        """
        True is page contains M elements
        """
        return self.m == BTORDER

    def split(self, pagenum):
        """
        splits a full page into 2 halves:
        lefthalf: M/2 items (original page)
        righthalf: M/2 items (a newly created page; brought into internal memory)
        returns (to its parent page) a reference to righthalf
        """
        righthalf = Page(self.bottom, pagenum)
        righthalf.keylist[:BTORDER // 2] = \
            copy.deepcopy(self.keylist[BTORDER // 2:])
        righthalf.m = BTORDER // 2

        lefthalf = self
        lefthalf.m = BTORDER // 2
        lefthalf.close()

        return righthalf

    def splitRoot(self, pagenum):
        """
        split root and create a new root page
        """
        righthalf = Page(True, pagenum)
        righthalf.keylist[:BTORDER // 2] = \
            copy.deepcopy(self.keylist[BTORDER // 2:])
        righthalf.m = BTORDER // 2

        lefthalf = self
        lefthalf.m = BTORDER // 2

        # add lefthalf and righthalf pages to new root page
        
        new_page = Page(False, pagenum + 1)

        tRIGHT = Entry()
        tRIGHT.key = righthalf.keylist[0].key
        tRIGHT.next = righthalf

        tLEFT = Entry()
        tLEFT.key = lefthalf.keylist[0].key
        tLEFT.next = lefthalf

        new_page.keylist[0] = tLEFT
        new_page.keylist[1] = tRIGHT
        new_page.m = 2

        # close lefthalf page, righthalf page
        lefthalf.close()
        righthalf.close()

        return new_page


class BTreeST(object):
    """
    balanced M order B-tree
    underlying data structure for a reverse web index
    each node (page) is stored as a file on disk
    word => file that contains word
    """

    def __init__(self):
        self.root = Page(True, 0)
        self.numpages = 1
        self.N = 0     #  number of words indexed

    def size(self):
        return self.numpages, self.N

    def contains(self, key):
        """
        True if key is in tree
        False otherwise
        """
        def helper_contains(p, key):
            if p.isExternal():
                return p.contains(key)
            else:
                return helper_contains(p.next(key), key)
        return helper_contains(self.root, key)

    def get(self, key):
        """
        if key in ST: return value
        else return None
        """
        def helper_get(page, key):
            """
            return value associated with key
            """
            # page is external
            if page.isExternal():
                for e in page.keylist[:page.m]:
                    if key == e.key:
                        return e.values
                return
            else:
                nextpage = page.getNext(key)
                return helper_get(nextpage, key)
        return helper_get(self.root, key)

    def add(self, r):
        """
        add r to BTree
        r : a response obj from a GET request
        """
        soup = BeautifulSoup(r.text, "lxml")
        list_of_words = []
        
        for string in soup.stripped_strings:
            if string and not js.search(string):
                words = (word for word in string.split() if p.match(word) if word not in list_of_words)
                for word in words:
                    list_of_words.append(word)
        list_of_words.sort()

        def helper_add(page, word):
            """
            page: stored as a file on disk
            list_of_words: list of keys added to a page
            """
            #  external page
            if page.isExternal():
                if not page.contains(word):
                    page.add(word, r.url, None)
                    self.N += 1  # counts number of words
                else:
                    page.addValue(word, r.url)
                return

            # internal page
            nextpage = page.getNext(word)  # returns a new, open page
            if not nextpage:
                return("file not found")
            helper_add(nextpage, word)
            if nextpage.isFull():
                # numpages: next page number to be used
                new_page = nextpage.split(self.numpages)  
                self.numpages += 1  # accounts for new righthalf

                # link to new page
                page.add(new_page.keylist[0].key, value=None, nextpage=new_page)
                new_page.close()
            nextpage.close()
            return

        for word in list_of_words:
            helper_add(self.root, word)
            if self.root.isFull():
                # split root
                self.root = self.splitRoot()
                self.numpages += 2
                print(self.root.m)  # debug
                
    def splitRoot(self):
        """
        split root and create a new root page
        """
        return self.root.splitRoot(self.numpages)
        
def openPage(filename):
    """
    bring an external page into internal memory
    """
    with open(filename, "rb") as f:
        page = pickle.load(f)
    return page


