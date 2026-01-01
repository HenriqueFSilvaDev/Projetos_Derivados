using System;
using System.Collections.Generic;

Random random = new Random();

Console.WriteLine("Would you like to play? (Y/N)");
if (ShouldPlay())
{
    PlayGame();
}

void PlayGame()
{
    var play = true;

    while (play)
    {
        var target;
        var roll;

        Console.WriteLine($"Roll a number greater than {target} to win!");
        Console.WriteLine($"You rolled a {roll}");
        Console.WriteLine(WinOrLose());
        Console.WriteLine("\nPlay again? (Y/N)");

        play = ShouldPlay();
    }
}
/*
Output

Copiar
Would you like to play? (Y/N)
Y
Roll a number greater than 1 to win!
You rolled a 2
You win!

Play again? (Y/N)
Y
Roll a number greater than 4 to win!
You rolled a 6
You win!

Play again? (Y/N)
Y
Roll a number greater than 1 to win!
You rolled a 1
You lose!

Play again? (Y/N)
N
*/

void WinOrLose()
{
    return roll > target ? "You win!" : "You lose!";
}
