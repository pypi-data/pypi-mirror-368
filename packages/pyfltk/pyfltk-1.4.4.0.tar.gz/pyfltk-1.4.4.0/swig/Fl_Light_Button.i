/* File : Fl_Light_Button.i */
//%module Fl_Light_Button

%feature("docstring") ::Fl_Light_Button
"""
Buttons generate callbacks when they are clicked by the user. You control 
exactly when and how by changing the values for type() and when().

The Fl_Light_Button subclass display the 'on' state by turning on a light, 
rather than drawing pushed in. The shape of the 'light' is initially set 
to FL_DOWN_BOX. The color of the light when on is controlled with 
selection_color(), which defaults to FL_YELLOW.
""" ;

%{
#include "FL/Fl_Light_Button.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Light_Button)

%include "FL/Fl_Light_Button.H"
