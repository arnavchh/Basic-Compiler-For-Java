class JavaConstructs {
    
    public static void main(String args) {

        int a;
        int q;
        int number = 10;
        float decimal = 115.17;
        boolean b1;
        int[] arr1;
        float arr2[];
        
        q = 1+2;
        a = q+1;

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
        int num = 0;
        do
        {
             num = num + number;
        }while( number < 20 );
    	// System.out.println("This statement is always executed.");
    }
}
