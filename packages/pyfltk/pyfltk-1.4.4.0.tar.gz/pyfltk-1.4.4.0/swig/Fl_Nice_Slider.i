/* File : Fl_Nice_Slider.i */
//%module Fl_Nice_Slider

%feature("docstring") ::Fl_Nice_Slider
"""
The Fl_Nice_Slider widget contains a sliding knob inside a box. It is 
often used as a scrollbar. Moving the box all the way to the top/left sets 
it to the minimum(), and to the bottom/right to the maximum(). The minimum() 
may be greater than the maximum() to reverse the slider direction.
""" ;


%{
#include "FL/Fl_Nice_Slider.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Nice_Slider)

%include "FL/Fl_Nice_Slider.H"
