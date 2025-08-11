/* File : Fl_Fill_Dial.i */
//%module Fl_Fill_Dial

%feature("docstring") ::Fl_Fill_Dial
"""
The Fl_Fill_Dial widget provides a filled, circular dial to control a single 
floating point value.
""" ;

%{
#include "FL/Fl_Fill_Dial.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Fill_Dial)

%include "FL/Fl_Fill_Dial.H"
