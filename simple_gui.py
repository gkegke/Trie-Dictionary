#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dearpygui.dearpygui as dpg
import random
import dbm
import json

from collections import deque
from Trie import DTrie

"""

 # Helper classes/functions
 - CONTEXT
 - get_words
 
 # viewport/windows
 - main
 - add_word_filter_window
 - add_recently_searched_window

 # Update functions
 - clear_table
 - update_word_filter_results
 - init_word_filter_results()
 - show_word_definitions


"""


class CONTEXT:
    """

    Helper class that stores all the 'global' esque
    variables.

    """

    RECENTLY_SEARCHED_MAX_STORED = 100
    FILTERED_RESULTS_MAX = 50

    def __init__(self, fpath):
        """

        Args:

          @fpath string

        Initializes,

         self.DEFINITIONS dict[string]True
           - where string = word

         self.T DTrie
           - 
         
         self.db 
          - Uses python std's libs built in k,v store for simple
          persistance

        """

        words, _defs = get_words(fpath)

        self.DEFINITIONS = _defs
        self.T = DTrie()
        self.db = dbm.open("data.db", "c")

        if "recently_searched" in self.db:
            _data = self.db["recently_searched"].decode("utf-8")
            self.recently_searched = deque(_data.split(","))
        else:
            self.recently_searched = deque()

        self.T.insert_many(words)

    def add_new_searched(self, word):

        if word not in self.recently_searched:
            self.recently_searched.append(word)

            if len(self.recently_searched) > self.RECENTLY_SEARCHED_MAX_STORED:
                self.recently_searched.popleft()

            self.db["recently_searched"] = ",".join(self.recently_searched)

    def get_recently_searched(self):
        return self.recently_searched

def get_words(fpath):
    """
    Input:

      @fpath string
        - path to the json file

    Return:
            
      @words list
        - the list of words to be searchable in the dictionary

      @word_meanings_dict
        - 

    Parse words from a json file
    """
    with open(fpath, "r") as jf:
        ws = json.load(jf)

    return ws.keys(), ws

def main():
    """

    Args: None
    Return: None

    1. The word filter window will have an intial randomly
    chosen option.

    2. Initial viewport is created, and some configuration is done.

    3. The word filter window and the recently searched window
    are added to the viewport.

    4. dearpygui starts up the app

    """

    # 1.
    default_values = [
        "happ",
        "enjoy",
        "blaz",
        "merr",
    ]

    _prefix = random.choice(default_values)

    # 2.
    dpg.create_context()
    dpg.create_viewport(title='Fast Word Finder', width=1000, height=500)

    with dpg.font_registry():
        default_font = dpg.add_font("./fonts/OpenSans.ttf", 30)

    dpg.bind_font(default_font)

    # 3.
    add_word_filter_window(_prefix)
    add_recently_searched_window()

    # 4.
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

def add_word_filter_window(_prefix):

    with dpg.window(
            label="Word filter",
            width=700, height=500, no_close=True
        ):

        dpg.add_input_text(label="Type here..", tag="query", callback=update_word_filter_results,
                           default_value=_prefix)

        with dpg.table(
            label="Words starting with..", tag="autocompleted",
            header_row=True,
            ):
            for column_name in ("A-Z", "Reverse"):
                dpg.add_table_column(label=column_name)

            init_word_filter_results(_prefix)

def add_recently_searched_window():

    with dpg.window(
        label="Recently Searched..",
        width=300, height=300,
        no_close=True,
        pos=(700, 0),
        tag="rs_window"
        ):
        with dpg.table(
            label="Word", tag="rs_table",
            header_row=True,
            ):
            for column_name in ("Last {} words..".format(_CONTEXT.RECENTLY_SEARCHED_MAX_STORED),):
                dpg.add_table_column(label=column_name)

            update_recently_searched()


def clear_table(table_tag):
    """

    Args:

      @table_tag string

    Returns:

      None

    Empties all the rows in the targeted table.

    Note: dearpygui uses string 'tags' to refer to items.
    """
    for tag in dpg.get_item_children(table_tag)[1]:
        dpg.delete_item(tag)

def update_word_filter_results(_):
    """

    Args:

      _ not used

    Returns:

      None

    Alternate Names:
     - Update the word filter results table

    1. Gets the current value from the query text_input.
    Then retrieves a given number of matches from the Trie.

    2. The update_word_filter_resultsd table, i.e. the word filter results table,
    is cleared. Then we add all the matches returned to the table.

    The left column will have words added in ascending order.
    The right column will have words added in descending order.

    """
 
    # 1. 
    q = dpg.get_value("query")

    matches = _CONTEXT.T.shallow_prefix_search(q, _max=_CONTEXT.FILTERED_RESULTS_MAX)

    # 2.

    clear_table("autocompleted")

    for i in range(len(matches)):
        with dpg.table_row(parent="autocompleted"):
            dpg.add_button(label=matches[i], user_data=matches[i], callback=show_word_definitions)
            dpg.add_button(label=matches[-i-1], user_data=matches[-i-1], callback=show_word_definitions)
    
    if len(matches) == _CONTEXT.FILTERED_RESULTS_MAX:

        with dpg.table_row(parent="autocompleted"):
            dpg.add_text("more.....")
            dpg.add_text("more.....")

def init_word_filter_results(prefix):
    """

    Helper function that updates the word filter results table,
    i.e. the 'autocompleted', with the results on an initial
    prefix.

    """
    matches = _CONTEXT.T.shallow_prefix_search(prefix, _max=50)

    for i in range(len(matches)):
        with dpg.table_row(parent="autocompleted"):
            dpg.add_button(label=matches[i], user_data=matches[i], callback=show_word_definitions)
            dpg.add_button(label=matches[-i-1], user_data=matches[-i-1], callback=show_word_definitions)



def show_word_definitions(sender, app_data, word):
    """

    Args:

      sender unused
      app_data unused
      word string

    Returns:
      
      None

    1. A new window is created that displays the definitions
    of the word.

    2. Newly searched word is added to _CONTEXT data store.
    The recently searched window is updated with the state change.

    """

    # 1. 
    with dpg.window(
        label=word,
        width=500, height=500,
    ):

        for definition in _CONTEXT.DEFINITIONS[word]:
            dpg.add_text(definition, wrap=400)

    # 2. 
    _CONTEXT.add_new_searched(word)

    update_recently_searched()

def update_recently_searched():
    """

    Updates the recently searched table to match the new
    data state.

    """
    clear_table("rs_table")

    for word in _CONTEXT.get_recently_searched():
        with dpg.table_row(parent="rs_table"):
            dpg.add_button(label=word, user_data=word, callback=show_word_definitions)

if __name__ == "__main__":

    _CONTEXT = CONTEXT(fpath="dictionary.json")
    main()

