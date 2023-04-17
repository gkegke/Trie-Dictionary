#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pickle
import time
import random
from datetime import datetime as dt, timedelta
import arrow

class DTrie:

    """

    An implementation of a Trie using inbuilt python dictionaries.
    
    Contents

     - __init__
     - __len__
     - __str__
     - __contains__

     # utility funcs
     - save_to_file

     # mutate funcs
     - insert
     - insert_many

     # Core search/retrieval funcs
     - _get_prefix_node (helper only)
     - iter_get_matches
     - recur_get_matches
     - shallow_prefix_search
     - deep_prefix_search

     # Nice to haves
     - word_in

     # Planned to Implement
     - TODO: DELETE

     # Not Implemented
     - 

     TODOS

      - Mid Priority
        - Delete method


    """

    def __init__(self, _use_set=False):
        """
        Initialization of a Trie made out of dictionaries.

        # Args

        @fpath
          - optional file path to a pickle file to read a "preinitialized"
          DTrie from to speed up initialization.

        @_use_set
          - optionally save each added word to a set to speed up certain
          less core functions, such as tests for existence.

        # Returns
        
        None
        
        ## Core

        Uses a dictionary as it's "nodes" since this is more of a "for fun"
        thing than anything too serious. Most of the implemenation should
        be easily changable to work with a class Node based system (currently
        a low priority TODO for me).

        ## Optional

        # pickling to/from file

        There's an optional fpath input to save/load the state of a Trie to/from a
        file. This is mainly to speed up initialization of the Trie in cases
        where the dataset is large.

        # can save words added to the Trie to a set

        _use_set allows you to initialize a set which from then on saves all
        added words to it. This can speed up tests for whole word existence by a
        respectable amount in exchange for a reasonable amount of memory.

        Tries are superior to tests for prefix-existences i.e. whether words
        beginning with a prefix such as "he" exists in the Trie ("hey", "hello",...),
        but for whole word existence tests, sets are still superior.
        """

        self.Trie = dict()
        self.length = 0

        # _use_set settings
        if _use_set == True:

            self._use_set = True
            self.words_set = set()

        else:

            self._use_set = False

    def __len__(self):
        return self.length

    def __str__(self):
        """

        # Args

        None

        # Returns

        str - a string that displays the current words found in the DTrie.

        In two formats currently,

        <=20 words
         - simple, shows the <20 words in a list

        > 20 words
         - more complex, shows the first 10 and last 10

        """

        if self.length <= 20:

            res = [
                "\nResults: "
                "{} words in total\n".format(self.length),
                *self.deep_prefix_search()
            ]

        else:

            wf = self.recur_get_matches()
            wr = self.recur_get_matches(forward=False)

            first_10 = [w for _, w in zip(range(10), wf)]
            last_10 = reversed([w for _, w in zip(range(10), wr)])

            res = [
                "\nResults: "
                "\nDisplaying 20 of {} words in total\n".format(self.length),
                *first_10,
                "\n......\n",
                *last_10,
                "\n"
            ]

        return "\n".join(res)

    def __contains__(self, word):
        return self.word_in(word)

    # utility funcs

    def save_to_file(self, fpath):
        """
        Utility function to help speed up the initialization of a Trie.

        # Args

        @fpath - file path to the pickle file to write to

        # Returns

        None

        Can shave a few seconds given a word list of ~500k. Reading from
        file means the Trie doesn't have to insert all the words again
        everytime.

        Uses the pickle library. Json was considered, but dictionaries with
        True as keys become convoluted if you switch between python and
        json.
        """

        with open(fpath, "wb+") as wf:
            self.Trie["__length__"] = self.length

            if self._use_set == True:
                self.Trie["__wordset__"] = self.words_set

            pickle.dump(self.Trie, wf, protocol=pickle.HIGHEST_PROTOCOL)

            del self.Trie["__length__"]

            if "__set__" in self.Trie:
                del self.Trie["__wordset__"]

    def load(self, fpath):

        with open(fpath, "rb") as rf:
            self.Trie = pickle.load(rf)
            self.length = self.Trie["__length__"]
            del self.Trie["__length__"]

            # _use_set settings
            if "__wordset__" in self.Trie:
                self.words_set = self.Trie["__wordset__"]
                self._use_set = True

                del self.Trie["__wordset__"]

            else:
                self._use_set = False

    # behaviour funcs

    def insert(self, word):
        """

        # Args
        @word - string

        # Returns
        None

        Inserts word into Trie
        """

        if self._use_set == True:

            if word in self.words_set:
                return

            self.words_set.add(word)

        curr = self.Trie

        for c in word:

            if c not in curr:
                curr[c] = dict()

            curr = curr[c]

        curr[True] = True
        self.length += 1

    def insert_many(self, iterable):
        """

        # Args
        @iterable - []string

        # Returns
        None

        Inserts all the words in an iterable into
        the Trie
        """
        for word in iterable:
            self.insert(word)

    # search funcs

    def _get_prefix_node(self, prefix):
        if prefix == None:
            return self.Trie, []

        curr = self.Trie

        for c in prefix:
            if c not in curr:
                return False, []
            curr = curr[c]

        return curr, list(prefix)

    def iter_get_matches(self, prefix=None, forward=True):
        """
        Used to create a generator that yields matches in ascending form.

        i.e. given prefix "h": hat -> hello -> hey -> ...

        This is useful for use cases where you have a very large number of matches,
        and to make the output more human readable, you limit the number of results
        displayed to say the first 10 and the last 10 results.
        """

        start, plist = self._get_prefix_node(prefix)

        if start == False:
            return []

        stack = [(start, plist)]

        while stack:

            curr = stack.pop()

            citems = curr[0].items() if not(forward) else reversed(curr[0].items())

            for k,v in citems:

                if k == True:

                    yield "".join(curr[1])

                else:

                    stack.append((v, curr[1] + [k]))


    def recur_get_matches(self, prefix=None, forward=True):
        """
        """
        def helper(node, letters):

            nitems = node.items() if forward else reversed(node.items())

            for k,v in nitems:
                if k == True:
                    yield "".join(letters)
                else:
                    yield from helper(v, letters+[k])

        curr, plist = self._get_prefix_node(prefix)

        if curr == False:
            return []
 
        # unecessary but to keep it simple
        for w in helper(curr, plist):
            yield w 


    def shallow_prefix_search(self, prefix=None, _max=20):
        """
        """

        _n = _max // 2

        wf = self.recur_get_matches(prefix)
        wr = self.recur_get_matches(prefix, forward=False)

        first_n = [w for _, w in zip(range(_n), wf)]
        last_n = [w for _, w in zip(range(_n), wr)]

        result = list(set(first_n + last_n))
        result.sort()

        return result

    def deep_prefix_search(self, prefix=None):
        """

        # Args
        @node - Starting "node" from which to search for all the
        sub-words

        # Returns
        results - []string 

        Returns a list of all the words contained in the Trie, given
        a starting node.
        """

        def helper(val, letters):
            if val == True:
                print(val, letters, len(results))

            for key,val in val.items():

                if key == True:
                    results.append("".join(letters))
                else:
                    helper(val, letters + [key])

        curr, plist = self._get_prefix_node(prefix)

        if curr == False:
            return []

        results = []

        for key, val in curr.items():
            if key == True:
                results.append(prefix)
                continue

            helper(val, plist + [key])

        return results

    def word_in(self, word):

        if self._use_set == True:
            return word in self.words_set

        curr = self.Trie
        for c in word:
            if c not in curr:
                return False
            curr = curr[c]

        if True in curr:
            return True
        
        return False

