
# browserData.py test program for pyFLTK the Python bindings
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


print("""
This is a quick hack to check setting and getting browser data 
""")

from fltk import *


# global object names
aBrowser = None	  # type 'Browser' from '()'


def onOK(ptr):
	import sys  # code
	#checkBrowserCallback(aBrowser.this)  # code
	sys.exit(0)  # code


def main():
	global aBrowser

	win = Fl_Window(394, 309, 245, 133, "check_browser.py")
	#win.thisown = 0

	aBrowser = Fl_Browser(5, 5, 240, 75)
	#aBrowser.thisown = 0
	aBrowser.end()

	btn = Fl_Return_Button(160, 90, 70, 30, "OK")
	#o_2_1.thisown = 0
	btn.label('OK')
	btn.callback(onOK)
	win.label('check_browser.py')
	win.end()
	aBrowser.add("Guiness", "line 1" )  # code
	aBrowser.add("Bud", "line 2")  # code
	aBrowser.add("Coors", "line 3")
	aBrowser.add("rocky mountain", "line 4")  # code
	aBrowser.add("Grimbergen", "line 5")  # code
	aBrowser.add("Burning River", "line 6")  # code
	aBrowser.add("Little Kings", "line 7")  # code

	return win



if __name__=='__main__':
	import sys
	window = main()
	window.show(len(sys.argv), sys.argv)
	print(aBrowser)
	d="data for 1"
	print("data(1,"+d+")")
	aBrowser.data(1, d)
	aBrowser.data(2, 123)
	print("data(1):", aBrowser.get_data(1))
	print("data(2):", aBrowser.get_data(2))
	print("data(3):", aBrowser.get_data(3))

	Fl.run()

