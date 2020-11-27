# tlog - Moving time entries from toggl.com to jira
# Written in 2020 by Grigory Solovyev gs1571@gmail.com
#
# To the extent possible under law, the author(s) have dedicated all copyright 
# and related and neighboring rights to this software to the public domain worldwide. 
# This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. 
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

from datetime import datetime, timedelta, date
from pprint import pprint
from getpass import getpass
from progress.bar import Bar 
from validator_collection import checkers
from togglapi import togglapi
from jiraapi import jiraapi
from worklog import worklog
import logging, sys, re, os, random, argparse
import config

os.system("")

class style():
  BLACK = '\033[30m'
  RED = '\033[31m'
  GREEN = '\033[32m'
  YELLOW = '\033[33m'
  BLUE = '\033[34m'
  MAGENTA = '\033[35m'
  CYAN = '\033[36m'
  WHITE = '\033[37m'
  UNDERLINE = '\033[4m'
  RESET = '\033[0m'

def validation_config():

  if not re.match(r'^[0-9a-fA-F]*$', config.API_TOKEN):
    print(f"Check the token, we got '{config.API_TOKEN}', but it seems not token string")
    sys.exit()

  if not checkers.is_url(config.JIRA_URL):
    print(f"Check the Jira url, we got '{config.JIRA_URL}', but it seems not url string")
    sys.exit()

  if not type(config.DAYS_AGO) == int:
    print(f"Check the days ago, we got '{config.DAYS_AGO}', expect integer number")
    sys.exit()

  return True

def main():

  # Definition some parameters:
  ## Time format
  tfmt = "%d-%m-%Y %H:%M"

  # Parse CLI arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('-w', 
                    action='store_true', 
                    default=False,
                    dest='write_result',
                    help='write missed worklogs to jira, by default jira will not updates')
  args = parser.parse_args()

  print(style.CYAN + 'Config validation...' + style.RESET)
  validation_config()

  if not config.JIRA_PASSWORD:
    print(style.CYAN + 'JIRA password is not defined, please enter the password' + style.RESET)
    config.JIRA_PASSWORD = getpass()
    
  ja = jiraapi.JiraAPI(config.JIRA_USERNAME, config.JIRA_PASSWORD, config.JIRA_URL + 'rest/api/2/')

  print(style.CYAN + 'Jira Access checking...' + style.RESET)
  ja.check()

  ta = togglapi.TogglAPI(config.API_TOKEN, '+00:00')

  # Getting time
  end_date = datetime.now()
  start_date = datetime.now() + timedelta(days=-config.DAYS_AGO)

  # Getting data from toggl
  print(style.CYAN + 'Getting data from toggl.com...' + style.RESET)
  time_entries = ta.get_time_entries(start_date.isoformat(), end_date.isoformat())

  print(style.CYAN + 'List of founded Toggl time entries:' + style.RESET)
  print(style.MAGENTA + f'From: {date.strftime(start_date, tfmt)}' + style.RESET)
  print(style.MAGENTA + f'  To: {date.strftime(end_date, tfmt)}' + style.RESET)

  # Filtering correct worklogs from toggl entries
  actual_worklogs = []
  for wl in time_entries:

    wl_entry = worklog.Worklog(wl['start'], wl['duration'], wl['description'], wl['id'])

    if int(wl['duration']) < 0:
      print(style.YELLOW + f"ID: {wl_entry.toggl_id}, Started: {date.strftime(wl_entry.started.astimezone(), tfmt)}, Original description: \'{wl['description']}\' - TASK STILL IN PROGRESS" + style.RESET)
      continue

    if not wl_entry.task:
      print(style.RED + f"ID: {wl_entry.toggl_id}, Started: {date.strftime(wl_entry.started.astimezone(), tfmt)}, Time spent: {str(timedelta(seconds=wl_entry.timespent))}, Original description: \'{wl['description']}\' - FAIL TO GET TASK ID" + style.RESET)
      continue
    else:
      print(style.GREEN + f"ID: {wl_entry.toggl_id}, Started: {date.strftime(wl_entry.started.astimezone(), tfmt)}, Time spent: {str(timedelta(seconds=wl_entry.timespent))}, Original description: \'{wl['description']}\' - OK" + style.RESET)
    
    actual_worklogs.append(wl_entry)

  if not actual_worklogs:
    print(style.CYAN + 'Nothing found!' + style.RESET)
    sys.exit()

  print(style.CYAN + 'Checking missed time entries...' + style.RESET)

  # Get list of tasks rwithout duplicates
  tasks = list(set(wl.task for wl in actual_worklogs))

  # Sorting toggl worklogs by task name, we get a dictionary where key is task and value is list of wroklogs
  wl_list_full = {}
  for task in tasks:
    task_list = [wl for wl in actual_worklogs if wl.task == task]
    wl_list_full[task] = task_list

  # Extract comments from Jira for each of task, we get dictionary where key is task and value is list of toogle id
  # if in comments toogl id is not found it will not be in the list
  jira_comments = {task: ja.get_worklog_toggle_id(task) for task in tasks}

  # Finding toogle worklogs which have not been added yet by comparing toggl id of toggl's worklogs and toggl_id in comments
  missed_wl = []
  for task in tasks:
    list_of_wls = [wl for wl in wl_list_full[task] if wl.toggl_id not in jira_comments[task]]

    missed_wl += list_of_wls

  if not missed_wl:
    print(style.CYAN + 'Nothing for updating!' + style.RESET)
    sys.exit()

  print(style.CYAN + 'List of missed time entries:' + style.RESET)
  for wl in missed_wl:
    print(style.GREEN + f"Task: {wl.task}, Toggle ID: {wl.toggl_id}, Started: {date.strftime(wl.started.astimezone(), tfmt)}, Time spent: {str(timedelta(seconds=wl.timespent))}, Description: {wl.comment}" + style.RESET)
  
  # Write missed worklogs to Jira
  if args.write_result:
    print(style.CYAN + 'Adding missed time entries to Jira...' + style.RESET)
    with Bar(max=len(missed_wl)) as bar:
      for wl in missed_wl:
        ja.put_worklog(wl)
        bar.next()
    print(style.CYAN + 'Done' + style.RESET)
  else:
    print(style.YELLOW + 'WARNING! The missed time entries did not added to Jira, because you did not add parameter -w to update Jira!' + style.RESET)

if __name__ == '__main__':
    main()