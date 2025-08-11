/* File : filename.i */
//%module filename
%include "cstring.i"

%{
#include "FL/filename.H"
%}

%cstring_bounded_mutable(char *to, 1024);

%ignore Fl_File_Sort_F;
%ignore fl_filename_list;
%ignore fl_numericsort;
%ignore fl_alphasort;
%ignore fl_casealphasort;
%ignore fl_casenumericsort;
%ignore _fl_filename_isdir_quick;

%include "FL/filename.H"

