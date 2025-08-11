/* File : Fl_Timer.i */
//%module Fl_Timer

%feature("docstring") ::Fl_Timer
"""
This is provided only to emulate the Forms Timer widget. It works by making 
a timeout callback every 1/5 second. This is wasteful and inaccurate if you 
just want something to happen a fixed time in the future. You should directly 
call Fl::add_timeout() instead.
""" ;

%{
#include "FL/Fl_Timer.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Timer)

%include "FL/Fl_Timer.H"
