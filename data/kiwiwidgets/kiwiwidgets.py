import os
import glob

from gi.repository import Gtk, GdkPixbuf

from kiwi.ui.hyperlink import HyperLink
from kiwi.ui.objectlist import ObjectList, ObjectTree
from kiwi.ui.widgets.label import ProxyLabel
from kiwi.ui.widgets.combo import ProxyComboEntry, ProxyComboBox
from kiwi.ui.widgets.checkbutton import ProxyCheckButton
from kiwi.ui.widgets.radiobutton import ProxyRadioButton
from kiwi.ui.widgets.entry import ProxyEntry, ProxyDateEntry
from kiwi.ui.widgets.spinbutton import ProxySpinButton
from kiwi.ui.widgets.textview import ProxyTextView
from kiwi.ui.widgets.button import ProxyButton

# pyflakes
HyperLink
ObjectList
ObjectTree
ProxyLabel
ProxyComboEntry
ProxyComboBox
ProxyCheckButton
ProxyRadioButton
ProxyEntry
ProxyDateEntry
ProxySpinButton
ProxyTextView
ProxyButton


def _get_icon_path():
    dirname = os.path.dirname(__file__)
    if not os.path.exists(os.path.join(dirname, '..', '.git')):
        icondir = os.path.join('/usr', 'share', 'glade3', 'pixmaps', '22x22')
    else:
        icondir = os.path.join(dirname, 'glade-plugin',
                               'resources', 'kiwiwidgets')
    return os.path.abspath(icondir)


def _register_icons():
    icondir = _get_icon_path()
    for filename in glob.glob(os.path.join(icondir, '*.png')):
        basename = os.path.basename(filename)
        name = basename[:-4]
        Gtk.IconTheme.add_builtin_icon(
            'widget-kiwi-%s' % (name,),
            22,
            GdkPixbuf.Pixbuf.new_from_file(filename))


_register_icons()
