#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2003-2005 Async Open Source
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
# USA
# 
# Author(s): Christian Reis <kiko@async.com.br>
#            Lorenzo Gil Sanchez <lgs@sicem.biz>
#            Gustavo Rahal <gustavo@async.com.br>
#

"""Defines an enhanced version of GtkEntry"""

import gobject
import gtk

from kiwi import ValueUnset
from kiwi.interfaces import implementsIProxy, implementsIMandatoryProxy
from kiwi.ui.widgets.icon import IconEntry
from kiwi.ui.widgets.proxy import WidgetMixinSupportValidation
from kiwi.utils import gproperty, gsignal

(COL_TEXT,
 COL_OBJECT) = range(2)

(ENTRY_MODE_TEXT,
 ENTRY_MODE_DATA) = range(2)

class Entry(gtk.Entry, WidgetMixinSupportValidation):
    """The Kiwi Entry widget has many special features that extend the basic
    gtk entry.
    
    First of all, as every Kiwi Widget, it implements the Proxy protocol.
    As the users types the entry can interact with the application model
    automatically. 
    Kiwi Entry also implements interesting UI additions. If the input data
    does not match the data type of the entry the background nicely fades
    to a light red color. As the background changes an information icon
    appears. When the user passes the mouse over the information icon a
    tooltip is displayed informing the user how to correctly fill the
    entry. When dealing with date and float data-type the information on
    how to fill these entries is displayed according to the current locale.
    """
    implementsIProxy()
    implementsIMandatoryProxy()

    gproperty("completion", bool, False, 
              "Completion", gobject.PARAM_READWRITE)
    gproperty('exact-completion', bool, True)
        
    def __init__(self):
        gtk.Entry.__init__(self)
        WidgetMixinSupportValidation.__init__(self)
        self._completion = False
        self._current_object = None
        self._entry_mode = ENTRY_MODE_TEXT
        self._exact_completion = True
        self._icon = IconEntry(self)
        self.show()

    # Virtual methods
    gsignal('changed', 'override')
    def do_changed(self):
        """Called when the content of the entry changes.

        Sets an internal variable that stores the last time the user
        changed the entry
        """

        self.chain()

        self._update_current_object(self.get_text())
        self.emit('content-changed')

    # Properties
    
    def prop_get_exact_completion(self):
        return self._exact_completion

    def prop_set_exact_completion(self, value):
        self._exact_completion = value
        
        if value:
            match_func = self._completion_exact_match_func
        else:
            match_func = self._completion_normal_match_func
        completion = self._create_completion()
        completion.set_match_func(match_func)
                
    def prop_get_completion(self):
        return self._completion
    
    def prop_set_completion(self, value):
        self._completion = value

        if not self.get_completion():
            self._enable_completion()
    
    # Public API
    def set_exact_completion(self, value):
        """
        Enable exact entry completion.
        Exact means it needs to start with the value typed
        and the case needs to be correct.
        
        @param value: enable exact completion
        @type value:  boolean
        """
        
        self.prop_set_exact_completion(value)
        self.notify('exact-completion')

    # XXX: Decide if this API or the Combobox prefill API should be used
    def set_completion_strings(self, strings=[], values=[]):
        """
        Set strings used for entry completion.
        If values are provided, each string will have an additional
        data type.
        
        @param strings:
        @type  strings: list of strings
        @param values:
        @type  values: list of values
        """

        completion = self._create_completion()
        model = completion.get_model()
        model.clear()
        
        if values:
            if len(strings) != len(values):
                raise ValueError("values must have the same length as strings")
                
            for i, text in enumerate(strings):
                model.append([text, values[i]])
            self._entry_mode = ENTRY_MODE_DATA
        elif not strings:
            # This is considered disabling completion, PyGTK 2.8.1
            #self.set_completion(None)
            pass
        else:
            for s in strings:
                model.append([s, None])
            self._entry_mode = ENTRY_MODE_TEXT

    def set_text(self, text):
        self._update_current_object(text)
                
        gtk.Entry.set_text(self, text)
        self.emit('content-changed')

    # Private / Semi-Private
    def _update_current_object(self, text):
        if self._entry_mode != ENTRY_MODE_DATA:
            return
        
        obj = None
        for row in self.get_completion().get_model():
            if row[COL_TEXT] == text:
                self._current_object = row[COL_OBJECT]
                break
        else:
            self._current_object = None

    def _get_text_from_object(self, obj):
        if self._entry_mode != ENTRY_MODE_DATA:
            return
        
        for row in self.get_completion().get_model():
            if row[COL_OBJECT] == obj:
                return row[COL_TEXT]
        
    def _create_completion(self):
        # Check so we have completion enabled, not this does not
        # depend on the property, the user can manually override it,
        # as long as there is a completion object set
        completion = self.get_completion()
        if completion:
            return completion
        
        return self._enable_completion()
        
    def _enable_completion(self):
        completion = gtk.EntryCompletion()
        self.set_completion(completion)
        completion.set_model(gtk.ListStore(str, object))
        completion.set_text_column(0)
        self.prop_set_exact_completion(False)
        completion.connect("match-selected",
                           self._on_completion__match_selected)
        self._current_object = None
        return completion
    
    def _completion_exact_match_func(self, completion, _, iter):
        model = completion.get_model()
        if not len(model):
            return

        content = model[iter][COL_TEXT]
        return self.get_text().startswith(content)

    def _completion_normal_match_func(self, completion, _, iter):
        model = completion.get_model()
        if not len(model):
            return

        content = model[iter][COL_TEXT].lower()
        return self.get_text().lower() in content

    def _on_completion__match_selected(self, completion, model, iter):
        if not len(model):
            return

        text, data = model[iter]
        self.set_text(text)
        self.set_position(-1)
        self._current_object = data
        self.emit('content-changed')
        
    def read(self):
        mode = self._entry_mode
        if mode == ENTRY_MODE_TEXT:
            value = self.get_text()
        elif mode == ENTRY_MODE_DATA:
            value = self._current_object
        else:
            raise AssertionError

        return self.validate_data(value)
    
    def update(self, data):
        if data is ValueUnset or data is None:
            self.set_text("")
            return
        
        mode = self._entry_mode
        if mode == ENTRY_MODE_DATA:
            new = self._get_text_from_object(data)
            if new is None:
                raise TypeError("%r is not a data object" % data)
            data = new
        elif mode == ENTRY_MODE_TEXT:
            data = self.type2str(data)

        self.set_text(data)

    def do_expose_event(self, event):
        gtk.Entry.do_expose_event(self, event)

        if event.window == self.window:
            self._icon.draw_pixbuf()

    gsignal('size-allocate', 'override')
    def do_size_allocate(self, allocation):
        #gtk.Entry.do_size_allocate(self, allocation)
        self.chain(allocation)
	
	if self.flags() & gtk.REALIZED:
            self._icon.resize_windows()

    def do_realize(self):
        gtk.Entry.do_realize(self)
        self._icon.construct()
        
    def do_unrealize(self):
        self._icon.deconstruct()
        gtk.Entry.do_unrealize(self)
        
    # IconEntry
    
    def set_pixbuf(self, pixbuf):
        self._icon.set_pixbuf(pixbuf)
        
    def update_background(self, color):
        self._icon.update_background(color)
        
    def get_icon_window(self):
        return self._icon.get_icon_window()

gobject.type_register(Entry)
    
