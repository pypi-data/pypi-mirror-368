/* File : Fl_Spinner.i */

%feature("docstring") ::Fl_Spinner
"""
The Fl_Spinner widget is a combination of the input widget and repeat 
buttons. The user can either type into the input area or use the buttons 
to change the value.
""" ;

%{
#include "FL/Fl_Spinner.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Spinner)

%ignore Fl_Spinner::minimum;
%ignore Fl_Spinner::maximum;

%include "FL/Fl_Spinner.H"

// hack to account for spelling mistakes in Fl_Spinner.H
%extend Fl_Spinner {

  %rename(minimum) min;
  %rename(maximum) max;

  void min(double m) {
    self->minimum(m);
  }

  double min() {
    return self->minimum();
  }

  void max(double m) {
    self->maximum(m);
  }

  double max() {
    return self->maximum();
  }
}


