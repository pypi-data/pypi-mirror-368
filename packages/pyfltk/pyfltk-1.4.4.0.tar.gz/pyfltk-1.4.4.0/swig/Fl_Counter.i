/* File : Fl_Counter.i */
//%module Fl_Counter

%feature("docstring") ::Fl_Counter
"""
The Fl_Counter widget is provided for forms compatibility. It controls a 
single floating point value.
""" ;

%{
#include "FL/Fl_Counter.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Counter)

%include "FL/Fl_Counter.H"
