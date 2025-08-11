/* File : Fl_Browser_.i */

%feature("docstring") ::Fl_Browser_
"""
This is the base class for browsers. To be useful it must be subclassed 
and several virtual functions defined. The Forms-compatible browser and 
the file chooser's browser are subclassed off of this.

This has been designed so that the subclass has complete control over 
the storage of the data, although because next() and prev() functions 
are used to index, it works best as a linked list or as a large block 
of characters in which the line breaks must be searched for.

A great deal of work has been done so that the 'height' of a data object 
does not need to be determined until it is drawn. This is useful if 
actually figuring out the size of an object requires accessing image 
data or doing stat() on a file or doing some other slow operation. 
""" ;

%{
#include "FL/Fl_Browser_.H"
%}

%ignore Fl_Browser_::scrollbar;
%ignore Fl_Browser_::hscrollbar;

%ignore Fl_Browser_::draw(int,int,int,int);

// deprecated in fltk-1.4
%ignore Fl_Browser_::position;

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Browser_)

%include "FL/Fl_Browser_.H"


%extend Fl_Browser_ {
	Fl_Scrollbar* getScrollbar() {
		return &(self->scrollbar);
	}
	Fl_Scrollbar* getHScrollbar() {
		return &(self->hscrollbar);
	}
}	

