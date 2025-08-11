#
# "$Id: widgets.py 28 2003-07-16 20:00:27Z andreasheld $"
#
# Widgets test program for pyFLTK the Python bindings
# for the Fast Light Tool Kit (FLTK).
#
# FLTK copyright 1998-1999 by Bill Spitzak and others.
# pyFLTK copyright 2003 by Andreas Held and others.
# Copyright 2024 - Gonzalo Garramuño. All rights reserved.
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

#
# Constants
#
ROUND_SIZE = 5

def cb_menu(o, data):
    print('Menu value=',o.value())
    
class RoundMenuButton(Fl_Menu_Button):
    def __init__(self, X, Y, W, H, L = None):
        super().__init__(X, Y, W, H, L)
        self.box(FL_NO_BOX)
        self.align(FL_ALIGN_INSIDE | FL_ALIGN_CENTER)
        self.labelsize(16)
        self.labelcolor(FL_WHITE)

    def handle(self, event):
        if event == FL_PUSH:
            # Turn Left Mouse Button clicks into Right Mouse Button clicks
            if Fl.event_button1():
                Fl.e_keysym.fset(FL_Button + 3)
                print(f"Fl.e_keysym is now: {Fl.e_keysym.fget()}")
        return super().handle(event)
    
    def draw(self):
        X = self.x() + ROUND_SIZE
        Y = self.y()
        W = self.w() - ROUND_SIZE * 2
        H = self.h()
    
        fl_color(self.color()-5)

        fl_rounded_rectf(X, Y, W, H, ROUND_SIZE)

        self.draw_label()


if __name__ == "__main__":
    win = Fl_Window(640, 480)
    menu = RoundMenuButton( 30, 20, 300, 30, "Menu should appear with LMB or RMB")
    menu.add('Do something')
    menu.add('Do another')
    menu.callback(cb_menu, None)
    win.show()
    Fl.run()
