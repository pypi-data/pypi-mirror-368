/* File : Fl_Free.i */
//%module Fl_Free

%feature("docstring") ::Fl_Free
"""
Emulation of the Forms 'free' widget. This emulation allows the free demo 
to run, and appears to be useful for porting programs written in Forms which 
use the free widget or make subclasses of the Forms widgets.

There are five types of free, which determine when the handle function is 
called:

      FL_NORMAL_FREE		1
      FL_SLEEPING_FREE		2
      FL_INPUT_FREE		3
      FL_CONTINUOUS_FREE	4
      FL_ALL_FREE		5

An FL_INPUT_FREE accepts FL_FOCUS events. A FL_CONTINUOUS_FREE sets a 
timeout callback 100 times a second and provides a FL_STEP event, this 
has obvious detrimental effects on machine performance. FL_ALL_FREE does 
both. FL_SLEEPING_FREE are deactivated. 
""" ;

%{
#include "FL/Fl_Free.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Free)

%include "FL/Fl_Free.H"
