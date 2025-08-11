/* File : Fl_Postscript.i */

%feature("docstring") ::Fl_PostScript
"""
Declaration of classes Fl_Postscript, Fl_System_Printer and Fl_PostScript_Printer.
""" ;

%{
#include "FL/Fl_PostScript.H"
%}

//%include "macros.i"

//CHANGE_OWNERSHIP(Fl_PostScript)

%ignore Fl_PostScript_Graphics_Driver::width;
%ignore Fl_PostScript_Graphics_Driver::height;
%ignore Fl_PostScript_Graphics_Driver::place;
%ignore Fl_PostScript_Graphics_Driver::descent;
%ignore Fl_PostScript_Graphics_Driver::transformed_draw;

%include "FL/Fl_PostScript.H"
