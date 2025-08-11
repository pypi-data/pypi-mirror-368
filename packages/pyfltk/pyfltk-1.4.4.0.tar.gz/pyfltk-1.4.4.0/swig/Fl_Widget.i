/* File : Fl_Widget.i */
//%module Fl_Widget

%feature("docstring") ::Fl_Widget
"""
Fl_Widget is the base class for all widgets in FLTK. You can't create one of 
these because the constructor is not public. However you can subclass it.

All 'property' accessing methods, such as color(), parent(), or argument() 
are implemented as trivial inline functions and thus are as fast and small 
as accessing fields in a structure. Unless otherwise noted, the property 
setting methods such as color(n) or label(s) are also trivial inline 
functions, even if they change the widget's appearance. It is up to the user 
code to call redraw() after these. 
""" ;

%{
#include <FL/Fl.H>
#include "FL/Fl_Widget.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Widget)

%pythonappend Fl_Widget::image(Fl_Image *a) %{
        if len(args) > 0:
            #delegate ownership to C++
            self.my_image = args[0]
%}
%pythonappend Fl_Widget::deimage(Fl_Image *a) %{
        if len(args) > 0:
            #delegate ownership to C++
            self.my_deimage = args[0]
%}

%pythonappend Fl_Widget::label %{
        if len(args) > 0:
            self.my_label = args[len(args)-1]
%}

DEFINE_CALLBACK(Fl_Widget)
  
%ignore Fl_Widget::image(Fl_Image& a);
%ignore Fl_Widget::deimage(Fl_Image& a);
//%ignore Fl_Widget::label;
%ignore Fl_Widget::user_data(void *);
%ignore Fl_Widget::user_data() const;

// typemap for Fl_Label::measure
%apply int *INOUT { int &w };
%apply int *INOUT { int &h };

// typemap for Fl_Widget::measure_label
%apply int *INOUT { int& ww };
%apply int *INOUT { int& hh };

%include "FL/Fl_Widget.H"

%clear int &w;
%clear int &h;
%clear int& ww;
%clear int& hh;

%extend Fl_Widget {
#include <FL/Fl_Window.H>
#include <FL/Fl_Image.H>

 // reimplementing protected member draw_label()
 void draw_label()
 {
   int X = self->x()+Fl::box_dx(self->box());
   int W = self->w()-Fl::box_dw(self->box());
   if (W > 11 && self->align()&(FL_ALIGN_LEFT|FL_ALIGN_RIGHT)) {X += 3; W -= 6;}
   self->draw_label(X, self->y()+Fl::box_dy(self->box()), W, self->h()-Fl::box_dh(self->box()),self->align());
 }

 // reimplementing protected member draw_label()
 void draw_backdrop()
 {
   if (self->align() & FL_ALIGN_IMAGE_BACKDROP) {
    const Fl_Image *img = self->image();
    // if there is no image, we will not draw the deimage either
    if (img && self->deimage() && !self->active_r())
      img = self->deimage();
    if (img) 
      ((Fl_Image*)img)->draw(self->x()+(self->w()-img->w())/2, self->y()+(self->h()-img->h())/2);
   }
 }
}

ADD_CALLBACK(Fl_Widget)
ADD_USERDATA(Fl_Widget)


%typemap(in) PyObject *PyFunc {
  if (!PyCallable_Check($input)) {
    PyErr_SetString(PyExc_TypeError, "Need a callable object!");
    return NULL;
  }
  $1 = $input;
}



