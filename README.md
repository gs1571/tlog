Time Logger
===========

The idea of the script is to copy time entries from service toggl.com to Jira. The script can check that some time entries have already uploaded to Jira.

The script wrote on Python 3.

You will need to install python libraries which are mentioned in [requirements.txt] to be able to use this.

Installation on linux/mac
-------------------------

If you are using linux/mac, you most probably have Python already installed on your machine, but it can be 2.7 version.
Use your distro's package management system to install at least Python 3.6.

To download the script you also need to install git.

* Clone the repository
* Navigate to the repository's directory and install the required packages

```
cd tlog
pip install --user -r requirements.txt
```

Installation on Windows
-----------------------

* If you don't have Python installed, then you must install at least Python 3.6 from [here](https://www.python.org/downloads/windows/)
* If you don't have Git installed, then you must install from [here](https://git-scm.com/download/win)
* Open the Windows command shell
* In the command shell, run the following commands

```
git clone https://github.com/gs1571/tlog.git tlog
cd tlog
pip install --user -r requirements.txt
```

Configuration
-------------
* Copy `config.py-example` to `config.py`
* In `config.py`:
  - add your Toggl API token, which can be found in your Toggl Profile's settings. It should be looks like a string of hexadecimal symbols;
  - add username and password for Jira, the password can be an empty line, in that case, you will be asked to enter it when the script is run;
  - add Jira url;
  - configure the time period in days, it means how long in history from now the script will look.

Usage
-----

Before you start to use the script you need to work with toggl time tracker app. The script will try to get Jira ticket number and commentary for each entry. The script takes first match in the description which is task number (capital letters plus dash plus number), all remaining part except symbol ']' and spaces will be commentary.

Examples:
* [ABC-54321] my comment
* XYZ-12345 my comment 2
* [ABC-54321]
* ABC-54321
* https://example.com/browse/XYZ-12345 my comment
* https://example.com/browse/ABC-54321

The script looks at toggl time entries, finds suitable, check worklogs for relative tickets in ServiceDesk, and add them.

The scripts tried to avoid duplication, for that reason, each worklog entry in ServiceDesk will have toggl.com ID. The script adds it to the commentary field in a format like `[TOGGL_ID:123456789]`.

To use the script in **dry-run** mode run the following command:

```
python run.py
```

To use the script in **write** mode run the following command:

```
python run.py -w
```
> If you use Linux or Mac possible you need to run `python3` instead of `python` since `python` will run Python 2.x version interpretator.

Links
-----
* Toggl API - https://github.com/toggl/toggl_api_docs
* Toggl API library example - https://github.com/mos3abof/toggl_target
* Jira API -https://docs.atlassian.com/software/jira/docs/api/REST/8.7.1/
