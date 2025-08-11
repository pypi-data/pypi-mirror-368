/* File : Fl_Adjuster.i */
//%module Fl_Adjuster

%feature("docstring") ::Fl_Adjuster
"""
The Fl_Adjuster widget has proven to be very useful for values that need a 
was stolen from Prisms, and large dynamic range.
When you press a button and drag to the right the value increases. When you 
drag to the left it decreases. The largest button adjusts by 100 * step(), 
the next by 10 * step() and that smallest button by step(). Clicking on the 
buttons increments by 10 times the amount dragging by a pixel does. 
Shift + click decrements by 10 times the amount. 
"""  ;

%{
#include "FL/Fl_Adjuster.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Adjuster)

%include "FL/Fl_Adjuster.H"
