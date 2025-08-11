/* File : Fl_Check_Browser.i */
//%module Fl_Check_Browser

%feature("docstring") ::Fl_Check_Browser
"""
The Fl_Check_Browser widget displays a scrolling list of text lines that may be selected and/or checked by the user.
""" ;

%{
#include "FL/Fl_Check_Browser.H"
%}

%ignore Fl_Check_Browser::add(char *s);  
%ignore Fl_Check_Browser::add(char *s, int b); 

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Check_Browser)

%include "FL/Fl_Check_Browser.H"


