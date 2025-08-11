/* File : Fl_Input_Choice.i */

%feature("docstring") ::Fl_Input_Choice
"""
A combination of the input widget and a menu button. The user can either 
type into the input area, or use the menu button chooser on the right, 
which loads the input area with predefined text. Normally it is drawn with 
an inset box and a white background.

The application can directly access both the input and menu widgets directly, 
using the menubutton() and input() accessor methods. 
""" ;

%{
#include "FL/Fl_Input_Choice.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Input_Choice)

%include "FL/Fl_Input_Choice.H"
