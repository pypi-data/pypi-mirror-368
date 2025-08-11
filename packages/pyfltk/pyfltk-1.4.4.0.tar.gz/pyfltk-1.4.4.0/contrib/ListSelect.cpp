
#include "ListSelect.h"

#include <FL/Fl_Pixmap.H>
static unsigned char *image__upArrow[] = {
(unsigned char *)"32 32 17 1",
(unsigned char *)" \tc None",
(unsigned char *)".\tc #000000",
(unsigned char *)"+\tc #800000",
(unsigned char *)"@\tc #008000",
(unsigned char *)"#\tc #808000",
(unsigned char *)"$\tc #000080",
(unsigned char *)"%\tc #800080",
(unsigned char *)"&\tc #008080",
(unsigned char *)"*\tc #C0C0C0",
(unsigned char *)"=\tc #808080",
(unsigned char *)"-\tc #FF0000",
(unsigned char *)";\tc #00FF00",
(unsigned char *)">\tc #FFFF00",
(unsigned char *)",\tc #0000FF",
(unsigned char *)"\'\tc #FF00FF",
(unsigned char *)")\tc #00FFFF",
(unsigned char *)"!\tc #FFFFFF",
(unsigned char *)"                                ",
(unsigned char *)"                                ",
(unsigned char *)"                                ",
(unsigned char *)"               ..               ",
(unsigned char *)"              .==.              ",
(unsigned char *)"             .====.             ",
(unsigned char *)"            .==**==.            ",
(unsigned char *)"           .==****==.           ",
(unsigned char *)"          .==******==.          ",
(unsigned char *)"         .==********==.         ",
(unsigned char *)"        .==**********==.        ",
(unsigned char *)"       .==************==.       ",
(unsigned char *)"      .==**************==.      ",
(unsigned char *)"     .==****************==.     ",
(unsigned char *)"    .==******************==.    ",
(unsigned char *)"   .==********************==.   ",
(unsigned char *)"  .=!!!!!!=*********!!!!!!!!=.  ",
(unsigned char *)"  ........=*********!.........  ",
(unsigned char *)"         .=*********!.          ",
(unsigned char *)"         .=*********!.          ",
(unsigned char *)"         .=*********!.          ",
(unsigned char *)"         .=*********!.          ",
(unsigned char *)"         .=*********!.          ",
(unsigned char *)"         .=*********!.          ",
(unsigned char *)"         .=*********!.          ",
(unsigned char *)"         .=*********!.          ",
(unsigned char *)"         .=*********!.          ",
(unsigned char *)"         .=*********!.          ",
(unsigned char *)"         .=!!!!!!!!!!.          ",
(unsigned char *)"          ...........           ",
(unsigned char *)"                                ",
(unsigned char *)"                                "
};
static Fl_Pixmap pixmap__upArrow(image__upArrow);

static unsigned char *image__downArrow[] = {
(unsigned char *)"32 32 17 1",
(unsigned char *)" \tc None",
(unsigned char *)".\tc #000000",
(unsigned char *)"+\tc #800000",
(unsigned char *)"@\tc #008000",
(unsigned char *)"#\tc #808000",
(unsigned char *)"$\tc #000080",
(unsigned char *)"%\tc #800080",
(unsigned char *)"&\tc #008080",
(unsigned char *)"*\tc #C0C0C0",
(unsigned char *)"=\tc #808080",
(unsigned char *)"-\tc #FF0000",
(unsigned char *)";\tc #00FF00",
(unsigned char *)">\tc #FFFF00",
(unsigned char *)",\tc #0000FF",
(unsigned char *)"\'\tc #FF00FF",
(unsigned char *)")\tc #00FFFF",
(unsigned char *)"!\tc #FFFFFF",
(unsigned char *)"                                ",
(unsigned char *)"                                ",
(unsigned char *)"           ...........          ",
(unsigned char *)"          .!!!!!!!!!!=.         ",
(unsigned char *)"          .!*********=.         ",
(unsigned char *)"          .!*********=.         ",
(unsigned char *)"          .!*********=.         ",
(unsigned char *)"          .!*********=.         ",
(unsigned char *)"          .!*********=.         ",
(unsigned char *)"          .!*********=.         ",
(unsigned char *)"          .!*********=.         ",
(unsigned char *)"          .!*********=.         ",
(unsigned char *)"          .!*********=.         ",
(unsigned char *)"          .!*********=.         ",
(unsigned char *)"  .........!*********=........  ",
(unsigned char *)"  .=!!!!!!!!*********=!!!!!!=.  ",
(unsigned char *)"   .==********************==.   ",
(unsigned char *)"    .==******************==.    ",
(unsigned char *)"     .==****************==.     ",
(unsigned char *)"      .==**************==.      ",
(unsigned char *)"       .==************==.       ",
(unsigned char *)"        .==**********==.        ",
(unsigned char *)"         .==********==.         ",
(unsigned char *)"          .==******==.          ",
(unsigned char *)"           .==****==.           ",
(unsigned char *)"            .==**==.            ",
(unsigned char *)"             .====.             ",
(unsigned char *)"              .==.              ",
(unsigned char *)"               ..               ",
(unsigned char *)"                                ",
(unsigned char *)"                                ",
(unsigned char *)"                                "
};
static Fl_Pixmap pixmap__downArrow(image__downArrow);


