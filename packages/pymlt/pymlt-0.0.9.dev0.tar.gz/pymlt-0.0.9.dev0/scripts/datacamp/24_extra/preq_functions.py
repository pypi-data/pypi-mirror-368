#!/usr/local/bin/python3

# ---------------------------------
# - chapter 1
# ---------------------------------

# create functions

from functools import reduce

from pydataset import data


def namefunction(i):
    """Explain function here"""
    shout_word = i + ", congratulations" + "!!!"
    print(shout_word)


namefunction("hi")


def namefunction(i):
    """Explain function here"""
    shout_word = i + ", congratulations" + "!!!"
    return shout_word  # return vs print


x = namefunction("hi")
print(x)


def namefunction(i, j):  # two input variables
    """Explain function here"""
    new_value = i**j
    return new_value


x = namefunction(2, 3)
print(x)

# tuples
# like a list, but you can't modify values
# constructed using parentheses
# you can unpack a tuples
even_nums = (2, 4, 6)
a, b, c = even_nums
print(a)
print(b)
print(even_nums[0])


def shout_all(w1, w2):  # function with tuples
    """Return a tuple of strings"""
    s1 = w1 + "!!!"
    s2 = w2 + "!!!"
    all = (s1, s2)
    return all


# returns a tuple
print(shout_all("congratulations", "you"))


# create freq table with for loops

mtcars = data("mtcars")

item_count = {}
col = df["cyl"]


for entry in col:
    if entry in item_count.keys():
        item_count[entry] += 1
    else:
        item_count[entry] = 1

print(item_count)


# create freq table with a function

mtcars = data("mtcars")


def count_entries(df, col_name):
    """return a frequency table"""
    items_count = {}
    col = df[col_name]

    for entry in col:
        if entry in items_count.keys():
            items_count[entry] += 1
        else:
            items_count[entry] = 1

    return items_count


print(count_entries(df, "cyl"))


# ---------------------------------
# - chapter 2
# ---------------------------------

# scopes in functions
# - global scope = defined in the main body of script
# - local scope = defined inside the functions
# - built-in scope = predefined by built-in modules
# a function looks first in the local scopen, then global, then built-in


x = 1  # x in global


def change_x():
    global x  # set x as global
    x = 2


print(x)
change_x()
print(x)


# nested functions = two scopes
# function looks first in the inner scope, then the outer scopen
# in sum: LEGB = local scope, Enclosing functions, Global, Built-in


# nested function


def three(x, y, z):
    def inner(i):
        return i**2

    return (inner(x), inner(y), inner(z))


print(three(1, 2, 3))


# closure
# - the  inner function remembers the state of its enclosing scope when called


def echo(n):
    def inner_echo(i):
        echo_n = i * n
        return echo_n

    return inner_echo


toSecond = echo(2)  # set closure
toThird = echo(3)  # set closure

print(toSecond(4), toThird(4))


# set nonlocal


def echo_shout(word):
    echo_word = word * 2
    print(echo_word)

    def shout():
        nonlocal echo_word  # not setting nonlocal gives error
        echo_word = echo_word + "!!!"

    shout()
    print(echo_word)


echo_shout("hello")


# create function with default argument
# - flexible argument = *args or **kwargs


def echo(i, echo=1, up=False):  # function with parameter
    j = str(i) * echo
    if up is True:
        j = j.upper()
    print(j)


echo(1, 4)
echo("hoi", 4, up=True)


# flexible input
def gib(*args):
    for i in args:
        i = i.upper()
        print(i)


gib("luke", "leia", "han", "obi", "darth")


# flexible arguments + flexible input = dictionary
def gib(**kwargs):
    for key, value in kwargs.items():
        print(key + ": " + value)


gib(name="luke", status="missing")


# ---------------------------------
# - chapter 3
# ---------------------------------

# lambda functions - quick and dirty
l1 = lambda x, y: x * y
print(l1(5, 5))

# map function goes over given sequence
seq1 = range(5)
print(list(map(lambda i: i**2, seq1)))  # use list to unpack output

# use lambda function as filter
seq1 = range(15)
print(list(map(lambda i: i > 10, seq1)))  # use list to unpack output


# Import reduce from functools

# Create a list of strings: stark
stark = ["robb", "sansa", "arya", "brandon", "rickon"]

print((lambda item1, item2: item1 + item2, stark))
print(reduce(lambda item1, item2: item1 + item2, stark))  # ?


# error handling


def functionName(x):
    """apply try-except handle"""
    if x < 0:
        raise ValueError("x must be greater than 0")
    try:
        print(x**0.5)
    except:
        print("error: input must be a float")


functionName(-4)
functionName(4)
functionName("hi")


def functionName(x, y):
    """apply try-except handle"""
    if y < 0:
        raise ValueError("x must be greater than 0")
    try:
        print(x**y)
    except:
        print("error")


functionName(9, -5)
