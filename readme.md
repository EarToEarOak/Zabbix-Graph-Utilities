# Zabbix Graph Utilities#

Copyright 2012, 2013 Al Brown

al [at] eartoearoak.com

Utilities to display graphs from a [Zabbix](http://www.zabbix.com/) server using matplotlib.

Tested on Windows 7 x64 and Ubuntu 12.04 x64 with Zabbix 2.0

## Requirements ##

- [Python 2.6](http://www.python.org) or greater
- [matplotlib](http://matplotlib.org/)
- [numpy](http://www.numpy.org/)

## Basic Usage ##

**zabbix_graphget.py - View or save a graph**

	zabbix_graphget.py url graph_id [-u User] [-p Password] [-o filename]

	url 		- zabbix server url
	graph_id	- graph id
	-u			- zabbix user
	-p			- zabbix password
	-o			- image filename
	-x			- image width
	-y			- image height
	-g			- show grid
	-l			- show legend
	-b			- invert graph background
	-w			- show graph in window
	
	

For example:

`zabbix_graphget.py -u query -p letmein -g -l -b -w http://myserver/zabbix 1248`

**zabbix_graphserver.py - Serve graph images over HTTP**

	zabbix_graphserver.py  url [-u User] [-p password] [-t port]

	url	- zabbix server url
	-u	- zabbix user
	-p	- zabbix password
	-t	- listen port

For example:

`zabbix_graphserver.py -u query -p letmein http://myserver/zabbix`

Requests can then be made as:

	http://<server>:<port>/?graph=<graph_id>[&width=<integer>][&height=<integer>][&scale=<float>][&grid=<boolean>][&legend=<boolean>][&invert=<boolean>]

	graph	- graph id
	width	- graph width
	height	- graph height
	scale	- scale graph by factor
	grid	- show grid
	legend	- show legend
	invert	- invert graph background

	Boolean values are 'true' or 'false', if omitted they are assumed to be false
	

For example:
`http://myserver:8051/?graph=1248&invert=true&legend=false&width=5&height=9&scale=0.4`

If you are running this in a headless environment please uncomment lines 29 & 30 in zabbix_graph.py

##Zabbix Permissions##

A zabbix user with read-only permissions to the group containing the graph is needed.

Ideally create a new user and add it to a group with permission to read the necessary host groups and disable front end access.

## License ##

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