void upCB( Fl_Widget *v, void *t)
{	
	((ListSelect *)(t))->upButtonCallback();
}

void downCB( Fl_Widget *v, void *t)
{	
	((ListSelect *)(t))->downButtonCallback();
}

void toggleCB( Fl_Widget *v, void *t)
{	
	((ListSelect *)(t))->toggleButtonCallback();
}

#define BORDER 8
#define BROWSER_BUTTON_BORDER ((int)(BORDER*1.5))
#define BROWSER_W (w-BORDER-BORDER)
#define BUTTON_H 38
#define BROWSER_H ((int)( \
	(h-BORDER-BROWSER_BUTTON_BORDER-BUTTON_H-BROWSER_BUTTON_BORDER-BORDER) / 2   ))
#define BUTTON_Y (BORDER+BROWSER_H+BROWSER_BUTTON_BORDER)
#define BOTBROWSER_Y ( BUTTON_Y+BUTTON_H+BROWSER_BUTTON_BORDER ) 

ListSelect::ListSelect(int x, int y, int w, int h, 
	char *topLabel, char *bottomLabel) :
	Fl_Group(x,y,w,h),
	topBrowser(BORDER, BORDER, BROWSER_W, BROWSER_H, topLabel),
	bottomBrowser(BORDER, BOTBROWSER_Y, BROWSER_W, BROWSER_H, bottomLabel),
	upButton(100, BUTTON_Y, 42, BUTTON_H),
	downButton(160, BUTTON_Y, 42, BUTTON_H),
	toggleButton(225, BUTTON_Y, 70, BUTTON_H, "Toggle")
{

	topBrowser.align(FL_ALIGN_TOP | FL_ALIGN_LEFT);
	bottomBrowser.align(FL_ALIGN_TOP | FL_ALIGN_LEFT );

	pixmap__upArrow.label(&upButton);
    pixmap__downArrow.label(&downButton);
	//upButton.labeltype(FL_SYMBOL_LABEL);
	//downButton.labeltype(FL_SYMBOL_LABEL);

	upButton.callback( (Fl_Callback *)upCB, (void *)this);
	downButton.callback( (Fl_Callback *)downCB, (void *)this);
	toggleButton.callback( (Fl_Callback *)toggleCB, (void *)this);

	end();

	//resizable(this);
	resize(x, y, w, h);

}

void ListSelect::upButtonCallback(void)
{ 
	moveSelected( bottomBrowser, topBrowser);
}

void ListSelect::downButtonCallback(void)
{
	moveSelected( topBrowser, bottomBrowser);
}

void ListSelect::moveSelected(Fl_Multi_Browser &fromB, Fl_Multi_Browser &toB)
{
	for (int i=1; i<=fromB.size(); i++)
	{
		if (fromB.selected(i))
		{
			toB.add(fromB.text(i), fromB.data(i));
			fromB.remove(i);
			--i;
		}
	}
	fromB.topline(1);
}

void ListSelect::toggleButtonCallback(void)
{
	toggleMultiBrowser(topBrowser);
	toggleMultiBrowser(bottomBrowser);
}

void ListSelect::toggleMultiBrowser(Fl_Multi_Browser &mb)
{
	for (int i=1; i<=mb.size(); i++)
	{
		mb.select( i, ( mb.selected(i)	? 0 : 1 ) );
	}
}

void ListSelect::resize(int x, int y, int w, int h)
{

	Fl_Group::resize(x, y, w, h);

	int b = 8;    //border
	int buh = 38; // all buttons height
	int abw = 42; //arrow buttons width
	int tbw = 70; //toggle button width 
	int abs = 12;  // arrow button spacing

	int ls = topBrowser.labelsize(); //label size

	int bbb =  (int)(b*1.5); // browser-button border
	int brw = w - b - b;  // browser width
	int brh = (int)( (h-(b+ls+bbb+buh+bbb+ls+b))/2 );   //browser height
	int atbs = (int)(abs*1.5); // arrow-toggle button spacing
	int ubx = (int)((w-(abw*2+tbw+abs+atbs))/2); //up button x
	int by = b+ls+brh+bbb;  //button y

	topBrowser.resize( b, b+ls, brw, brh );
	upButton.resize( ubx, by, abw, buh);
	downButton.resize( ubx+abw+abs, by, abw, buh );
	toggleButton.resize( ubx+abw+abs+abw+atbs, by, tbw, buh);
	bottomBrowser.resize( b, by+buh+bbb+ls, brw, brh);

}

