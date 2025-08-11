/* File : Fl_Int_Input.i */
//%module Fl_Int_Input

%feature("docstring") ::Fl_Int_Input
"""
The Fl_Int_Input class is a subclass of Fl_Input  that only allows the user 
to type decimal digits (or hex numbers of the form 0xaef).
""" ;

%{
#include "FL/Fl_Int_Input.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Int_Input)

%include "FL/Fl_Int_Input.H"
