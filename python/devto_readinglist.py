#'////////////////////////////////////////////////////////////////////////////
#' FILE: devto_readinglist.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-02
#' MODIFIED: 2021-10-23
#' PURPOSE: fetch readinglist from https://dev.to
#' STATUS: working
#' PACKAGES: requests
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import requests
import pandas as pd
from os import environ
from time import sleep
from re import sub

class DevTo:
    def __init__(self, token: str = None):
        self.host = 'https://dev.to/api/'
        self.headers = {
            'Content-Type': 'application/json',
            'api-key': str(token)
        }
        
    
    def __send__request__(self, url: str = None):
        """Wrapper for Get request
        """
        try:
            resp = requests.get(url = url, headers = self.headers)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise SystemError(error)   

        return resp.json()

    def __extract__data__(self, data: dict):
        """Extract Reading List entry
        Pull content from readlist entry
        """
        # process and format article description
        desc = data.get('article', {}).get('description', None)
        if desc:
            desc = sub(r'(\s+)', ' ', desc)
            desc = sub(r'(Enter fullscreen mode)|(Exit fullscreen mode...)', '', desc)
            
        # extract attributes of interest
        return {
            'id': data.get('id'),
            'published_at': data.get('article',{}).get('published_at'),
            'title': data.get('article').get('title'),
            'description': desc,
            'canonical_url': data.get('article', {}).get('canonical_url'),
            'tags': data.get('article', {}).get('tags'),
            'reading_time_minutes': data.get('article', {}).get('reading_time_minutes'),
            'username': data.get('article', {}).get('user', {}).get('username')
        }

    def getReadingList(self, page: int = 1, per_page: int = 100):
        """Get Reading List
        
        Retrieve user reading list
        
        Attributes
            
                page (int) : pagination page (default: max 100)
            per_page (int) : the number of items per page
        
        @references
            https://developers.forem.com/api#operation/getReadinglist
        
        """
        if page < 1:
            raise ValueError('Error in getReadingList: page must be greater than 1')

        if per_page < 1 or per_page > 100:
            raise ValueError('Error in getReadingList: per_page must be between 1:100')
        
        url = f'{self.host}readinglist?page={str(page)}&per_page={str(per_page)}'
        
        readinglist = []
        data = self.__send__request__(url)
        for d in data:
            readinglist.append(self.__extract__data__(data = d))
        
        return readinglist
                

#//////////////////////////////////////////////////////////////////////////////
            
# Fetch readinglist
print('Starting session...')
devto = DevTo(token = environ.get('DEVTO_TOKEN'))

# Get posts in batches
print('Pulling data...')
sendRequests = True
readinglist = []
ids = []
p = 1
while sendRequests:
    print(f'Getting batch {p}')
    data = devto.getReadingList(page = p, per_page = 100)
    for d in data:
        if not (d['id'] in ids):
            readinglist.append(d)
            ids.append(d['id'])
        else:
            sendRequests = False
    p += 1
    sleep(0.3)

# write to csv
print('Saving data to csv...')
posts = pd.DataFrame(readinglist).sort_values(by = 'published_at', key=pd.to_datetime, ascending = False)
posts.to_csv('data/devto_readinglist.csv', index=False)
