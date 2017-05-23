# encoding: iso-8859-1
from __future__ import print_function
from gi.repository import Gtk

from kiwi.ui.widgets.entry import ProxyEntry


def on_entry_activate(entry):
    print('You selected:', entry.read())
    Gtk.main_quit()

win = Gtk.Window()
win.connect('delete-event', Gtk.main_quit)

vbox = Gtk.VBox()
win.add(vbox)

# Normal entry
entry = ProxyEntry()
entry.data_type = str
entry.connect('activate', on_entry_activate)
entry.prefill(['Belo Horizonte', u'S�o Carlos',
               u'S�o Paulo', u'B�stad',
               u'�rnsk�ldsvik', 'sanca', 'sampa'])
vbox.pack_start(entry, True, True, 0)

entry = ProxyEntry()
entry.data_type = int
entry.connect('activate', on_entry_activate)
entry.prefill([('Brazil', 186),
               ('Sweden', 9),
               ('China', 1306)])
vbox.pack_start(entry, True, True, 0)

win.show_all()
Gtk.main()
