#! /usr/bin/env python

#
# Zabbix Graph Utilities
#
# http://eartoearoak.com
#
# Copyright 2013 - 2014 Al Brown
#
# Utilities to display graphs from a Zabbix server using matplotlib.
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from zabbix_graph import Graph
from zabbix_lib import Zabbix_Json, Zabbix_Error
import argparse
import pylab
import sys


def main(argv=None):

    print 'zabbix_getgraph\n'

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    try:
        parser = argparse.ArgumentParser(description='Get Zabbix graphs')
        parser.add_argument('url', type=str, help='Zabbix JSON URL')
        parser.add_argument('graph_id', type=int, help='Graph ID')
        parser.add_argument('-u', type=str, default='guest', metavar='User',
                            help='User')
        parser.add_argument('-p', type=str, default='', metavar='Password',
                            help='Password')
        parser.add_argument('-o', type=str, default='graph.png',
                            help='Output image')
        parser.add_argument('-x', type=int, default=8, help='Image width)')
        parser.add_argument('-y', type=int, default=5, help='Image height)')
        parser.add_argument('-g', action="store_true", help='Show grid)')
        parser.add_argument('-l', action="store_true", help='Show legend)')
        parser.add_argument('-b', action="store_true",
                            help='Invert backround)')
        parser.add_argument('-w', action="store_true",
                            help='Show image in window')

        args = parser.parse_args()
        url = args.url
        user = args.u
        password = args.p
        id_graph = args.graph_id
        filename = args.o
        width = args.x
        height = args.y
        show_grid = args.g
        show_legend = args.l
        invert = args.b
        show_window = args.w

        api = Zabbix_Json(url, user, password)
        try:
            api.login()
            title = api.get_graph_title(id_graph)
            if title is None:
                sys.stderr.write('Graph not found\n')
                return 1
            if show_window:
                print 'Generating graph \'{0}\''.format(title)
            else:
                print 'Generating graph \'{0}\' as {1}'.format(title, filename)

            graph = Graph()
            api.get_graph(graph, title, id_graph)
            api.logout()
            figure = graph.plot_mpl(width, height, invert, show_grid,
                                      show_legend)
            if show_window:
                pylab.show()
            else:
                try:
                    figure.savefig(filename)
                except ValueError, error:
                    sys.stderr.write(error.message + "\n")
                    return 1

            print 'Completed'
            return 0

        except Zabbix_Error:
            return 2

    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit(main())
