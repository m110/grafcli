# grafcli
Grafana CLI for fast and easy dashboards management.

**Note that this is still WIP and some of the features described here may be not implemented at the moment.**

## Featuring:

* Dashboards backup and restore.
* Easy rows and panels moving/copying between dashboards.
* Editing dashboards/rows/panels in-place.
* Interactive CLI with completions support.
* ...and more!

## Why?

To let you easily manage your dashboards using just your keyboard.

## How?

Grafcli connects directly to ElasticSearch and modifies dashboards' documents. However, this is all hidden behind an interface you already know well, similar to *nix filesystem.

## Requirements

* [Python 3](http://python.org)
* [elasticsearch-py](http://github.com/elastic/elasticsearch-py)

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

* `backups` - for storing backups of your dashboards (surprised?)
* `remote` - which lets you access remote hosts
* `templates` - that contains templates of dashboards, rows and panels.

## Management

Most of the arguments here are paths to a dashboard, row or panel.

* `cat <path>` - display JSON of given element.
* `$EDITOR <path>` - edit the JSON of given element in-place and update it afterwards.
* `cp <source> <destination>` - copies one element to another. Can be used to copy whole dashboards, rows or single panels.
* `mv <source> <destination>` - the same as `cp`, but moves (renames) the source.
* `rm <path>` - removes the element.
* `template <path> [name]` - saves element as template.
* `backup <remote_path>` - saves element as backup.
* `export <path> <system_path>` - saves the JSON-encoded element to file.
* `import <system_path> <path>` - loads the JSON-encoded element from file.

# Configuration

Grafcli will attempt to read `./grafcli.conf`, `~/.grafcli.conf` and `/etc/grafcli/grafcli.conf` in that order.

Here is the configuration file explained.
```ini
[grafcli]
# Commands history file. Leave empty to disable.
history = ~/.grafcli_history

[resources]
# Directory where all local data will be stored (including backups).
data-dir = ~/.grafcli

# List of remote ElasticSearch hosts.
# The key names do not matter, as long as matching section exists.
# Set the value to False to disable the host.
[hosts]
host.example.com = True

[host.example.com]
# In case of more hosts, use comma-separated values.
hosts = host1.example.com,host2.example.com
port = 9200
index = grafana-dash
# HTTP user and password, if any.
user =
password =
```

# Tips

## Batch mode

Any command can be passed directly as arguments to grafcli, which will exit just after after executing it. If you run it without arguments, you will get to interactive mode (preferable choice in most cases).

For example:
```bash
$ grafcli ls /remote
host.example.com
another.example.com
```

## Short names

All rows and panels names start with a number and it may seem that typing all that stuff gets boring soon. However, there are completions available (triggered by `TAB` key) to help you with that. What is more, it is enough to provide just the number of the row or panel, so take advantage of that!

So instead of typing:
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
[/]> get remote/example/main_dashboard
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
