Instructions

You are a fluent speaker of the french language and your task is to correct eventual
typos and spelling errors within a list of words.

You are provided with a list of categories and a list of words. The list of categories denotes
the context which the list of words belong to.

You should output a list that contains the corrections to be done. Each item in the output
list is a list itself composed with two elements. The first element is the word as it was provided
in the list of words; and the second element is the correct spelled version of the same word.

Only output words which contain typos and spelling errors. If there are no errors in the provided list of
words, output an empty list.
-----

Examples

List of categories

Character
Sex
Adjective
-----

List of words

feminin
masculin
-----

[[feminin, féminin]]
