# Web Scrapper

This folder contains the web scrapper tool we used to scrap Sam's musings
from his website.

The scrapper tool itself may be run directly using the command
> python ./scrapper.py
from that directory.

The scrapper tool itself only works on Sam's musing because the scrapper
has been made to crawl is particular web page format. If this format
changes in the near future, the script will have to be changes to
accommodate. To update to the most recently musings, simply run the script
again and it will overwrite all previous musings with all the musings from
his website in addition to the new ones.

To signal progress in this script, each and every musing presently being
scrapped will be printed to the terminal. If an error occurs, the last
musing that was printed indicates where the script failed.
