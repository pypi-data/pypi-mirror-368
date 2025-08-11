/* File : Fl_File_Icon.i */
//%module Fl_File_Icon

%feature("docstring") ::Fl_File_Icon
"""
The Fl_File_Icon class manages icon images that can be used as labels in 
other widgets and as icons in the FileBrowser widget.
""" ;

%{

#include "FL/Fl_File_Icon.H"
%}

//%include "macros.i"
//CHANGE_OWNERSHIP(Fl_File_Icon)

%include "FL/Fl_File_Icon.H"
