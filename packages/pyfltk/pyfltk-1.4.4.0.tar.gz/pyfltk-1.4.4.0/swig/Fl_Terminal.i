/* File : Fl_Terminal.i */
//%module Fl_Terminal
%feature("docstring") ::Fl_Terminal
"""

""" ;

// Ignore the following methods:
//%rename("$ignore", regextarget=1, fullname=1) operator==;
//%rename("$ignore", regextarget=1, fullname=1) operator!=;
%ignore Fl_Terminal::vprintf(const char *fmt, va_list ap);


%{
#include "FL/Fl_Terminal.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Terminal)

%include "FL/Fl_Terminal.H"
