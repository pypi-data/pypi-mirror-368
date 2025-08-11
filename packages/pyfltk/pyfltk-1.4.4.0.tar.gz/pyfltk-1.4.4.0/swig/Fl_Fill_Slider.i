/* File : Fl_Fill_Slider.i */
//%module Fl_Fill_Slider

%feature("docstring") ::Fl_Fill_Slider
"""
The Fl_Fill_Slider widget contains a sliding knob inside a box. It if often 
used as a scrollbar. Moving the box all the way to the top/left sets it to 
the minimum(), and to the bottom/right to the maximum(). The minimum() may 
be greater than the maximum() to reverse the slider direction.
""" ;

%{
#include "FL/Fl_Fill_Slider.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Fill_Slider)

%include "FL/Fl_Fill_Slider.H"
