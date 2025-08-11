/* File : Fl_Input_.i */
//%module Fl_Input_

%feature("docstring") ::Fl_Input_
"""
This is a virtual base class below Fl_Input. It has all the same interfaces, 
but lacks the handle() and draw() method. You may want to subclass it if you 
are one of those people who likes to change how the editing keys work.

This can act like any of the subclasses of Fl_Input, by setting type() to one 
of the following values:

      FL_NORMAL_INPUT		0
      FL_FLOAT_INPUT		1
      FL_INT_INPUT		2
      FL_MULTILINE_INPUT	4
      FL_SECRET_INPUT		5
      FL_INPUT_TYPE		7
      FL_INPUT_READONLY		8
      FL_NORMAL_OUTPUT		(FL_NORMAL_INPUT | FL_INPUT_READONLY)
      FL_MULTILINE_OUTPUT	(FL_MULTILINE_INPUT | FL_INPUT_READONLY)
      FL_INPUT_WRAP		16
      FL_MULTILINE_INPUT_WRAP	(FL_MULTILINE_INPUT | FL_INPUT_WRAP)
      FL_MULTILINE_OUTPUT_WRAP 	(FL_MULTILINE_INPUT | FL_INPUT_READONLY | FL_INPUT_WRAP)

""" ;

%{
#include "FL/Fl_Input_.H"
%}

// deprecated in fltk-1.4
%ignore Fl_Input_::position;

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Input_)

//%ignore Fl_Input_::Fl_Input_(int, int, int, int, const char* = 0);

%include "FL/Fl_Input_.H"
