/* File : widget_casts.i */
//%module widget_casts

%{
#include "FL/Fl_Widget.H"
#include "FL/Fl_Button.H"
%}

%inline %{
/* C-style cast */
Fl_Window* castWidget2Window(Fl_Widget *source) {
   printf("castWidget2Window is deprecated!\n");
   return (Fl_Window *) source;
}

Fl_Menu* castWidget2Menu(Fl_Widget *source) {
   printf("castWidget2Menu is deprecated!\n");
   return (Fl_Menu *) source;
}

Fl_Menu_* castWidget2Menu_(Fl_Widget *source) {
   printf("castWidget2Menu_ is deprecated!\n");
   return (Fl_Menu_ *) source;
}

Fl_Button* castWidget2Btn(Fl_Widget *source) {
   printf("castWidget2Btn is deprecated!\n");
   return (Fl_Button *) source;
}

Fl_Browser* castWidget2Browser(Fl_Widget *source) {
   printf("castWidget2Browser is deprecated!\n");
   return (Fl_Browser *) source;
}

Fl_Slider* castWidget2Slider(Fl_Widget *source) {
   printf("castWidget2Slider is deprecated!\n");
   return (Fl_Slider *) source;
}

Fl_File_Chooser* castWidget2FileChooser(Fl_Widget *source) {
   printf("castWidget2FileChooser is deprecated!\n");
   return (Fl_File_Chooser *) source;
}

Fl_Dial* castWidget2Dial(Fl_Widget *source) {
   printf("castWidget2Dial is deprecated!\n");
   return (Fl_Dial *) source;
}

Fl_Box* castWidget2Box(Fl_Widget *source) {
   printf("castWidget2Box is deprecated!\n");
   return (Fl_Box *) source;
}

Fl_Adjuster* castWidget2Adjuster(Fl_Widget *source) {
   printf("castWidget2Adjuster is deprecated!\n");
   return (Fl_Adjuster *) source;
}

Fl_Valuator* castWidget2Valuator(Fl_Widget *source) {
   printf("castWidget2Valuator is deprecated!\n");
   return (Fl_Valuator *) source;
}

Fl_Scrollbar* castWidget2Scrollbar(Fl_Widget *source) {
   printf("castWidget2Scrollbar is deprecated!\n");
   return (Fl_Scrollbar *) source;
}

Fl_Scroll* castWidget2Scroll(Fl_Widget *source) {
   printf("castWidget2Scroll is deprecated!\n");
   return (Fl_Scroll *) source;
}
%}



