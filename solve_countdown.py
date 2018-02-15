""" This file contains functions to solve the countdown numbers game.
    The game follows simple rules. Given a target value and six numbers,
    use arithmetic operations to calculate the target. You do not need
    to use all the numbers. Numbers are either small {1 to 10} or large
    {25, 50, 75, 100}.

Example:
    $ python solve_countdown.py

    Enter numbers (1 2 ...): 50 75 25 100 8 9
    Enter the target: 981

    Target:  981

    Numbers: [100, 50, 75, 25, 8, 9]

      ################################################
      ###                 SOLVED!                  ###
      ###  (75 + (8 + (100 * 9 - 50 / 25))) = 981  ###
      ###               Time: 0.91s                ###
      ################################################

"""
from collections import Counter
from itertools import combinations
from random import randint, sample
from string import ascii_lowercase
from time import time
import bz2
import os
import re
import sqlite3
import sys

ZEROS = dict.fromkeys(ascii_lowercase, 0)
DB_PATH = ".countdown_words.db"


def _blue(s):
    """ Get a string that when printed, is blue.
    """
    return "\033[94m" + s + "\033[0m"


def _red(s):
    """ Get a string that when printed, is red.
    """
    return "\033[93m" + s + "\033[0m"


def get_target():
    """ Get a random number between 300 and 1000 inclusive.
    """
    return randint(300, 1000)


def get_numbers():
    """ Get six numbers from which to calculate the target (or get close)
    """
    n = randint(1,4)
    return sample([25, 50, 75, 100], n) + [randint(1,10) for _ in range(6-n)]


def numbers(ns=None, t=None):
    """ This function solves the numbers round of Countdown.

    This method will calculate all possible values that can be produced by
    applying arithmetic operations (+, -, * //) to six given numbers.

    Args:
        ns, the numbers with which to calculate all possible values.
        t, the target value

    Returns:
        Nothing, it just prints some output with operations to get as close as
        possible to the target value.
    """
    if not ns:
        ns = prompt_numbers()
    if not t:
        t = prompt_target()

    print("\nTarget:  {}".format(t))
    print("\nNumbers: {}\n".format(ns))

    length, solution, is_solved, seconds = solve(ns, t)
    outcome = _blue("SOLVED!") if is_solved else _red("Close!")

    print("  " + "#" * (length + 10))
    print("  ###  {:^{length}}  ###".format(outcome,  length=length+9))
    print("  ###  {:^{length}}  ###".format(solution, length=length))
    print("  ###  {:^{length}}  ###".format(seconds,  length=length))
    print("  " + "#" * (length + 10) + "\n")


def solve(ns, t):
    """ Return the calculation and metadata for the one closest to the target.

    Args:
        ns, the numbers with which to calculate all possible values.
        t, the target value

    Returns:
        A typle of
        - length of solution
        - solution calculation string representation
        - whether or not it is exactly the target
        - the time in seconds it took to calculate
    """
    t0 = time()
    closest = ("0", 1, abs(t))

    for (v, s) in all_values(ns):
        diff = abs(t-v)

        if diff == 0:
            solution = "{} = {}".format(s, v)
            seconds = "Time: {:.2f}s".format(time()-t0)
            return (len(solution), solution, True, seconds)

        elif diff < closest[2]:
            closest = (s, v, diff)

    solution = "{} = {}, {} away from {}".format(*closest, t)
    seconds = "Time: {:.2f}s".format(time()-t0)

    return (len(solution), solution, False, seconds)


def all_values(ns):
    """ Generate all possible values from the number list.

    This function will iterate through all comprised complementary groups and
    all possible values produced from those groups, yielding each value.

    Args:
        ns, the list of numbers.

    Yields:
        Every possible value generated from the number list.
    """
    for cs in all_subgroups(ns):
        for v in arithmetic_values(cs):
            yield v


