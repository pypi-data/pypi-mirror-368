/* File : Fl_Text_Editor.i */
//%module Fl_Text_Editor

%feature("docstring") ::Fl_Text_Editor
"""
This is the FLTK text editor widget. It allows the user to edit multiple 
lines of text and supports highlighting and scrolling. The buffer that is 
displayed in the widget is managed by the Fl_Text_Buffer class.
""" ;

%{
#include "FL/Fl_Text_Editor.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Text_Editor)

// because of problems with Key_Binding
%ignore Fl_Text_Editor::add_key_binding(int key, int state, Key_Func f, Key_Binding** list);
%ignore Fl_Text_Editor::remove_key_binding(int key, int state, Key_Binding** list);
%ignore Fl_Text_Editor::remove_all_key_bindings(Key_Binding** list);
%ignore Fl_Text_Editor::add_default_key_bindings(Key_Binding** list);
%ignore Fl_Text_Editor::bound_key_function(int key, int state, Key_Binding* list);

%include "FL/Fl_Text_Editor.H"


