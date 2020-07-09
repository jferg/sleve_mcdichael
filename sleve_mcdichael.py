#!/usr/bin/env python3

import random
import string
from collections import Counter


VOWELS = set('aeiou')
CONSONANTS = set(string.ascii_lowercase) - VOWELS
NEVER_TWINNED_LETTERS = set('ahijkqstuvwxyz')
CONSERVED_2GRAMS = set([
#     'ch',
#     'ck',
#     'fl',  # changing the 'l' would be fine...
#     'ng',  # likewise the 'n'
#     'ph',
#     'qu',
#     'rg',
#     'rt',
#     'sh',
#     'st',
#     'th',
])


def make_name_sampling_distribution(filename):
    lines = (line.strip().split() for line in open(filename))
    names = {name.lower(): int(round((int(count) / 4000)**0.5)) for name, count in lines}
    return list(Counter(names).elements())

first_names = make_name_sampling_distribution('first_name_frequencies.txt')
distinct_first_names = set(first_names)

last_names = make_name_sampling_distribution('last_name_frequencies.txt')
distinct_last_names = set(first_names)

middle_names = first_names + last_names
distinct_middle_names = set(middle_names)
# NOTE it's funny to see first names overrepresented as last names
# last_names = middle_names

letter_counts = Counter(c for name in middle_names for c in name)
letter_distribution = list(letter_counts.elements())


MIDDLE_NAME_FREQUENCY = 0.25
MC_FREQUENCY = 0.1
RETRY_UNCHANGED_NAME_CHANCE = 0.5

N_DISTRIBUTION_PER_LENGTH = {
    1: [0, 1],
    2: [0, 1],
    3: [0, 1],
    4: [0, 1, 1],
    5: [0, 1, 1, 1],
    6: [1],
    7: [1],
    8: [1, 1, 1, 1, 2, 2],
    9: [1, 1, 1, 2, 2],
}
BIG_N_DISTRIBUTION = [1, 2]


def how_many_letters_to_fuck_up(name):
    return random.choice([0, 1]) if len(name) <= 8 else random.choice([0, 1, 2])


def fuck_up_a_letter(c):
    # TODO target letter frequency should depend on letter_counts
    which = VOWELS if (c in VOWELS or c == 'y') else CONSONANTS
    return random.choice(list(which - set(c)))


def in_twinned_letters(name, i):
    return ((i > 0 and name[i-1] == name[i]) or
            (i < len(name)-1 and name[i+1] == name[i]))

def fuck_up_a_single_name(in_name):
    # TODO what about the letter 'q'?
    # should i treat 'qu' as one letter in the original name?
    # should i treat 'qu' as one replacement letter?
    # TODO preserve 'Mc'?
    name = list(in_name)
    n = how_many_letters_to_fuck_up(name)
    for i in random.sample(range(len(name)), n):

        # TODO twinned letters in the original name should potentially be *wholly replaced with one letter*, not just preserved
        if in_twinned_letters(name, i):
            continue

        # preserve 2-grams that look too weird when one letter is changed
        if any(two_gram in (str(name[i-1:i+1]), str(name[i:i+2])) for two_gram in CONSERVED_2GRAMS):
            continue

        # never change an ending 'e'; sometimes it works, usually no
        if i == len(name)-1 and name[i] == 'e':
            continue

        # prevent jarring repeated letters in result, like 'aa' or 'hh'
        name[i] = fuck_up_a_letter(name[i])
        while in_twinned_letters(name, i) and name[i] in NEVER_TWINNED_LETTERS:
            name[i] = fuck_up_a_letter(name[i])

    name = ''.join(name)

    if name != in_name and name in distinct_middle_names:
        return fuck_up_a_single_name(in_name)

    if name == in_name and random.random() <= RETRY_UNCHANGED_NAME_CHANCE:
        return fuck_up_a_single_name(in_name)

    return name


def sleve_mcdichael():
    if random.random() <= MIDDLE_NAME_FREQUENCY:
        name_sets = [first_names, middle_names, last_names]
    else:
        name_sets = [first_names, last_names]
    real_names = [random.choice(names) for names in name_sets]
    fucked_up_names = [fuck_up_a_single_name(name) for name in real_names]
    if real_names == fucked_up_names:
        return sleve_mcdichael()
    fucked_up_names = [name.title() for name in fucked_up_names]
    # sprinkle in weird 'Mc' last names
    if random.random() <= MC_FREQUENCY:
        fucked_up_names[-1] = 'Mc' + fucked_up_names[-1].title()
    return ' '.join(fucked_up_names)


def main():
    while True:
        print(sleve_mcdichael())

if __name__ == '__main__':
    main()
