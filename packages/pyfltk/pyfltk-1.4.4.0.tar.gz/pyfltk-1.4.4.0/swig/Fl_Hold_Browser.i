/* File : Fl_Hold_Browser.i */
//%module Fl_Hold_Browser

%feature("docstring") ::Fl_Hold_Browser
"""
The Fl_Hold_Browser class is a subclass of Fl_Browser  which lets the user 
select a single item, or no items by clicking on the empty space. As long 
as the mouse button is held down the item pointed to by it is highlighted, 
and this highlighting remains on when the mouse button is released. Normally 
the callback is done when the user releases the mouse, but you can change 
this with when().

See Fl_Browser for methods to add and remove lines from the browser. 
""" ;

%{
#include "FL/Fl_Hold_Browser.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Hold_Browser)

%include "FL/Fl_Hold_Browser.H"
