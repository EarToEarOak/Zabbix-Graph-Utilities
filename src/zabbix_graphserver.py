#! /usr/bin/env python

#
# Zabbix Graph Utilities
#
# http://eartoearoak.com
#
# Copyright 2013 Al Brown
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

from PIL import Image
from cgi import parse_qs, escape
from zabbix_graph import Graph
from wsgiref.simple_server import make_server
from zabbix_lib import Zabbix_Json, Zabbix_Error
import StringIO
import argparse
import datetime
import socket
import sys

api = None


def graph_server(environ, start_response):

    start = datetime.datetime.now()

    content = ('Content-Type', 'text/plain')
    remote = environ['REMOTE_HOST']

    __query = parse_qs(environ['QUERY_STRING'])
    try:
        id_graph = int(escape(__query.get('graph', ['-1'])[0]))
    except ValueError:
        id_graph = -1
    try:
        width = float(escape(__query.get('width', ['8'])[0]))
    except ValueError:
        width = 8
    try:
        height = float(escape(__query.get('height', ['5'])[0]))
    except ValueError:
        height = 5
    try:
        scale = float(escape(__query.get('scale', ['1'])[0]))
    except ValueError:
        scale = 1

    show_grid = escape(__query.get('grid', [''])[0]) == 'true'
    show_legend = escape(__query.get('legend', [''])[0]) == 'true'
    invert = escape(__query.get('invert', [''])[0]) == 'true'

    if id_graph == -1:
        body = 'Graph not specified'
    else:
        try:
            api.login()
            title = api.get_graph_title(id_graph)
            if title is None:
                body = 'Graph not found'
                api.logout()
            else:
                print 'Generating graph \'{0}\' for {1}'.format(title, remote)
                content = ('Content-Type', 'image/png')
                graph = Graph()
                api.get_graph(graph, title, id_graph)
                figure = graph.plot_mpl(width, height, invert, show_grid,
                                        show_legend)
                figure.canvas.draw()
                graph.close(figure)
                image_buffer = StringIO.StringIO()
                size = figure.canvas.get_width_height()
                image = Image.fromstring('RGB', size,
                                         figure.canvas.tostring_rgb())
                if scale != 1:
                    scale_size = (int(size[0] * scale), int(size[1] * scale))
                    image = image.resize(scale_size, Image.ANTIALIAS)
                image.save(image_buffer, 'PNG')
                body = image_buffer.getvalue()
                api.logout()
                duration = datetime.datetime.now() - start
                print 'Completed in {0}ms'.format(duration.microseconds / 1000)
        except Zabbix_Error:
            body = 'Zabbix Error'

    headers = [content, ('Content-Length', str(len(body)))]
    start_response('200 OK', headers)
    return [body]


def main(argv=None):

    global api

    print 'zabbix_graphserver\n'

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    try:
        parser = argparse.ArgumentParser(description='Serve Zabbix graphs')
        parser.add_argument('url', type=str, help='Zabbix JSON URL')
        parser.add_argument('-u', type=str, default='guest', metavar='User',
                            help='User')
        parser.add_argument('-p', type=str, default='', metavar='Password',
                            help='Password')
        parser.add_argument('-t', type=int, default=8051, help='Port')

        args = parser.parse_args()
        url = args.url
        user = args.u
        password = args.p
        port = args.t

        api = Zabbix_Json(url, user, password)

        try:
            httpd = make_server('0.0.0.0', port, graph_server)
            httpd.serve_forever()
        except socket.error, error:
            sys.stderr.write(error.strerror + "\n")
            return 1

        return 0
    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit(main())
