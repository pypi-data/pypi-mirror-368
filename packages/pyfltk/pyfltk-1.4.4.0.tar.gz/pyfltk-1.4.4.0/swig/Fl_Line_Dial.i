/* File : Fl_Line_Dial.i */
//%module Fl_Line_Dial

%feature("docstring") ::Fl_Line_Dial
"""
The Fl_Line_Dial widget provides a circular dial to control a single 
floating point value.
""" ;

%{
#include "FL/Fl_Line_Dial.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Line_Dial)

%include "FL/Fl_Line_Dial.H"
