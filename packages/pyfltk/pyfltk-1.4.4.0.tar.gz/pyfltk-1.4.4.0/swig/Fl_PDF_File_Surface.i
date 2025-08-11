/* File : Fl_PDF_File_Surface.i */

%feature("docstring") ::Fl_PDF_File_Surface
"""
Declaration of classes Fl_PDF_File_Surface.
""" ;

%{
#include "FL/Fl_PDF_File_Surface.H"
%}

//%include "macros.i"

//CHANGE_OWNERSHIP(Fl_PDF_File_Surface)

// origin method
%apply int* OUTPUT { int* x };
%apply int* OUTPUT { int* y };

// printable_rect method
%apply int* OUTPUT { int* w };
%apply int* OUTPUT { int* h };

// margins method
%apply int* OUTPUT { int* left };
%apply int* OUTPUT { int* top };
%apply int* OUTPUT { int* right };
%apply int* OUTPUT { int* bottom };

%include "FL/Fl_PDF_File_Surface.H"
