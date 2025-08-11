/* File : Fl_File_Chooser.i */
//%module Fl_File_Chooser

%feature("docstring") ::Fl_File_Chooser
"""
The Fl_File_Chooser widget displays a standard file selection dialog that 
supports various selection modes.

The Fl_File_Chooser class also exports several static values that may be used 
to localize or customize the appearance of all file chooser dialogs:
Member 	Default value
add_favorites_label 	'Add to Favorites'
all_files_label 	'All Files (*)'
custom_filter_label 	'Custom Filter'
existing_file_label 	'Please choose an existing file!'
favorites_label 	'Favorites'
filename_label 		'Filename:'
filesystems_label 	'My Computer' (WIN32)
			'File Systems' (all others)
manage_favorites_label 	'Manage Favorites'
new_directory_label 	'New Directory?'
new_directory_tooltip 	'Create a new directory.'
preview_label 		'Preview'
save_label 		'Save'
show_label 		'Show:'
sort 			fl_numericsort

The sort member specifies the sort function that is used when loading the 
contents of a directory. 
""" ;

%{
#include "FL/Fl_File_Chooser.H"
%}

%include "macros.i"
//CHANGE_OWNERSHIP(Fl_File_Chooser)

%ignore Fl_File_Chooser::sort;
// this is not declared on all systems!
%ignore Fl_File_Chooser::rescan_keep_filename;

DEFINE_CALLBACK(Fl_File_Chooser)

%ignore Fl_File_Chooser::user_data(void *);
%ignore Fl_File_Chooser::user_data() const;

%include "FL/Fl_File_Chooser.H"

ADD_CALLBACK(Fl_File_Chooser)
ADD_USERDATA(Fl_File_Chooser)

%typemap(in) PyObject *PyFunc {
  if (!PyCallable_Check($input)) {
      PyErr_SetString(PyExc_TypeError, "Need a callable object!");
      return NULL;
  }
  $1 = $input;
}

