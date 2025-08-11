/* File : Fl_Return_Button.i */
//%module Fl_Return_Button

%feature("docstring") ::Fl_Return_Button
"""
The Fl_Return_Button is a subclass of Fl_Button that generates a callback 
when it is pressed or when the user presses the Enter key. A carriage-return 
symbol is drawn next to the button label.
""" ;

%{
#include "FL/Fl_Return_Button.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Return_Button)

%include "FL/Fl_Return_Button.H"
