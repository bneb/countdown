""" This file contains functions to solve the countdown numbers game.
    [link](https://en.wikipedia.org/wiki/Countdown_(game_show)#Numbers_round)
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
from itertools import combinations
from random import randint, sample
from time import time


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
    outcome = ("\033[94mSOLVED!" if is_solved else "\033[93mClose!") + "\033[0m"

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
        for i in range(1, len(ns)//2 + 1):

            for lcs in combinations(ns, i):
                temp = list(ns)
                for x in lcs: temp.remove(x)

                for rcs in combinations(tuple(temp), len(ns)-i):

                    for ls in all_subgroups(lcs):
                        yield ls

                        for rs in all_subgroups(rcs):
                            yield rs

                            yield (ls, rs)


def compare():
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
    int(input("Enter the target: "))

if __name__ == "__main__":
    numbers(prompt_numbers(), prompt_target())
