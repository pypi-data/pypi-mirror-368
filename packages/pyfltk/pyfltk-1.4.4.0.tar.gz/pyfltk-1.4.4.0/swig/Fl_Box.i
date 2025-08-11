/* File : Fl_Box.i */
//%module Fl_Box

%feature("docstring") ::Fl_Box
"""
This widget simply draws its box, and possibly it's label. 
Putting it before some other widgets and making it big enough 
to surround them will let you draw a frame around them.
""" ;

%{
#include "FL/Fl_Box.H"
  %}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Box)

%include "FL/Fl_Box.H"


