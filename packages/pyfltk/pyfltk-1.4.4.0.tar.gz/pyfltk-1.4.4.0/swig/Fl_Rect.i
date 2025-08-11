/* File : Fl_Rect.i */
//%module Fl_Rect
%feature("docstring") ::Fl_Rect
"""

""" ;

// Ignore the following methods:
%rename("$ignore", regextarget=1, fullname=1) operator==;
%rename("$ignore", regextarget=1, fullname=1) operator!=;

%{
#include "FL/Fl_Rect.H"
%}

%include "macros.i"

 //CHANGE_OWNERSHIP(Fl_Rect)

%include "FL/Fl_Rect.H"
