using System;


public class Program
{
    public static void Main(string[] args)
    {
        string value = "abc123";
        char[] valueArray = value.ToCharArray();
        string newValue = new string(valueArray);
        Array.Reverse(valueArray);
        foreach (var val in valueArray)
        {
            Console.WriteLine(val);
        }

        Console.WriteLine($"New Value: {newValue}   Reversed: {new string(valueArray)} ");
    }
}

