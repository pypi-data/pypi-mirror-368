/* File : Fl_Progress.i */
//%module Fl_Progress

%feature("docstring") ::Fl_Progress
"""
The Fl_Progress widget displays a progress bar for the user.
""" ;

%{
#include "FL/Fl_Progress.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Progress)

%include "FL/Fl_Progress.H"
