/* File : Fl_Value_Input.i */
//%module Fl_Value_Input

%feature("docstring") ::Fl_Value_Input
"""
The Fl_Value_Input widget displays a numeric value. The user can click in 
the text field and edit it - there is in fact a hidden Fl_Input widget with 
type(FL_FLOAT_INPUT) or type(FL_INT_INPUT) in there - and when they hit 
return or tab the value updates to what they typed and the callback is done.

If step() is non-zero, the user can also drag the mouse across the object 
and thus slide the value. The left button moves one step() per pixel, the 
middle by 10 * step(), and the right button by 100 * step(). It is therefore 
impossible to select text by dragging across it, although clicking can still 
move the insertion cursor.

If step() is non-zero and integral, then the range of numbers are limited 
to integers instead of floating point values. 
""" ;

%{
#include "FL/Fl_Value_Input.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Value_Input)

%ignore Fl_Value_Input::input;

%include "FL/Fl_Value_Input.H"


