%{
#include<stdio.h>
#include<stdlib.h>	
int valid = 1 ; 
%}

%token letter digit Type Semicolon keyword

%%
start : Type Identifier Semicolon

Identifier	: letter s
			  | keyword {printf("Syntax Error\n");
			  				valid  = 0 ;
			  			exit(0);}


s :     letter s

      | digit s

      |

      ;
%%


int yyerror(char *err)
{
	printf("Incorrect code\n");
	printf("%s",err);
	valid = 0; 
	return 0;
}

int main()
{
	printf("\nEnter a name to tested for identifier ");
	yyparse();

    if(valid)

    {
		printf("\nIt is a identifier!\n");
    }
}

