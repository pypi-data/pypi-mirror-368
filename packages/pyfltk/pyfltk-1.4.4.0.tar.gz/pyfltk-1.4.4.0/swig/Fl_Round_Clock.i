/* File : Fl_Round_Clock.i */
//%module Fl_Round_Clock

%feature("docstring") ::Fl_Round_Clock
"""
This widget provides a round analog clock display and is provided for 
Forms compatibility. It installs a 1-second timeout callback using 
Fl::add_timeout().
""" ;

%feature("notabstract") Fl_Round_Clock;

%{
#include "FL/Fl_Round_Clock.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Round_Clock)

%include "FL/Fl_Round_Clock.H"
