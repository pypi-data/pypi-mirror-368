/* File : Fl_Repeat_Button.i */
//%module Fl_Repeat_Button

%feature("docstring") ::Fl_Repeat_Button
"""
The Fl_Repeat_Button is a subclass of Fl_Button that generates a callback 
when it is pressed and then repeatedly generates callbacks as long as it 
is held down. The speed of the repeat is fixed and depends on the 
implementation.
""" ;

%{
#include "FL/Fl_Repeat_Button.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Repeat_Button)

%include "FL/Fl_Repeat_Button.H"
