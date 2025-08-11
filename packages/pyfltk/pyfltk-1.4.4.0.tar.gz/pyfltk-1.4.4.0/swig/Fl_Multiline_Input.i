/* File : Fl_Multiline_Input.i */
//%module Fl_Multiline_Input

%feature("docstring") ::Fl_Multiline_Input
"""
This input field displays '\n' characters as new lines rather than ^J, and 
accepts the Return, Tab, and up and down arrow keys. This is for editing 
multiline text.

This is far from the nirvana of text editors, and is probably only good for 
small bits of text, 10 lines at most. I think FLTK can be used to write a 
powerful text editor, but it is not going to be a built-in feature. Powerful 
text editors in a toolkit are a big source of bloat. 
""" ;

%{
#include "FL/Fl_Multiline_Input.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Multiline_Input)

%include "FL/Fl_Multiline_Input.H"
