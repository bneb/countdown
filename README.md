# Countdown Solver

###### This repo contains solutions to the game-show ["Countdown"](https://en.wikipedia.org/wiki/Countdown_(game_show)#Numbers_round).

Solutions are aimed at using very few imports, and no classes.

Avoiding classes (eschewing binary trees for modeling nested operations), led
to significant performance increases anecdotally.

Using few imports just provides a better challenge (as does using primitives).

---

## Numbers

The numbers game is easily apprehended:
Construct a target number from any subset of six numbers using only arithmetic operations
  - addition
  - subtraction
  - multiplicatios
  - integer division (no fractions)

The target number is a three digit number.
The numbers used to compute the target can comprise
  - Zero to four 'big' numbers {25, 50, 75, 100}
  - The rest 'small' numbers, 0-10

### Example Output

```
$ python solve_countdown.py
Enter numbers (1 2 ...): 3 4 5 6 7 75
Enter the target: 955

Target:  955

Numbers: [3, 4, 5, 6, 7, 75]

  ######################################
  ###            SOLVED!             ###
  ###  (75 * (6 + 7) - 4 * 5) = 955  ###
  ###          Time: 0.30s           ###
  ######################################

```

---

## Letters

###### TODO: Hopefully I get to this soon!
