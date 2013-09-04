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

import datetime
import json
import sys
import urllib2


class Zabbix_Error(Exception):

    def __init__(self, response):

        super(Zabbix_Error, self).__init__(response)

        error = response['error']
        sys.stderr.write('Error\n')
        sys.stderr.write('\tCode: ')
        sys.stderr.write(str(error['code']))
        sys.stderr.write('\n')
        sys.stderr.write('\tData: ')
        sys.stderr.write(error['data'])
        sys.stderr.write('\n')
        sys.stderr.write('\tMessage: ')
        sys.stderr.write(error['message'])
        sys.stderr.write('\n')


class Zabbix_Json():

    url = ''
    user = ''
    password = ''
    auth = ''
    id = 1

    limit = 24 * 60 * 60 / (60 / 15)  # 15s samples in 24 hours

    def __init__(self, url, user, password):

        self.url = url.rstrip('/')
        self.user = user
        self.password = password

    def __dt_to_string(self, dt):

        epoch = datetime.datetime.utcfromtimestamp(0)
        delta = dt - epoch
        return str(int(delta.total_seconds()))

    def __convert_graph(self, graph, item_map, styles, history):

        for name, item in item_map.iteritems():
            graph.plots[item['id']] = {'name': name,
                                       'colour': 0,
                                       'units': item['units'],
                                       'time': [],
                                       'value': []}
        for style in styles:
            graph.plots[style['itemid']]['colour'] = '#' + style['color']
            graph.plots[style['itemid']]['drawtype'] = '#' + style['drawtype']

        for item in history:
            graph.plots[item['itemid']]['time'].append((item['clock']))
            graph.plots[item['itemid']]['value'].append(float((item['value'])))

        return graph

    def __query(self, method, params={}):

        method_json = {
               'jsonrpc': '2.0',
               'method': method,
               'params': params,
               'auth': self.auth,
               'id': self.id}
        command = json.dumps(method_json)
        headers = {'Content-Type': 'application/json-rpc'}
        request = urllib2.Request(self.url + '/api_jsonrpc.php',
                                  command.encode('utf-8'), headers)
        urlopen = urllib2.urlopen(request)
        data = urlopen.read()
        urlopen.close()
        response = json.loads(data)
        self.id += 1

        return response

    def __get_graph_styles(self, item_map):

        ids = []

        for _name, item in item_map.iteritems():
            ids.append(item['id'])

        response = self.__query('graphitem.get', {'itemids': ids,
                                                'output': 'extend',
                                                'expandData': 1})
        try:
            styles = response['result']
        except KeyError:
            raise Zabbix_Error(response)

        return styles

    def __get_history(self, item_map):

        ids = []
        history = ''

        for _name, item in item_map.iteritems():
            ids.append(item['id'])

        time_to = datetime.datetime.utcnow()
        time_from = time_to - datetime.timedelta(days=1)

        response = self.__query('history.get',
                              {'itemids': ids,
                               'history': 0,
                               'output': 'extend',
                               'sortfield': 'clock',
                               'time_from': self.__dt_to_string(time_from),
                               'time_till': self.__dt_to_string(time_to),
                               'limit': self.limit})
        try:
            history = response['result']
        except KeyError:
            raise Zabbix_Error(response)

        return history

    def login(self):

        response = self.__query('user.authenticate', {'user': self.user,
                                                  'password': self.password})

        try:
            self.auth = response['result']
        except KeyError:
            raise Zabbix_Error(response)

    def logout(self):

        self.__query('user.logout', {})
        self.auth = ''

    def get_graph_title(self, id_graph):

        graph_ids = []

        graph_ids.append(str(id_graph))

        response = self.__query('graph.get', {'graphids': graph_ids,
                                            'output': 'extend'})
        try:
            title = response['result'][0]['name']
            return title
        except KeyError:
            raise Zabbix_Error(response)

    def get_graph(self, graph, title, id_graph):

        graph_ids = []
        item_map = {}

        graph_ids.append(str(id_graph))

        response = self.__query('item.get', {'graphids': graph_ids,
                                           'output': 'extend'})
        try:
            items = response['result']
            for item in items:
                item_map[item['name']] = {'id': item['itemid'],
                                          'units': item['units']}

            history = self.__get_history(item_map)
            styles = self.__get_graph_styles(item_map)
            self.__convert_graph(graph, item_map, styles, history)
            graph.title = title

            return graph

        except KeyError:
            raise Zabbix_Error(response)
