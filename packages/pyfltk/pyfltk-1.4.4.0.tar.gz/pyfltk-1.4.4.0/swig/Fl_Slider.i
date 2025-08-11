/* File : Fl_Slider.i */
//%module Fl_Slider

%feature("docstring") ::Fl_Slider
"""
The Fl_Slider widget contains a sliding knob inside a box. It if often 
used as a scrollbar. Moving the box all the way to the top/left sets it 
to the minimum(), and to the bottom/right to the maximum(). The minimum() 
may be greater than the maximum() to reverse the slider direction.
""" ;

%{
#include "FL/Fl_Slider.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Slider)

%include "cstring.i"

// the following is needed to conform to the fltk signature
%cstring_mutable(char* format_string);

%include "FL/Fl_Slider.H"
