#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Search instantly as you type. Edvard Rejthar
# https://github.com/e3rd/zim-plugin-instantsearch
#
import gi
gi.require_version('Gtk', '3.0')

import logging
from collections import OrderedDict

from gi.repository import Gtk, Pango

from zim.actions import action
from zim.gui.mainwindow import MainWindowExtension
from zim.gui.widgets import Dialog
from zim.gui.widgets import InputEntry
from zim.history import HistoryList
from zim.history import HistoryPath
from zim.notebook import Path
from zim.plugins import PluginClass

logger = logging.getLogger('zim.plugins.recentpages')

class RecentPagesPlugin(PluginClass):

    plugin_info = {
        'name': _('Recent Pages'), # T: plugin name
        'description': _('''\
Show the recently viewed pages in a popup window.

(V 0.1.0)
'''),
        'author': "Marco Laspe"
    }


class RecentPagesMainWindowExtension(MainWindowExtension):

    uimanager_xml = '''
    <ui>
    <menubar name='menubar'>
            <menu action='tools_menu'>
                    <placeholder name='plugin_items'>
                            <menuitem action='recentpages'/>
                    </placeholder>
            </menu>
    </menubar>
    </ui>
    '''


    gui = None

    @action(_('_Recent Pages'), accelerator='<ctrl><shift>r') # T: menu item
    def recentpages(self):

        #init
        #TODO: Get Items from pathbar
        self.history = self.window.history.get_recent()

        # preferences
        # self.plugin.preferences['keystroke_delay']


        # Gtk
        self.gui = Dialog(self.window, _('Recent Pages'), buttons=None, defaultwindowsize=(400, -1))

        (px, py) = self.window.get_position()
        (pw, ph) = self.window.get_size()
        (x, y) = self.gui.get_position()
        self.gui.resize(300,100)
        self.gui.move(px + (pw / 2) - 150, py + (ph / 2) - 250)

        # Maybe add a filter field, like atom dialogs
        #self.inputEntry = InputEntry()
        #self.inputEntry.connect('key_press_event', self.move)
        #self.inputEntry.connect('changed', self.change) # self.change is needed by GObject or something
        #self.gui.vbox.pack_start(self.inputEntry, False, False, 0)


        self.listmodel = Gtk.ListStore(str)

        # My own model for creating dialog labels and later retrieving them
        self.model = OrderedDict()
        for page in self.history:
            # Get the page name directly from the page object
            ky = page.name if hasattr(page, 'name') else str(page)
            # If it's a full path, get just the last part
            if ':' in ky:
                ky = ky.split(':')[-1].strip()
            self.model[ky] = page

        # populate the treeview
        for row in self.model.keys():
            self.listmodel.append([row])
        self.treeview = Gtk.TreeView(model=self.listmodel)
        self.treeview.set_headers_visible(False)
        # cellrenderer to render the text
        cell = Gtk.CellRendererText()
        cell.set_property('ellipsize', Pango.EllipsizeMode.NONE)  # Don't truncate with ellipsis
        # the text in the first column should be in boldface
        # the column is created
        col = Gtk.TreeViewColumn("", cell, text=0)
        # and it is appended to the treeview
        self.treeview.append_column(col)

        self.treeview.connect("row-activated", self.on_row_activated)

        self.gui.vbox.pack_start(self.treeview, True, True, 0)

        self.gui.show_all()


    def on_row_activated(self, treeview, path, view_column):
        #self.gui.move(600, 600)
        #ui.open_page(path)
        (tm, it) = self.treeview.get_selection().get_selected()
        ky = tm[it][0]
        self.window.open_page(self.model[ky])
        self.gui.destroy()