# tlog - Moving time entries from toggl.com to jira
# Written in 2020 by Grigory Solovyev gs1571@gmail.com
#
# To the extent possible under law, the author(s) have dedicated all copyright 
# and related and neighboring rights to this software to the public domain worldwide. 
# This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. 
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

import requests
from urllib.parse import urlencode

class TogglAPI():

  def __init__(self, api_token, timezone, url=None, headers=None):
    self.api_token = api_token
    self.timezone = timezone
    self.url = url or 'https://www.toggl.com/api/v8/'
    self.headers = {'content-type': 'application/json'}

  def get_time_entries(self, start_date, end_date):
    parameters = {
      'start_date': start_date + self.timezone,
      'end_date': end_date + self.timezone
    }
    response = requests.get(
      url = self.url + 'time_entries' + '?{}'.format(urlencode(parameters)),
      headers = self.headers,
      auth=requests.auth.HTTPBasicAuth(self.api_token, 'api_token')
    )
  
    return response.json()
    