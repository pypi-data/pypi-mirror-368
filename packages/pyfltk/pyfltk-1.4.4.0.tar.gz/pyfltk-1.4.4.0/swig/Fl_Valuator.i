/* File : Fl_Valuator.i */
//%module Fl_Valuator

%feature("docstring") ::Fl_Valuator
"""
The Fl_Valuator class controls a single floating-point value and provides 
a consistent interface to set the value, range, and step, and insures that 
callbacks are done the same for every object.
""" ;

%{
#include "FL/Fl_Valuator.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Valuator)



%include "cstring.i"

// the following is needed to conform to the fltk signature
%cstring_mutable(char* format_string);
//%include "FL/Fl_Valuator.H"

class Fl_Valuator : public Fl_Widget {
 protected:
  Fl_Valuator(int X, int Y, int W, int H, const char* L);

 public:
  ~Fl_Valuator() FL_OVERRIDE { };
  void bounds(double a, double b) {min=a; max=b;}
  double minimum() const {return min;}
  void minimum(double a) {min = a;}
  double maximum() const {return max;}
  void maximum(double a) {max = a;}
  void range(double a, double b) {min = a; max = b;}
  void step(int a) {A = a; B = 1;}
  void step(double a, int b) {A = a; B = b;}
  void step(double s);
  double step() const {return A/B;}
  void precision(int);

  double value() const {return value_;}
  int value(double);

  virtual int format(char* format_string);
  double round(double); // round to nearest multiple of step
  double clamp(double); // keep in range
  double increment(double, int); // add n*step to value
};

%pythoncode %{
FL_VERTICAL=0
FL_HORIZONTAL=1
%}
