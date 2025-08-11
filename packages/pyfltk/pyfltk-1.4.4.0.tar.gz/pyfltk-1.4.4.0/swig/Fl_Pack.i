/* File : Fl_Pack.i */
//%module Fl_Pack

%feature("docstring") ::Fl_Pack
"""
This widget was designed to add the functionality of compressing and 
aligning widgets.

If type() is FL_HORIZONTAL all the children are resized to the height of 
the Fl_Pack, and are moved next to each other horizontally. If type() is 
not FL_HORIZONTAL then the children are resized to the width and are stacked 
below each other. Then the Fl_Pack resizes itself to surround the child 
widgets.

This widget is needed for the Fl_Tabs. In addition you may want to put the 
Fl_Pack inside an Fl_Scroll. 
""" ;

%{
#include "FL/Fl_Pack.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Pack)

%include "FL/Fl_Pack.H"


