# tlog - Moving time entries from toggl.com to jira
# Written in 2020 by Grigory Solovyev gs1571@gmail.com
#
# To the extent possible under law, the author(s) have dedicated all copyright 
# and related and neighboring rights to this software to the public domain worldwide. 
# This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. 
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

import re
from datetime import datetime

class Worklog():
  """
  The class process worklog entries of Jira
  """

  def __init__(self, started, timespent, comment, toggl_id):
    self.started = datetime.fromisoformat(started)
    self.timespent = timespent
    self.task, self.comment = self.parse_comment(comment)
    self.toggl_id = toggl_id

  def __repr__(self):
    return f'WorkLog(toggl_id: {str(self.toggl_id)} task: {self.task})'

  @property
  def timespent(self):
    return self.__timespent

  @timespent.setter
  def timespent(self, time):
    """
    A worklog cannot be lower than 60 seconds
    """
    if time < 60:
      self.__timespent = 60
    else:
      self.__timespent = time

  @staticmethod
  def parse_comment(line):
    """
    Parsing comment line to extract:
    - ticket number as capital letters plus dash plus number, like ABC-12345
    - additional comment after ticket number

    The method return touple of two, first item is ticket number, seconbd item is description
    In case of absent ticket number both are None, in case of description absent second item is None

    Function return tuple of two items, first one is ticket number, second one is comment line

    >>> Worklog.parse_comment('[ABC-54321] my comment')
    ('ABC-54321', 'my comment')
    >>> Worklog.parse_comment('[XYZ-12345] my comment 2')
    ('XYZ-12345', 'my comment 2')
    >>> Worklog.parse_comment('[ABC-54321]')
    ('ABC-54321', None)
    >>> Worklog.parse_comment('my comment' )
    (None, None)
    >>> Worklog.parse_comment('https://servicedesk.luxoft.com/browse/XYZ-12345')
    ('XYZ-12345', None)
    >>> Worklog.parse_comment('https://servicedesk.luxoft.com/browse/XYZ-12345 comment')
    ('XYZ-12345', 'comment')
    >>> Worklog.parse_comment('ABC-54321')
    ('ABC-54321', None)
    >>> Worklog.parse_comment('ABC-54321 ABC-5555 [XYZ-12345]')
    ('ABC-54321', 'ABC-5555 [XYZ-12345]')
    >>> Worklog.parse_comment('XYZ-12345 my comment 2')
    ('XYZ-12345', 'my comment 2')
    >>> Worklog.parse_comment('')
    (None, None)
    >>> Worklog.parse_comment('XYZ_12345 comment')
    (None, None)
    >>> Worklog.parse_comment('GGG-12345 my comment 2')
    ('GGG-12345', 'my comment 2')
    """

    # try to find ticket number, it is first ticket number in string
    task_match = re.search(r'([A-Z]+)\-\d+', line)
    if task_match:
      task = task_match.group(0)
      # remove '[' and spaces on the beggining of remaining part of the line,
      # it will be description
      descr = re.sub(r'^(\]\s*|\s*)', "", line[task_match.end():])
      if descr == '':
        descr = None
      return (task, descr)
    else:
      return (None, None)

  def to_jira(self):
    """
    Prepage dictionary of Worklog in Jira format, it should be like this example:
    {
      'comment': 'text of commentary [TOGGL_ID:1702917845]',
      'started': '2020-09-23T08:00:47.000+0000',
      'timeSpentSeconds': 662
    }
    Be careful with timezone, isoformat of datetime library return with column, 
    but Jira supports only without column!
    """
    if self.comment:      
      return {
        'comment': f'{self.comment} [TOGGL_ID:{self.toggl_id}]',
        'started': self.started.isoformat(timespec='milliseconds').replace('+00:00', '+0000'),
        'timeSpentSeconds': self.timespent
      }
    else:
      return {
        'comment': f'[TOGGL_ID:{self.toggl_id}]',
        'started': self.started.isoformat(timespec='milliseconds').replace('+00:00', '+0000'),
        'timeSpentSeconds': self.timespent
      }


    