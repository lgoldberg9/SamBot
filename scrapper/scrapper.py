# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 15:33:31 2018

@author: logan
"""

from lxml import html
import requests

body_regex = '//div[@class="col-md-12"]'

# Get all a refs from Sam's index page
index_page = requests.get('https://www.cs.grinnell.edu/~rebelsky/musings/index-by-number')
index_tree = html.fromstring(index_page.content)
hrefs = [href.attrib['href'] for href in index_tree.xpath('//a')[33:-5]]

for href in hrefs:
    # Automate this request getting
    if href[0:4] != 'http':
        page = requests.get('https://www.cs.grinnell.edu/~rebelsky/musings/' + href)
        name = href
    else:
        page = requests.get(href)
        name = href[-8:]
    tree = html.fromstring(page.content)
    
    try:
        # Get the body of the text, namely first element
        print href
        text_body = tree.xpath(body_regex)[0].text_content()
            
        # Split body according to newlines and drop all empty instances
        text_body_split = text_body.split('\n')
        text_body_filtered = filter(None, text_body_split)
        
        # Drop title and footer information
        text_body_pure = text_body_filtered[1:-2]
        
        # Rejoin all the strings into one body and encode using ascii
        final_text_body = ' '.join(text_body_pure).encode('ascii', 'ignore')
        
        f = open('./sam_musings/' + name, 'w')
        f.write(final_text_body)
        f.close()
    except IndexError:
        # Can't find the webpage or some other error
        pass
    