
#
# "$Id: file_chooser.py 495 2013-03-30 09:39:45Z andreasheld $"
#
# File chooser test program for pyFLTK the Python bindings
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
import sys

# globals
TERMINAL_HEIGHT = 120
fc = None
filter = None
files = None
relative = ""

def PickFile_CB(widget):
        global G_filename
        global G_tty
        # Create native chooser
        native = Fl_Native_File_Chooser()
        native.title("Pick a file")
        native.directory(G_filename.value())
        native.type(Fl_Native_File_Chooser.BROWSE_FILE)
        # Show native chooser
        status = native.show()
        if status == -1:
                G_tty.printf("ERROR: %s\n", native.errmsg())
        elif status == 1:
                G_tty.printf("*** CANCEL\n")
                fl_beep()
        else:
                if native.filename():
                        G_filename.value(native.filename())
                        G_tty.printf("filename='%s'\n"%native.filename())
                else:
                        G_filename.value("NULL");
                        G_tty.printf("dirname='(null)'\n")

def PickDir_CB(widget):
        global G_filename
        global G_tty
        # Create native chooser
        native = Fl_Native_File_Chooser()
        native.title("Pick a directory")
        native.directory(G_filename.value())
        native.type(Fl_Native_File_Chooser.BROWSE_DIRECTORY)
        # Show native chooser
        status = native.show()
        if status == -1:
                G_tty.printf("ERROR: %s\n", native.errmsg())
        elif status == 1:
                G_tty.printf("*** CANCEL\n")
                fl_beep()
        else:
                if native.filename():
                        G_filename.value(native.filename())
                        G_tty.printf("dirname='%s'\n"%native.filename())
                else:
                        G_filename.value("NULL");
                        G_tty.printf("dirname='(null)'\n")


if __name__=='__main__':
        global G_filename
        argn = 1
        
        Fl_File_Icon.load_system_icons()

        win = Fl_Window(640, 400+TERMINAL_HEIGHT, "Native File Chooser Test")
        win.size_range(win.w(), win.h(), 0, 0)
        win.begin()

        G_tty = Fl_Terminal(0,400,win.w(),TERMINAL_HEIGHT)
        x = 80
        y = 10
        G_filename = Fl_Input(x, y, win.w()-80-10, 25, "Filename")
        G_filename.value(".")
        G_filename.tooltip("Default filename")

        y += G_filename.h() + 10
        G_filter = Fl_Multiline_Input(x, y, G_filename.w(), 100, "Filter")
        G_filter.value("Text\t*.txt\n"
                    "C Files\t*.{cxx,h,c,cpp}\n"
                    "Tars\t*.{tar,tar.gz}\n"
                    "Apps\t*.app")
        G_filter.tooltip("Filter to be used for browser.\n"
                      "An empty string may be used.\n")

        y += G_filter.h() + 10
        view = Fl_Help_View(x, y, G_filename.w(), 200)
        view.box(FL_FLAT_BOX)
        view.color(win.color())
        #define TAB "&lt;Tab&gt;"
        view.textfont(FL_HELVETICA)
        view.textsize(10)
        view.value("The Filter can be one or more filter patterns, one per line.\n"
                "Patterns can be:<ul>\n"
                "  <li>A single wildcard (e.g. <tt>\"*.txt\"</tt>)</li>\n"
                "  <li>Multiple wildcards (e.g. <tt>\"*.{cxx,h,H}\"</tt>)</li>\n"
                "  <li>A descriptive name followed by a &lt;Tab&gt; and a wildcard (e.g. <tt>\"Text Files&lt;Tab&gt;*.txt\"</tt>)</li>\n"
                "</ul>\n"
                "In the above \"Filter\" field, you can use <b><font color=#55f face=Courier>Ctrl-I</font></b> to enter &lt;Tab&gt; characters as needed.<br>\n"
                "Example:<pre>\n"
                "\n"
                "    Text<font color=#55f>&lt;Ctrl-I&gt;</font>*.txt\n"
                "    C Files<font color=#55f>&lt;Ctrl-I&gt;</font>*.{cxx,h,c,cpp}\n"
                "    Tars<font color=#55f>&lt;Ctrl-I&gt;</font>*.{tar,tar.gz}\n"
                "    Apps<font color=#55f>&lt;Ctrl-I&gt;</font>*.app\n"
                "</pre>\n")

        but = Fl_Button(win.w()-x-10, win.h()-TERMINAL_HEIGHT-25-10, 80, 25, "Pick File")
        but.callback(PickFile_CB)

        butdir = Fl_Button(but.x()-x-10, win.h()-TERMINAL_HEIGHT-25-10, 80, 25, "Pick Dir")
        butdir.callback(PickDir_CB)

        win.resizable(G_filter)

        win.end()
        win.show()

        Fl.run()



