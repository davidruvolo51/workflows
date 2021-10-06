
import pandas as pd
import requests
import re
from datetime import datetime
# import calplot
# import matplotlib.pyplot as plt

# Get CRAN Stats
# Get download stats from CRAN from http://cranlogs.r-pkg.org
class getCranStats:
    def __init__(self):
        """Get CRAN Status

        @examples

        from cran_status import getCranStats
        c = getCranStats()
        c.dailyDownloads('<package_name>', '2021-01-01', '2021-02-01')
        """
        self.host = 'https://cranlogs.r-pkg.org'
        self.endpoint = 'downloads/daily'
        self.headers = {
            'Content-Type': 'application/json'
        }

    def __validate__date__(self, date):
        if not re.fullmatch(r'([0-9]{4}(-[0-9]{2}){2})', date):
            raise ValueError(
                'Error in date {}: must be in `yyyy-mm-dd` format'
                .format(date)
            )


    def dailyDownloads(
        self,
        package: list = None,
        start: str = None,
        end: str = None
    ):
        """Get Daily Downloads
        Get CRAN daily download stats for one or more packages

        @param package (list) : a list of CRAN package names
        @param start   (str)  : a date string, yyyy-mm-dd
        @param end     (str)  : a date string, yyyy-mm-dd

        @return list
        """
        self.__validate__date__(start)
        self.__validate__date__(end)
        
        url = '{}/{}/{}:{}/{}'.format(
            self.host,
            self.endpoint,
            start,
            end,
            package
        )

        try:
            response = requests.get(url = url, headers = self.headers)
            return response.json()
        except requests.exceptions.HTTPError as err:
            raise SystemError(err)


#//////////////////////////////////////

# Download Data for `rheroicons`
c = getCranStats()

start = '2021-02-26' # date accepted
end = str(datetime.now().date()) # today's date

raw = c.dailyDownloads('rheroicons', start, end)[0]['downloads']
downloads = pd.DataFrame(raw)

# save data
downloads.to_csv('data/rheroicons_daily_downloads.csv', index=False)

# build plot
# downloads['day'] = pd.to_datetime(downloads.day, yearfirst = True)
# downloads.set_index('day', inplace = True)
# fig = calplot.calplot(downloads['downloads'], how = 'sum')

# plt.show()