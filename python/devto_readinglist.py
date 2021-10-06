#'////////////////////////////////////////////////////////////////////////////
#' FILE: devto_readinglist.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-02
#' MODIFIED: 2021-10-02
#' PURPOSE: fetch readinglist from https://dev.to
#' STATUS: in.progress
#' PACKAGES: requests
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import requests
import pandas as pd
from os import getenv
from re import sub

class DevTo:
    def __init__(self, token: str = None):
        self.host = 'https://dev.to/api/'
        self.readinglist = []
        self.headers = {
            'Content-Type': 'application/json',
            'api-key': str(token)
        }
        
    
    def __send__request__(self, url: str = None):
        """Wrapper for Get
        """
        try:
            resp = requests.get(url = url, headers = self.headers)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise SystemError(error)   

        return resp.json()
        

    def getReadingList(self):
        """Get Reading List
        
        Retrieve user reading list
        
        @references
            https://developers.forem.com/api#operation/getReadinglist
        
        """
        if not self.readinglist:
            data = self.__send__request__(url = self.host + 'readinglist')
            for d in data:
                
                # process and format article description
                desc = d.get('article', {}).get('description', None)
                if desc:
                    desc = sub(r'(\s+)', ' ', desc)
                    desc = sub(r'(Enter fullscreen mode)|(Exit fullscreen mode...)', '', desc)
                    
                # extract attributes of interest
                self.readinglist.append({
                    'id': d.get('id'),
                    'published_at': d.get('article',{}).get('published_at'),
                    'title': d.get('article').get('title'),
                    'description': desc,
                    'canonical_url': d.get('article', {}).get('canonical_url'),
                    'tags': d.get('article', {}).get('tags'),
                    'reading_time_minutes': d.get('article', {}).get('reading_time_minutes'),
                    'username': d.get('article', {}).get('user', {}).get('username')
                })

#//////////////////////////////////////////////////////////////////////////////
            
# Fetch readinglist
devto = DevTo(token = getenv('devto_token'))
devto.getReadingList()

# write to csv
posts = pd.DataFrame(devto.readinglist)
posts.to_csv('data/devto_readinglist.csv', index=False)
