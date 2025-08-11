#
# "$Id: grid_buttons.py 28 2003-07-16 20:00:27Z andreasheld $"
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


if __name__=='__main__':
    win = Fl_Double_Window(460, 200, "Fl_Grid Row with 5 Buttons")
    grid = Fl_Grid(0, 0, win.w(), 50)
    grid.layout(1, 7, 10, 10)

    # create the buttons

    b0 = Fl_Button(0, 0, 80, 30, "New")
    b1 = Fl_Button(0, 0, 80, 30, "Options")
    b3 = Fl_Button(0, 0, 80, 30, "About")
    b4 = Fl_Button(0, 0, 80, 30, "Help")
    b6 = Fl_Button(0, 0, 80, 30, "Quit")

    grid.end()

    # assign buttons to grid positions

    grid.widget(b0, 0, 0)
    grid.widget(b1, 0, 1)
    grid.col_gap(1, 0)
    grid.widget(b3, 0, 3)
    grid.widget(b4, 0, 4)
    grid.col_gap(4, 0)
    grid.widget(b6, 0, 6)

    # set column weights for resizing (only empty columns resize)

    weight = [ 0, 0, 50, 0, 0, 50, 0 ];
    grid.col_weight(weight);

    grid.end()
    grid.show_grid(1)     # enable to display grid helper lines

    # add content ...

    g1 = Fl_Group(0, 50, win.w(), win.h() - 50)
    # add more widgets ...

    win.end()
    win.resizable(g1)
    win.size_range(win.w(), 100)

    
    win.show()
    Fl.run()
