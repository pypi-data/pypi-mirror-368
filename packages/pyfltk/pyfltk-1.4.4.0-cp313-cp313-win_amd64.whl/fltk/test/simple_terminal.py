#
# "$Id: simple_terminal.py 624 2024-01-17 19:40:30U robertarkiletian $"
#
# Terminal test program for pyFLTK the Python bindings
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

import time
from fltk import *


def tick_cb():
    tty.printf(f'Timer tick: \033[32m{time.ctime()}\033[0m\n')
    Fl.repeat_timeout(2.0, tick_cb)

TERMINAL_HEIGHT=120
win = Fl_Double_Window(500, 200+TERMINAL_HEIGHT, "Your App")
win.begin()
box = Fl_Box(0, 0, win.w(), 200,
        "Your app GUI in this area.\n\n"
        "Your app's debugging output in tty below")
#Add simple terminal to bottom of app window for scrolling history of status messages.
tty = Fl_Terminal(0, 200, win.w(), TERMINAL_HEIGHT)
tty.ansi(True) #enable use of "\033[32m"
win.end()
win.resizable(win)
win.show()
Fl.add_timeout(0.5, tick_cb)
Fl.run()
 


