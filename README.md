# grafcli

[![Build Status](https://travis-ci.org/m110/grafcli.svg?branch=master)](https://travis-ci.org/m110/grafcli)

[Grafana](http://grafana.org) CLI for fast and easy dashboards management.

**Please note** that grafcli has been tested for a while, but it still can have some minor defects. All help by contributions and suggestions is welcomed! Remember to back up your dashboards first.

Also note that grafcli was created when grafana itself lacked some features, like exports or API. Although it's still nice to have some of those in form of a CLI application.

Credit goes to [b3niup](https://github.com/b3niup) for the original idea!

## Featuring:

* Dashboards backup and restore.
* Easy rows and panels moving/copying between dashboards.
* Editing dashboards/rows/panels in-place.
* Templates of dashboards, rows and panels.
* File export/import.
* Interactive CLI with completions support.
* Compatibility across older Grafana versions.
* ...and more!

## Why?

* Lets you easily manage your dashboards using just your keyboard.
* Provides convenient way to backup dashboards and restore them.
* Can be used by any shell script with even more logic added.

## How?

Grafcli connects to Grafana HTTP API or directly to one of the backends (Elastic, SQLite, MySQL, PostgreSQL) and modifies the dashboards. This is all hidden behind an interface you already know well, similar to *nix filesystem.

## Requirements

* [Python 3](http://python.org)
* [climb](https://github.com/m110/climb)
* [pygments](http://pygments.org/)
* Depending on which storage backends you use, you need to install as well:
    * [requests](http://docs.python-requests.org/en/master/)
        * `pip install requests`
    * [elasticsearch-py](http://github.com/elastic/elasticsearch-py)
        * `pip install elasticsearch`
    * [psycopg2](http://initd.org/psycopg/)
        * `pip install psycopg2`
    * [MySQL Connector/Python](http://dev.mysql.com/downloads/connector/python/)
        * `pip install mysql-connector-python-rf`

## Installation

```
pip3 install grafcli
```

or get the source and run:

```
python3 setup.py install
```

Then define your hosts in the config file (see below for details).
```
cp /etc/grafcli/grafcli.conf.example /etc/grafcli/grafcli.conf
```

You will need at least one of the backend libraries listed above (except sqlite3, which comes with Python).

## TODO

* Improve confirmation prompt.
* Improve completions.
* Implement asterisk (*) handling.

# Usage

## Navigation

Use `cd` and `ls` commands to list nodes and move around.

```
[/]> cd templates
[/templates]> ls
dashboards
rows
panels
[/templates]> ls dashboards
example_dashboard
another_dashboard
[/templates]> ls dashboards/example_dashboard
1-Example-Row
2-Another-Row
3-Yet-Another-Row
[/templates]> ls dashboards/example_dashboard/1-Example-Row
1-Example-Panel
2-Another-Panel
```

## Directories

In the root directory, you will find three basic directories:

* `backups` - for storing backups of your dashboards (surprised?).
* `remote` - which lets you access remote hosts.
* `templates` - that contains templates of dashboards, rows and panels.

## Management

Most of the arguments here are paths to a dashboard, row or panel.

* `cat <path>` - display JSON of given element.
* `$EDITOR <path>` - edit the JSON of given element in-place and update it afterwards. Editor name can be set in the config file.
* `cp <source> <destination>` - copies one element to another. Can be used to copy whole dashboards, rows or single panels.
* `mv <source> <destination>` - the same as `cp`, but moves (renames) the source.
* `rm <path>` - removes the element.
* `template <path>` - saves element as template.
* `backup <remote_host> <system_path>` - saves backup of all dashboards from remote host as .tgz archive.
* `restore <system_path> <remote_host>` - restores saved backup.
* `export <path> <system_path>` - saves the JSON-encoded element to file.
* `import <system_path> <path>` - loads the JSON-encoded element from file.
* `pos <path> <index>` - change position of row in a dashboard or panel in a row.

# Configuration

Grafcli will attempt to read `./grafcli.conf`, `~/.grafcli.conf` and `/etc/grafcli/grafcli.conf` in that order.

Here is the configuration file explained.
```ini
[grafcli]
# Your favorite editor - this name will act as a command!
editor = vim
# Commands history file. Leave empty to disable.
history = ~/.grafcli_history
# Additional verbosity, if needed.
verbose = off
# Answer 'yes' to all overwrite prompts.
force = on

[resources]
# Directory where all local data will be stored (including backups).
data-dir = ~/.grafcli

# List of remote Grafana hosts.
# The key names do not matter, as long as matching section exists.
# Set the value to off to disable the host.
[hosts]
host.example.com = on

[host.example.com]
type = elastic
# In case of more hosts, use comma-separated values.
hosts = host1.example.com,host2.example.com
port = 9200
index = grafana-dash
ssl = off
# HTTP user and password, if any.
user =
password =
```

You can use other backends as well.

HTTP API:
```ini
[api.example.com]
type = api
url = http://localhost:3000/api
# Use either user and password or just the token
user =
password =
token =
```

MySQL:
```ini
[mysql.example.com]
type = mysql
host = mysql.example.com
port = 3306
user = grafana
password =
database = grafana
```

PostgreSQL:
```ini
[postgresql.example.com]
type = postgresql
host = postgresql.example.com
port = 5432
user = grafana
password =
database = grafana
```

SQLite:
```ini
[sqlite.example.com]
type = sqlite
path = /opt/grafana/data/grafana.db
```

# Tips

## Batch mode

Any command can be passed directly as arguments to grafcli, which will exit just after executing it. If you run it without arguments, you will get to interactive mode (preferable choice in most cases).

Batch mode:
```bash
$ grafcli ls remote
host.example.com
another.example.com
$ 
```

Interactive mode:
```bash
$ grafcli
[/]> ls remote
host.example.com
another.example.com
[/]> 
```

## Short names

All rows and panels names start with a number and it may seem that typing all that stuff gets boring soon. There are completions available (triggered by the `TAB` key) to help you with that.

It is enough to provide just the number of the row or panel. So instead of typing:
```
[/]> cp /templates/dashboards/dashboard/1-Top-Row/1-Top-Panel /remote/example/dashboard/1-Top-Row
```
You can just do:
```
[/]> cp /templates/dashboards/dashboard/1/1 /remote/example/dashboard/1
```

But then again, TAB-completions make it easy enough to type full names.

# Examples

Some of the common operations.

* Store dashboard as template (saved to `templates/dashboards/main_dashboard`):

```
[/]> template remote/example/main_dashboard
```

* Create the exact copy of dashboard's template:

```
[/templates/dashboards]> cp main_dashboard new_dashboard
```

* Update remote dashboard with local template:

```
[/]> cp templates/dashboards/new_dashboard remote/main_dashboard
```

* Move row from one dashboard to another (adds one more row to destination dashboard):

```
[/templates/dashboards]> cp main_dashboard/1-Top-Row new_dashboard
```

* Move row from one dashboard to another and replace existing row:

```
[/templates/dashboards]> cp main_dashboard/1-Top-Row new_dashboard/2-Some-Existing-Row
```

* Copy panel between rows (add one more panel to destination row).

```
[/templates/dashboards]> cp main_dashboard/1-Top-Row/1-Top-Panel new_dashboard/1-Top-Row
```

* Copy panel between rows and replace existing panel.

```
[/templates/dashboards]> cp main_dashboard/1-Top-Row/1-Top-Panel new_dashboard/1-Top-Row/2-Second-Panel
```

* Backup all dashboards.

```
[/] backup remote/example ~/backup.tgz
```

* Restore a backup.

```
[/] restore ~/backup.tgz remote/example
```

* Import dashboard from a file.

```
[/]> import ~/dashboard.json templates/dashboards/dashboard
```

* Export dashboard to a file.

```
[/]> export templates/dashboards/dashboard ~/dashboard.json
```
