/* File : Fl_Tree_Item_Array.i */

%feature("docstring") ::Fl_Tree_Item_Array
"""
Because FLTK 1.x.x. has mandated that templates and STL not be used, we use this class to dynamically manage the arrays.
None of the methods do range checking on index values; the caller must be sure that index values are within the range 0<index<total() (unless otherwise noted).
""" ;

%{
#include "FL/Fl_Tree_Item_Array.H"
%}

%include "macros.i"

 //CHANGE_OWNERSHIP(Fl_Tree_Item_Array)

%include "FL/Fl_Tree_Item_Array.H"