def arithmetic_values(ns):
    """ Generate all different arithmetic values.

    This generator produces all the different values for the provided numbers.

    Args:
        ns, the numbers

    Yields:
        If ns is just one number, then the (number, number_str).
        Else, the different pairwise arithmetic values (only integer division).

    Example:
        arithmetic_values((1,))
            (1, '1')

        arithmetic_values((1, 1))
            (2, '1+1'), (1, '1*1'), (0, '1-1'), (1, '1/1')

        arithmetic_values((1, 2))
            (3, '1+1'), (2, '1*2'), (-1, '1-2'), (1, '2-1'), (2, '2/1')

        arithmetic_values((2, 3))
            (5, '2+3'), (6, '2*3'), (-1, '2-3'), (1, '3-2') # no even division

        arithmetic_values(((2, '2'), (3, '1 + 2')))
            ( 5, '2 + (1 + 2)'),
            ( 6, '2 * (1 + 2)'),
            (-1, '2 - (1 + 2)'),
            ( 1, '(1 + 2) - 2')
            # no even division
    """

    if type(ns) == int:
        yield (ns, str(ns))

    elif len(ns) == 1:
        yield (ns[0], str(ns[0]))

    elif len(ns) == 2:
        for (n0, n0_str) in arithmetic_values(ns[0]):
            for (n1, n1_str) in arithmetic_values(ns[1]):
                yield (n0 + n1, "({} + {})".format(n0_str, n1_str))
                yield (n0 * n1, "{} * {}".format(n0_str, n1_str))

                if n0 == n1:
                    yield (0, "({} - {})".format(n0_str, n1_str))

                    if n0 != 0:
                        yield (1, "{} / {}".format(n0_str, n1_str))

                else:
                    yield (n0 - n1, "({} - {})".format(n0_str, n1_str))
                    yield (n1 - n0, "({} - {})".format(n1_str, n0_str))

                    if n1 != 0 and n0 % n1 == 0:
                        yield (n0 // n1, "{} / {}".format(n0_str, n1_str))

                    elif n0 != 0 and n1 % n0 == 0:
                        yield (n1 // n0, "{} / {}".format(n1_str, n0_str))


def all_subgroups(ns):
    """ Generate all possible subgroups from the given numbers.

    This does not include the null group, nor the group itself :)

    Args:
        ns, the numbers.

    Yields:
        Each complementary groups that make up the given numbers.

    Example:
        all_subgroups((1, 2, 3))
            (1,),
            (2, 3),
            ((1,), (2, 3))
            (2,),
            (1, 3),
            ((2,), (1, 3))
            (3,),
            (1, 2),
            ((3,), (1, 2))
    """
    if len(ns) <= 2:
        yield ns

    else:
        for i in range(1, (len(ns)+1)//2):

            for lcs in combinations(ns, i):
                remaining_numbers = [x for x in list(ns) if x not in lcs]

                for rcs in combinations(tuple(remaining_numbers), len(ns)-i):

                    for ls in all_subgroups(lcs):
                        yield ls

                        for rs in all_subgroups(rcs):
                            yield rs

                            yield (ls, rs)


def run_numbers():
    """ Run 20 numbers rounds.
    """
    for _ in range(20): numbers(get_numbers(), get_target()); print("-"*80);


def prompt_numbers():
    """ Prompt the user for numbers.
    """
    return [int(x) for x in input("Enter numbers (1 2 ...): ").split()]


def prompt_target():
    """ Prompt the user for the target.
    """
    return int(input("Enter the target: "))


def run_letters(n=20):
    """ Run 20 letters rounds.
    """
    for _ in range(n): letters(get_letters()); print("-" * 80)


def get_letters():
    """ Get 7 random letters and two additional random vowels.
    """
    return ''.join(sample(ascii_lowercase * 3, 7) + sample("aeiou", 2))


def get_each_word():
    """ Get a generator for each word in the compressed word list.
    """
    with bz2.open(".word_list.txt.bz2", "rt") as f:
        return (w.strip() for w in f.readlines())


def get_unique_frequencies():
    """ Get a single word for each unique letter frequencies.
    """
    letter_frequency_map = {}
    for w in get_each_word():
        frequencies = [f for (_, f) in sorted({**ZEROS, **Counter(w)}.items())]
        letter_frequency_map[tuple(frequencies)] = w

    return tuple(letter_frequency_map.items())


def connect():
    """ Get a connection to the SQLite database.
    """
    return sqlite3.connect(DB_PATH)


def get_create_query():
    """ Get the create table query string.
    """
    create_str = "CREATE TABLE words ("
    for l in ascii_lowercase: create_str += "{} integer, ".format(l)
    create_str += "word text, length integer)"

    return create_str


def get_insert_query():
    """ Get the insert into table query string.
    """
    return "INSERT INTO words VALUES ({})".format(", ".join("?" * 28))


def get_insert_vals():
    """ Get all (frequencies, word, word length) records to insert.
    """
    return [(*fs, w, len(w)) for fs, w in get_unique_frequencies()]


def words_table():
    """ Create and populate the SQLite table if it doesn't exist.
    """
    if not os.path.isfile(DB_PATH):
        c = connect()
        c.execute(get_create_query())
        c.executemany(get_insert_query(), get_insert_vals())
        c.commit()
        c.close()


def get_check_query(chars):
    """ Get the query to find the longest acceptable word.
    """
    query = "SELECT word FROM words WHERE 1 = 1 "
    for (letter, count) in  tuple(sorted({**ZEROS, **Counter(chars)}.items())):
        query += "AND {} <= {} ".format(letter, count)
    query += "ORDER BY length DESC LIMIT 1"

    return query


def check_chars(chars):
    """ Query the SQLite table for the longest acceptable word.
    """
    c = connect()
    t = c.execute(get_check_query(chars)).fetchone()
    c.close()

    if t: return t[0]


def prompt_letters():
    """ Prompt the user for a list of letters to play the letters round.
    """
    letters = input("\nEnter the letters ('a b ...'): ").lower().strip().split()

    if len(letters) == 0: letters = get_letters()
    elif len(letters) < 9: raise Exception("Game requires 9 letters.")

    return letters


def letters(chars):
    """ Solve the letters round of Countdown given an iterable of chars.
    $ python solve_countdown.py letters

    Enter the letters ('a b ...'): n q i a l t j e u

      Letters: N Q I A L T J E U

      We found 'antique' for 7 points!
      Time: 0.01 seconds.

    """
    print("\n  Letters: {}\n".format(" ".join(chars).upper()))

    t0 = time()
    words_table()
    sol = check_chars(chars)

    if sol:
        print("  We found '{}' for {} points!".format(_blue(sol), len(sol)))
    else:
        print(_red("  We didn't find anything... 0 points."))

    print("  Time: {:0.2f} seconds.\n".format(time() - t0))


def prompt_game_type():
    """ Prompt the user until they enter 'numbers' or 'letters'.
    """
    result = ""
    while result.lower() not in ["letters", "numbers"]:
        result = input("Select game type of either 'numbers' or 'letters': ")
    return result


if __name__ == "__main__":
    game_type = prompt_game_type() if len(sys.argv) < 2 else sys.argv[1]

    if game_type == "numbers":
        numbers(prompt_numbers(), prompt_target())

    elif game_type == "letters":
        letters(prompt_letters())
