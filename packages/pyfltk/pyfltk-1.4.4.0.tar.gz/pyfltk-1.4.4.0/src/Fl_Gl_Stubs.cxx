// This files implements stubs for missing OpenGl libraries.
//

#include <FL/Fl_Gl_Window.H>

Fl_Gl_Window::~Fl_Gl_Window()
{
}

void Fl_Gl_Window::show() {}
//void Fl_Gl_Window::show(int a, char **b) {}
void Fl_Gl_Window::flush() {}
void Fl_Gl_Window::hide() {}
void Fl_Gl_Window::resize(int,int,int,int) {}

//char Fl_Gl_Window::valid() const {return 0;}
//void Fl_Gl_Window::valid(char v) {}
void Fl_Gl_Window::invalidate() {}

//static int Fl_Gl_Window::can_do(int m) {return 0;}
//static int Fl_Gl_Window::can_do(const int *m) {return 0;}
//int Fl_Gl_Window::can_do() {return 0;}
int Fl_Gl_Window::can_do(int a, const int *b) {return 0;}
//Fl_Mode Fl_Gl_Window::mode() const {return 0;}
//int Fl_Gl_Window::mode(int a) {return 0;}
//int Fl_Gl_Window::mode(const int *a) {return 0;}
int Fl_Gl_Window::mode(int m, const int *a) {return 0;}

//void* Fl_Gl_Window::context() const {return 0;}
void Fl_Gl_Window::context(void*, int destroy_flag) {}
void Fl_Gl_Window::make_current() {}
void Fl_Gl_Window::swap_buffers() {}
void Fl_Gl_Window::ortho() {}

int Fl_Gl_Window::can_do_overlay() { return 0; }
void Fl_Gl_Window::redraw_overlay() {}
void Fl_Gl_Window::hide_overlay() {}
void Fl_Gl_Window::make_overlay_current() {}

void Fl_Gl_Window::draw_overlay() {}
void Fl_Gl_Window::init() {}

void Fl_Gl_Window::make_overlay() {}

//static int Fl_Gl_Window::can_do(int, const int *) {{}
//int Fl_Gl_Window::mode(int, const int *) {return 0;}

// gl stubs
void gl_start() {}
void gl_finish() {}
void gl_color(Fl_Color) {}
void gl_color(int c) {}
void gl_rect(int x,int y,int w,int h) {}
void gl_rectf(int x,int y,int w,int h) {}
//void gl_recti(int x,int y,int w,int h) {}
void gl_font(int fontid, int size) {}
int  gl_height() {return 0;}
int  gl_descent() {return 0;}
double gl_width(const char *) {return 0.0;}
double gl_width(const char *, int n) {return 0.0;}
double gl_width(uchar) {return 0.0;}

void gl_draw(const char*) {}
void gl_draw(const char*, int n) {}
void gl_draw(const char*, int x, int y) {}
void gl_draw(const char*, float x, float y) {}
void gl_draw(const char*, int n, int x, int y) {}
void gl_draw(const char*, int n, float x, float y) {}
void gl_draw(const char*, int x, int y, int w, int h, Fl_Align) {}
void gl_measure(const char*, int& x, int& y) {}

void gl_draw_image(const uchar *, int x,int y,int w,int h, int d=3, int ld=0) {}
  void glLoadIdentity( ) {}
  void glRecti( int x1, int y1, int x2, int y2 ) {}
  void glViewport( int x, int y, int width, int height ) {}
  void glClear( int mask ) {}
  void glColor3f( float red, float green, float blue ) {}
  void glBegin( int mode ) {}
  void glEnd( void ) {}
  void glVertex3f( float x, float y, float z ) {}


