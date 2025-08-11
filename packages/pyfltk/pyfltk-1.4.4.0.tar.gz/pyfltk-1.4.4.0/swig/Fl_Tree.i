/* File : Fl_Tree.i */

%feature("docstring") ::Fl_Tree
"""
An expandable tree widget. Similar to Fl_Browser, Fl_Tree is browser of Fl_Tree_Item's, which can be in a parented hierarchy. Subtrees can be expanded or closed. Items can be added, deleted, inserted, sorted and re-ordered. The tree items may also contain other FLTK widgets, like buttons, input fields, or even 'custom' widgets.
""" ;

%{
#include "FL/Fl_Tree.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Tree)

%include "FL/Fl_Tree.H"

