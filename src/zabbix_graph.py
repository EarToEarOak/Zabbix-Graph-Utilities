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


from matplotlib.font_manager import FontProperties
import datetime
# For headless environment
# import matplotlib
# matplotlib.use("Agg")
import pylab


class Graph():

    title = ''
    plots = {}

    drawtype_mpl = {'#0': ('-', False),
                    '#1': ('-', True),
                    '#2': ('-', False),
                    '#3': (':', False),
                    '#4': ('--', False),
                    '#5': ('--', True),
                    }

    def __init__(self):

        self.title = ''
        self.plots = {}

    def __drawtype_to_mpl(self, drawtype):

        return self.drawtype_mpl[drawtype]

    def plot_mpl(self, width, height, invert, show_grid, show_legend):

        fg = 'black'
        bg = 'white'

        if invert:
            fg = 'white'
            bg = 'black'

        pylab.rcParams['figure.facecolor'] = bg
        pylab.rcParams['axes.facecolor'] = bg
        pylab.rcParams['axes.edgecolor'] = fg
        pylab.rcParams['axes.labelcolor'] = fg
        pylab.rcParams['text.color'] = fg
        pylab.rcParams['grid.color'] = fg
        pylab.rcParams['xtick.color'] = fg
        pylab.rcParams['ytick.color'] = fg

        figure = pylab.figure(figsize=(width, height))
        axes = figure.add_subplot(111)
        axes.set_title(self.title, fontsize='xx-large')
        axes.set_xlabel('')
        axes.tick_params(axis='both', which='major', labelsize='large')
        axes.grid(show_grid)

        plots = self.plots.items()
        plots.reverse()

        for _id, plot in plots:
            times = []
            if len(plot['value']):
                for time in plot['time']:
                    times.append(datetime.datetime.fromtimestamp(float(time)))
                label = format(u'{0} - ({1:g} {2})'.format(plot['name'],
                                                           float(plot['value'][-1]),
                                                           plot['units']))
                linestyle, fill = self.__drawtype_to_mpl(plot['drawtype'])
                if fill:
                    axes.fill_between(times, min(plot['value']),
                                      plot['value'], color=plot['colour'],
                                      label=label, antialiased=True)
                    show_legend = False
                else:
                    axes.plot(times, plot['value'], color=plot['colour'],
                              label=label, linewidth=4, linestyle=linestyle,
                              antialiased=True)
                axes.set_xticklabels(times, visible=False)
                axes.set_ylabel(plot['units'])
                axes.autoscale(True, 'both', True)

        if show_legend:
            font = FontProperties()
            font.set_size('xx-large')

            box = axes.get_position()
            axes.set_position([box.x0, box.y0 + box.height * 0.1,
                               box.width, box.height * 0.9])
            legend = axes.legend(loc='upper center', bbox_to_anchor=(0.5, 0),
                                 prop=font)
            for handle in legend.legendHandles:
                handle.set_linewidth(4)

        time_to = datetime.datetime.utcnow()
        time_from = time_to - datetime.timedelta(days=1)
        axes.set_xlim(time_from, time_to)

        return figure

    def close(self, figure):

        pylab.close(figure)
