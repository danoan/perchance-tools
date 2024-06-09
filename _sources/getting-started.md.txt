# Getting started with perchance-tools

Collection of tools to write files in the perchance language.

This program contains several scripts to help with the creation
of perchance files. Perchance is a language that facilitates the
generation of natural text in several languages.

The main purpose of this script is to transform a list of words
into perchance data structures. The assumption is that the list of
words was provided from a thesaurus in markdown format.

## Workflow example

### Digitization

The data source should be a markdown file with a structure similar to the one below:

```markdown
# Cinq sens

## Vue

### Verbes

admirer
voir
zieuter

### Noms

agencement
uniformité
vision
visualisation

### Adjectifs

affreux
versicolore
vif
vilain
visible

## Toucher

### Verbes

affleurer
appuyer
attoucher
caresser
```

That is, words are listed inside a hierarchy of categories where they belong to.

If you have this data in a physical or digital book, you can make use of [digital-note](https://github.com/danoan/digital-note) to convert it to text and them make the necessary modifications to put it in the markdown format.

### Convert to perchance-format

The `perchance-tools` comes up with the following scripts:

1. markdown_to_yml
2. correct_words
3. convert_to_perchance_format

We should execute these three scripts in order to obtain a curated perchance data structure.

#### markdown_to_yml

Converts the markdown data in a more structured format. We choose yml because it is similar to the final perchance format.

##### Example

The example markdown data above would be converted to:

```yml
cinq_sens:
    vue:
        verbes:
            words:
            - admirer
            - voir
            - zieuter
        noms:
            words:
            - agencement
            - uniformité
            - vision
            - visualisation
        adjectifs:
            words:
            - affreux
            - versicolore
            - vif
            - vilain
            - visible
    toucher:
        verbes:
            words:
            - affleurer
            - appuyer
            - attoucher
            - caresser
```

#### correct_words

It is common to find errors during the digitization process. That could be a mispelling, a missing diacritic and so on.  This script will find these digitization errors with the help of a LLM prompt and the word categories.

#### convert_to_perchance_format

Finally, this script translates the categories into English and add some tags that can be recovered by a perchance command.

```yml
five_senses
  name=five senses
  sight
    name=sight
    verbs
      name=verbs
      words
        admirer
        voir
        zieuter
    noms
      name=noms
        words
          agencement
          uniformité
          vision
          visualisation
    adjectives
        name=adjectives
            words
              affreux
              versicolore
              vif
              vilain
              visible
    toucher
      name=toucher
        verbs
          name=verbs
            words
              affleurer
              appuyer
              attoucher
              caresser
```


## Contributing

Please reference to our [contribution](http://danoan.github.io/perchance-tools/contributing) and [code-of-conduct](http://danoan.github.io/perchance-tools/code-of-conduct) guideline.
