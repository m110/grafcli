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

Grafcli connects directly to ElasticSearch and modifies dashboard's documents. However, this is all hidden behind an interface you already know well, similar to *nix filesystem.

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
* `get <path>` - saved backup of given element.

# Examples

Some of the common operations.

```
To be added
```
