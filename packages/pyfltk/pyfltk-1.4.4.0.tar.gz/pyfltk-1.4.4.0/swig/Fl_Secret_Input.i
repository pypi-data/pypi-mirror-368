/* File : Fl_Secret_Input.i */
//%module Fl_Secret_Input

%feature("docstring") ::Fl_Secret_Input
"""
The Fl_Secret_Input class is a subclass of Fl_Input  that displays its input 
as a string of asterisks. This subclass is usually used to receive passwords 
and other 'secret' information.
""" ;

%{
#include "FL/Fl_Secret_Input.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Secret_Input)

%include "FL/Fl_Secret_Input.H"
