# Some URLs are the same, and they also have the same data but the formatting of the data is done differently. 
# And due to that, they are treated as separate pages. Below is the code to verify the same. The URLs taken have been 
# obtained from the previously generated log files.
from urllib.parse import unquote




def are_urls_equal(url1, url2):
    # Extract the page titles from the URLs
    page_title1 = unquote(url1.split('/')[-1].replace('_', ' '))
    page_title2 = unquote(url2.split('/')[-1].replace('%3A', ':'))

    # Compare the page titles
    return page_title1 == page_title2

# url1 = "https://ab.wikipedia.org/wiki/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0"
# url2 = "https://ab.wikipedia.org/wiki/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0"

url1 = 'https://bdp.ft.com/'
url2 = 'https://bdp.ft.com/'

if are_urls_equal(url1, url2):
    print("The only difference is in the formatting of the page title.")
else:
    print("There are other differences between the URLs.")
