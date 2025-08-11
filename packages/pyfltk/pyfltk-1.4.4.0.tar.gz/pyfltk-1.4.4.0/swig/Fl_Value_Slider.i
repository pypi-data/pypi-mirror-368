/* File : Fl_Value_Slider.i */
//%module Fl_Value_Slider

%feature("docstring") ::Fl_Value_Slider
"""
The Fl_Value_Slider widget is a Fl_Slider widget with a box displaying 
the current value.
""" ;

%{
#include "FL/Fl_Value_Slider.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Value_Slider)

%include "cstring.i"

// the following is needed to conform to the fltk signature
%cstring_mutable(char* format_string);

%include "FL/Fl_Value_Slider.H"
