/* File : Fl_Dial.i */

%feature("docstring") ::Fl_Dial
"""
The Fl_Dial widget provides a circular dial to control a single floating 
point value.
""" ;

%{
#include "FL/Fl_Dial.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Dial)

%include "FL/Fl_Dial.H"

