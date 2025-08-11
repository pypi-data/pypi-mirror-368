/* File : Fl_Clock.i */

%feature("docstring") ::Fl_Clock
"""
This widget provides a round analog clock display and is provided for Forms 
compatibility. It installs a 1-second timeout callback using Fl.add_timeout().
""" ;

%{
#include "FL/Fl_Clock.H"
%}

%ignore Fl_Clock::update();

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Clock)

CHANGE_OWNERSHIP(Fl_Clock_Output)

%include "FL/Fl_Clock.H"

