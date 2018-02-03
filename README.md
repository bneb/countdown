# Countdown Solver

###### This repo contains solutions to the game-show ["Countdown"](https://en.wikipedia.org/wiki/Countdown_(game_show)#Numbers_round).

---

# Numbers

The numbers game is easily apprehended:
Construct a target number from any subset of six numbers using only arithmetic operations
  - addition
  - subtraction
  - multiplicatios
  - even division (no fractions)

The target number is a three digit number.
The numbers used to compute the target can comprise
  - Zero to four 'big' numbers {25, 50, 75, 100}
  - The rest 'small' numbers, 0-10

### Example Output

```
$ python solve_countdown.py numbers
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

### Implementation

The algorithm is a brute force.

All operations are pairwise.

Because subtraction and division are flipped when necessary, order of pairs is irrelevant.

The arithmetic operations should be modeled as non-leaf tree nodes.

For example:
```
    ( + )
   /     \
 ( 3 )  ( - )
       /     \
      2       4
```

Should produce 1, because `3 + (2 - 4) = 1`.

This can be done using a tree structure, but the overhead caused significant slowdown.

The recursive approach is well documented in the code, and offers good performance.

---

# Letters

With nine letters, create the longest English language word you can.

### Implementation

The implementation details for the letters round are much less interesting.

A word list is taken from `NLTK.brown.words()`.

Each word has its letter frequencies computed.

Each unique letter frequency is inserted into a SQLite database table.

We avoid duplication, because the rules of the game only care about word length.

This means that "prose" scores just as well as "spore". Let's assume "prose" is examined first.

Then the following record is inserted into the db:
```
(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0,  prose,  5  )

```

During the letters round, a list of letters is entered: 'A V G Q U I W R T'

Then a query will pull back the longest acceptable word:

```
SELECT
  word
FROM
  words
WHERE
  a <= 1
AND
  b <= 0
...
ORDER BY
  length DESC
LIMIT 1

```

The above query will filter to words that have at most the frequency of each letter of the given list of letters.

### Example Output

```
Enter the letters ('a b ...'): a v g q u i w r t

  Letters: A V G Q U I W R T

  We found 'guitar' for 6 points!
  Time: 0.01 seconds.

```
