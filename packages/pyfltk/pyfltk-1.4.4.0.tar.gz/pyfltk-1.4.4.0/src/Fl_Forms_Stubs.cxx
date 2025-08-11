// This files implements stubs for missing Forms libraries.
//
#include <Fl/Fl_Widget.H>
#include <Fl/Fl_FormsBitmap.H>

Fl_FormsBitmap::Fl_FormsBitmap(
  Fl_Boxtype t, int X, int Y, int W, int H, const char* l) : Fl_Widget(X, Y, W, H, l)
{}

void Fl_FormsBitmap::set(int W, int H, const uchar *bits) {}

void Fl_FormsBitmap::draw() {}

#include <Fl/Fl_FormsPixmap.H>

Fl_FormsPixmap::Fl_FormsPixmap(
  Fl_Boxtype t, int X, int Y, int W, int H, const char* l)
: Fl_Widget(X, Y, W, H, l) 
{}

void Fl_FormsPixmap::set(char*const* bits) {}

void Fl_FormsPixmap::draw() {}

#include <FL/Fl_Free.H>

void Fl_Free::step(void *v) {}

Fl_Free::Fl_Free(uchar t,int X, int Y, int W, int H,const char *l,
		 FL_HANDLEPTR hdl) :
  Fl_Widget(X,Y,W,H,l) {}

Fl_Free::~Fl_Free() {}

void Fl_Free::draw() {}

int Fl_Free::handle(int e) { return 0; }


#include <FL/Fl_Timer.H>

void Fl_Timer::draw() {}

void Fl_Timer::stepcb(void* v) {}

void Fl_Timer::step() {}

int Fl_Timer::handle(int event) {
  return 0;
}

Fl_Timer::~Fl_Timer() {}

Fl_Timer::Fl_Timer(uchar t, int X, int Y, int W, int H, const char* l)
  : Fl_Widget(X, Y, W, H, l) {}

void Fl_Timer::value(double d) {}

void Fl_Timer::suspended(char d) {}

