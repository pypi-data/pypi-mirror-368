/* File : Fl_Chart.i */
//%module Fl_Chart

%feature("docstring") ::Fl_Chart
"""
This widget displays simple charts and is provided for Forms compatibility.
""" ;

%{
#include "FL/Fl_Chart.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Chart)

%include "FL/Fl_Chart.H"
