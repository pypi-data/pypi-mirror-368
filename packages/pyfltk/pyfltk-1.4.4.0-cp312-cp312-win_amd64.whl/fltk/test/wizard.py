#
# "$Id: wizard.py 28 2003-07-16 20:00:27Z andreasheld $"
#
# Wizard test program for pyFLTK the Python bindings
# for the Fast Light Tool Kit (FLTK).
#
# FLTK copyright 1998-1999 by Bill Spitzak and others.
# pyFLTK copyright 2003 by Andreas Held and others.
#
# This library is free software you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License, version 2.0 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA.
#
# Please report all bugs and problems to "pyfltk-user@lists.sourceforge.net".
#


from fltk import *


class Panel(Fl_Group):
    def __init__(self, X, Y, W, H, C, T):
        Fl_Group.__init__(self, X, Y, W, H, T)
        Fl_Group.align(self, FL_ALIGN_INSIDE | FL_ALIGN_CENTER)
        Fl_Group.box(self, FL_ENGRAVED_BOX)
        self.labelcolor(C)
        self.labelsize(20)
        self.end()


class Wizard(Fl_Wizard):
    def __init__(self, X, Y, W, H, T):
        Fl_Wizard.__init__(self, X, Y, W, H, T)
        self.p1 = Panel(X,Y,W,H, FL_RED,     "Panel 1")
        self.p2 = Panel(X,Y,W,H, FL_MAGENTA, "Panel 2")
        self.p3 = Panel(X,Y,W,H, FL_BLUE,    "Panel 3")
        self.value(self.p1)

    def next_callback(self, widget): 
        if self.value() == self.p3:
            self.value(self.p1)
        else:
            self.next()

    def prev_callback(self, widget):
        if self.value() == self.p1:
            self.value(self.p3)
        else:
            self.prev()
        

if __name__=='__main__':
    window = Fl_Window(300, 165, "Fl_Wizard test")
    wizard = Wizard(5, 5, 290, 100, "")
    wizard.end()
    
    buttons = Fl_Group(5, 110, 290, 50)
    buttons.box(FL_ENGRAVED_BOX)
    prev_button = Fl_Button( 15, 120, 110, 30, "@< Prev Panel")
    prev_button.callback(wizard.prev_callback)
    prev_button.align(FL_ALIGN_INSIDE | FL_ALIGN_CENTER | FL_ALIGN_LEFT)
    next_button = Fl_Button(175, 120, 110, 30, "Next Panel @>")
    next_button.align(FL_ALIGN_INSIDE | FL_ALIGN_CENTER | FL_ALIGN_RIGHT)
    next_button.callback(wizard.next_callback)
    buttons.end()
    window.end()
    window.show()
    Fl.run()
