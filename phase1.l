%{
#include "y.tab.h"
#include<stdio.h>
%}
%%
("True"|"False") return keyword;
("int "|"char "|"boolean ") {return Type;}
[a-zA-Z][a-zA-Z_0-9]* return letter;
[0-9] return digit;
";" return Semicolon;
. return yytext[0];
\n return 0;
%%

int yywrap()
{
	return 1;
}