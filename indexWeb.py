"""
This model builds an index of web pages.
"""
import requests
import pickle
from bs4 import BeautifulSoup
from BTrees import BTreeST

class IndexWeb(object):
    """
    an index of web pages
    each web page is stored as a file
    """
    def __init__(self):
        self.st = BTreeST()

    def add(self, r):
        self.st.add(r)

    def size(self):
        return self.st.size()

    def contains(self, key):
        return self.st.contains(key)

    def get(self, key):
        """
        key: a word
        value: list of urls
        """
        return self.st.get(key)

###########################################################

if __name__ == "__main__":

    ROOTURL = "http://www.princeton.edu"
    MAXNODES = 100
    rset = set()

    # create index
    index = IndexWeb()

    # get root page
    r = requests.get(ROOTURL)
    rset.add(r)
    numwebpages = 0

    while len(rset) < 200:
        r = rset.pop()
        index.add(r)
        numwebpages += 1
        numnodes, numwords = index.size()
        print(numnodes, numwords, numwebpages)
        if numnodes > MAXNODES:
            print("total nodes: ", numnodes)
            break
        else:
            soup = BeautifulSoup(r.text, "lxml")
            for url in soup.find_all('a'):
                # 2 lines for debugging index.get
                #if len(rset) == 2:
                #    break
                try:
                    link = url['href']
                    if 'javascript' in link:
                        continue
                    if 'http' not in link:
                        myurl = ROOTURL + link
                    else:
                        myurl = link
                    try:
                        rnext = requests.get(myurl)
                        rset.add(rnext)
                    except ConnectionError:
                        print(myurl)
                        continue
                except KeyError:
                    continue
            print("len rset", len(rset))


    while len(rset) > 0:
        r = rset.pop()
        index.add(r)
        numwebpages += 1
        numnodes, numwords = index.size()
        print(numnodes, numwords, numwebpages)
        if numnodes > MAXNODES:
            print("total nodes: ", numnodes)
            break
    print("no more web pages")

    with open("index.txt", 'wb') as fp:
            pickle.dump(index, fp)

    print("wrote index to file")


###########################################################################
    print("Start searching")

    with open("index.txt", "rb") as fp:
        index2 = pickle.load(fp)

    with open("searchterms.txt", 'r', encoding='utf-8')  as f:
        for word in f.read().split():
            values = index2.get(word)
            if values:
                print(word, ":", values)
            else:
                print(word, "not found")
    print("done searching")



