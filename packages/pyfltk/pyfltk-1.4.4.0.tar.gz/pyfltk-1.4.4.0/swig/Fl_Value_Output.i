/* File : Fl_Value_Output.i */
//%module Fl_Value_Output

%feature("docstring") ::Fl_Value_Output
"""
The Fl_Value_Output widget displays a floating point value. If step() is 
not zero, the user can adjust the value by dragging the mouse left and right. 
The left button moves one step()  per pixel, the middle by 10 * step(), and 
the right button by 100 * step().

This is much lighter-weight than Fl_Value_Input because it contains no text 
editing code or character buffer. 
""" ;

%{
#include "FL/Fl_Value_Output.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Value_Output)

%include "FL/Fl_Value_Output.H"
