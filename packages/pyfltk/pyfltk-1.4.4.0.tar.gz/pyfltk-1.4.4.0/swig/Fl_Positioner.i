/* File : Fl_Positioner.i */

%feature("docstring") ::Fl_Positioner
"""
This class is provided for Forms compatibility. It provides 2D input. It 
would be useful if this could be put atop another widget so that the 
crosshairs are on top, but this is not implemented. The color of the 
crosshairs is selection_color().
""" ;


%{
#include "FL/Fl_Positioner.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Positioner)

%include "FL/Fl_Positioner.H"

