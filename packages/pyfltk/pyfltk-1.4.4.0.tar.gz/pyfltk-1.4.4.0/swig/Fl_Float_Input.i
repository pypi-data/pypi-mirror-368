/* File : Fl_Float_Input.i */
//%module Fl_Float_Input

%feature("docstring") ::Fl_Float_Input
"""
The Fl_Float_Input class is a subclass of Fl_Input  that only allows the 
user to type floating point numbers (sign, digits, decimal point, more 
digits, 'E' or 'e', sign, digits).
""" ;

%{
#include "FL/Fl_Float_Input.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Float_Input)

%include "FL/Fl_Float_Input.H"
