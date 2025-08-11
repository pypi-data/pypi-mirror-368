/* File : Fl_Round_Button.i */
//%module Fl_Round_Button

%feature("docstring") ::Fl_Round_Button
"""
Buttons generate callbacks when they are clicked by the user. You control 
exactly when and how by changing the values for type() and when().

The Fl_Round_Button subclass display the 'on' state by turning on a light, 
rather than drawing pushed in. The shape of the 'light' is initially set 
to FL_ROUND_DOWN_BOX. The color of the light when on is controlled with 
selection_color(), which defaults to FL_RED.
""" ;

%{
#include "FL/Fl_Round_Button.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Round_Button)

%include "FL/Fl_Round_Button.H"
