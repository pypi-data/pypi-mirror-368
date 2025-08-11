/* File : Fl_Help_Dialog.i */
//%module Fl_Help_Dialog

%feature("docstring") ::Fl_Help_Dialog
"""
The Fl_Help_Dialog widget displays a standard help dialog window using the 
Fl_Help_View widget.
""" ;

%{
#include "FL/Fl_Help_Dialog.H"
%}

%include "macros.i"

//CHANGE_OWNERSHIP(Fl_Help_Dialog)
%include "FL/Fl_Help_Dialog.H"
