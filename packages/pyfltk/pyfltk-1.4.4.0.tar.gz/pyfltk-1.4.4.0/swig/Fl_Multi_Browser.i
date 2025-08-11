/* File : Fl_Multi_Browser.i */
//%module Fl_Multi_Browser

%feature("docstring") ::Fl_Multi_Browser
"""
The Fl_Multi_Browser class is a subclass of Fl_Browser  which lets the user 
select any set of the lines. The user interface is Macintosh style: clicking 
an item turns off all the others and selects that one, dragging selects all 
the items the mouse moves over, and shift + click toggles the items. This 
is different then how forms did it. Normally the callback is done when the 
user releases the mouse, but you can change this with when().

See Fl_Browser for methods to add and remove lines from the browser. 
""" ;

%{
#include "FL/Fl_Multi_Browser.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Multi_Browser)

%include "FL/Fl_Multi_Browser.H"
