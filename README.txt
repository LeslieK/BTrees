index.txt: a pickled file that stores the index of 271 web pages starting from the root url:
www.princeton.edu

searchIndex.py: run this script to search the index for keywords. This script reads the keywords
from the file "searchterms.txt"

indexWeb.py: run this script to build a web index of urls crawled from ROOTURL.
Resulting index is pickled to the file "index.txt"

searchterms.txt: a file that contains search words

BTreeNode**.txt : a file that stores a node of the BTree index. When the node is part of the search path, the searchIndex.py script opens the file and stores the data in memory.

BTreeNode2 is the root node. It resides in memory after index.txt is unpickled. This is the only node that always resides in memory.

