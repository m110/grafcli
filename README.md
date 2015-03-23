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

# Usage

Note that any command can be passed directly as arguments to grafcli, which will exit just after after executing it. If you run it without arguments, you will get to interactive mode (preferable choice in most cases).

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
* `rm <source> <destination>` - removes the element
* `get <path>` - saves backup of given element.

# Configuration

Graftcli will attempt to read `./grafcli.conf`, `~/.grafcli.conf` and `/etc/grafcli/grafcli.conf` in that order.

Here is the configuration file exmplained.
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

# Examples

Some of the common operations.

```
To be added
```
