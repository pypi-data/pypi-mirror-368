/* File : Fl_Scrollbar.i */
//%module Fl_Scrollbar

%feature("docstring") ::Fl_Scrollbar
"""
The Fl_Scrollbar widget displays a slider with arrow buttons at the ends 
of the scrollbar. Clicking on the arrows move up/left and down/right by 
linesize(). Scrollbars also accept FL_SHORTCUT events: the arrows move by 
linesize(), and vertical scrollbars take Page Up/Down (they move by the 
page size minus linesize()) and Home/End (they jump to the top or bottom).

Scrollbars have step(1) preset (they always return integers). If desired 
you can set the step() to non-integer values. You will then have to use 
casts to get at the floating-point versions of value() from Fl_Slider. 
""" ;

%{
#include "FL/Fl_Scrollbar.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Scrollbar)

%include "FL/Fl_Scrollbar.H"
