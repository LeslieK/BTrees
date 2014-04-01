"""
search for terms in BTree index (index.txt)
"""
import pickle
from indexWeb import IndexWeb  # used by pickle


print("Start searching")
with open("index.txt", "rb") as f:
    index2 = pickle.load(f)

with open("searchterms.txt", 'r', encoding='latin-1') as f:
    for word in f:
        values = index2.get(word.strip())
        if values:
            print(word),
            for val in values:
                print(val)
        else:
            print(word, "not found")
print("done searching")
print(index2.size())
