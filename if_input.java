class IfStatement {
    public static void main(String args) {

    	int number = 10;
    	// System.out.println("Number is positive.");
    	if (number > 0)
        {
    		number = 5;
     	}
     	else if(number==0)
     	{
     		number = 4;
     	}
        else
        {
            number = 2;
        }
    	// System.out.println("This statement is always executed.");
    }
}