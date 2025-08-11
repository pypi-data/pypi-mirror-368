/* File : Fl_Paged_Device.i */

%feature("docstring") ::Fl_Paged_Device
"""
 Represents page-structured drawing surfaces.
 
 This class has no public constructor: don't instantiate it; use Fl_Printer 
 or Fl_PostScript_File_Device instead.
""" ;

%{
#include "FL/Fl_Paged_Device.H"
%}

//%include "macros.i"

//CHANGE_OWNERSHIP(Fl_Paged_Device)

%include "FL/Fl_Paged_Device.H"
