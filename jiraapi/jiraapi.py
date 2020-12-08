# tlog - Moving time entries from toggl.com to jira
# Written in 2020 by Grigory Solovyev gs1571@gmail.com
#
# To the extent possible under law, the author(s) have dedicated all copyright 
# and related and neighboring rights to this software to the public domain worldwide. 
# This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. 
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

import requests, math, re
from pprint import pprint

class JiraAPI():
  """
  The class process requests to Jira
  """

  def __init__(self, username, password, url):
    self.username = username
    self.password = password
    self.url = url

  def check(self):
    """
    Request information about myself to be sure that the script can get access to Jira
    """
    response = requests.get(
      self.url + 'myself', 
      auth=requests.auth.HTTPBasicAuth(self.username, self.password)
    )
    if response.status_code == 200:
      return response.status_code
    else:
      print('Error Message: {}'.format(response.content))
      raise NameError(f'Code of error {response.status_code} and text {response.text}.')

  def get_worklog_entries(self, task):
    """
    Getting worklogs entries of the task
    """
    data = []
    response = requests.get(
      self.url + f'issue/{task}/worklog', 
      auth=requests.auth.HTTPBasicAuth(self.username, self.password)
    )
    if response.status_code == 200:
      pass
    elif response.status_code == 404:
      print('Error Message: {}'.format(response.content))
      raise NameError(f'Task {task} not found!')
    else:
      print('Error Message: {}'.format(response.content))
      raise NameError(f'Code of error {response.status_code} and text {response.text}.')
    
    json = response.json()

    # Pagination processing
    max_results = int(json['maxResults'])
    total = int(json['total'])

    if max_results == total:
      data += json['worklogs']
    else:
      data += json['worklogs']
      for page in range(2, math.ceil(total/max_results) + 1):
        response = requests.get(
          self.url + f'issue/{task}/worklog', 
          patams={"startAt": page * max_results}, 
          auth=requests.auth.HTTPBasicAuth(self.username, self.password)
        )
        data += json['worklogs']
      
    return data

  @staticmethod
  def get_id_from_comment(comment):
    """
    Searching special text in comments to get toggl id. It help us to avoid duplication of worklog entries
    """
    result_id_line = re.search(r'\[TOGGL_ID\:\d*\]', comment)
    if result_id_line:
      return int(result_id_line.group()[10:-1])
    else:
      False

  def get_worklog_toggle_id(self, ticket):
    """
    Getting toggl id if it exists
    """

    list_of_worklogs = self.get_worklog_entries(ticket)
    comments = [
      self.get_id_from_comment(entry['comment']) for entry in list_of_worklogs if self.get_id_from_comment(entry['comment'])
    ]

    return comments

  def put_worklog(self, worklog):
    """
    Putting worklog entriy
    """
    response = requests.post(
      self.url + f'issue/{worklog.task}/worklog', 
      auth=requests.auth.HTTPBasicAuth(self.username, self.password), 
      json=worklog.to_jira()
    )
    if response.status_code == 201:
      return True
    elif response.status_code == 400:
      print('Error Message: {}'.format(response.content))
      raise NameError(f'The input is invalid (e.g. missing required fields, invalid values, and so forth). Worklog: {worklog}')
    elif response.status_code == 403:
      print('Error Message: {}'.format(response.content))
      raise NameError(f'The calling user does not have permission to add the worklog. Worklog: {worklog}')
    else:
      raise NameError(f'Code of error {response.status_code} and text {response.text}. Worklog: {worklog}')
