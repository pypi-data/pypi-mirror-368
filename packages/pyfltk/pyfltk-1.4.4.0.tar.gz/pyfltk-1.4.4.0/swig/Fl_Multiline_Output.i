/* File : Fl_Multiline_Output.i */
//%module Fl_Multiline_Output

%feature("docstring") ::Fl_Multiline_Output
"""
This widget is a subclass of Fl_Output that displays multiple lines of text. 
It also displays tab characters as whitespace to the next column.
""" ;

%{
#include "FL/Fl_Multiline_Output.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Multiline_Output)

%include "FL/Fl_Multiline_Output.H"
