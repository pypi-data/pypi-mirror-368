#ifndef MyListSelect_h
#define MyListSelect_h

#include <FL/Fl.H>
#include <FL/Fl_Button.H>
#include <FL/Fl_Group.H>
#include <FL/Fl_Multi_Browser.H>
#include <FL/Fl_Pack.H>
#include <FL/Fl_Window.H>

extern void upCB( Fl_Widget *v, void *);
extern void downCB( Fl_Widget *v, void *);
extern void toggleCB( Fl_Widget *v, void *);

class ListSelect : public Fl_Group
{
	public:
		ListSelect(int x, int y, int w, int h, 
			char *topLabel=0, char *bottomLabel=0);

                Fl_Multi_Browser* getTopBrowser() { return &topBrowser;};
                Fl_Multi_Browser* getBottomBrowser() { return &bottomBrowser;};

        protected:
		Fl_Multi_Browser topBrowser;
		Fl_Multi_Browser bottomBrowser;


		virtual void resize(int x, int y, int w, int h);

		//toggles selection state of every item in the browser
		void toggleMultiBrowser(Fl_Multi_Browser &mb);

		//moves selected items from one browser to another	
		void moveSelected(Fl_Multi_Browser &fromB, Fl_Multi_Browser &toB);


		void upButtonCallback(void);
		void downButtonCallback(void);
		void toggleButtonCallback(void);

		friend void upCB( Fl_Widget *v, void *);
		friend void downCB( Fl_Widget *v, void *);
		friend void toggleCB( Fl_Widget *v, void *);

		Fl_Button upButton;
		Fl_Button downButton;
		Fl_Button toggleButton;

};


#endif
