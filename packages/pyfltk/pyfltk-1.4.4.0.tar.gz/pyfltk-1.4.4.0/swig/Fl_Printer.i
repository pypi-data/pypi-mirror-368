/* File : Fl_Printer.i */

%feature("docstring") ::Fl_Printer
"""
Declaration of classes Fl_Printer, Fl_System_Printer and Fl_PostScript_Printer.
""" ;

%{
#include "FL/Fl_Printer.H"
%}

//%include "macros.i"

//CHANGE_OWNERSHIP(Fl_Printer)
%ignore Fl_PostScript_Printer;
%ignore Fl_System_Printer;


%include "FL/Fl_Printer.H"
