#ifdef Check_Browser
%{
#include "Check_Browser.h"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Check_Browser)

class Check_Browser : public Fl_Browser_ {

public:
	Check_Browser(int x, int y, int w, int h, const char *l = 0);

	int add(char *s);               // add an (unchecked) item
	%name(add1) int add(char *s, int b);        // add an item and set checked
					// both return the new nitems()
	void clear();                   // delete all items
	int nitems() const { return nitems_; }
	int nchecked() const { return nchecked_; }
	int checked(int item) const;
	%name(checked1) void checked(int item, int b);
	void set_checked(int item) { checked(item, 1); }
	void check_all();
	void check_none();
	int value() const;              // currently selected item
	char *text(int item) const;     // returns pointer to internal buffer
};


#endif 
