/* File : Fl_File_Input.i */
//%module Fl_File_Input

%feature("docstring") ::Fl_File_Input
"""
This widget displays a pathname in a text input field. A navigation bar 
located above the input field allows the user to navigate upward in the 
directory tree.
""" ;

%{
#include "FL/Fl_File_Input.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_File_Input)

%include "FL/Fl_File_Input.H"
