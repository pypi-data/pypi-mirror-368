/* File : Fl_Roller.i */
//%module Fl_Roller

%feature("docstring") ::Fl_Roller
"""
The Fl_Roller widget is a 'dolly' control commonly used to move 3D objects.
""" ;

%{
#include "FL/Fl_Roller.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Roller)

%include "FL/Fl_Roller.H"
