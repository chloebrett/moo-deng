# moo-deng

Simple, cute command line spaced repetition system

[WIP]

# Commands

## moo add "front" "back"

Adds a new card.

## moo learn

Learn new cards.

## moo study

Revise learned cards.

## moo deng

Show a cute ASCII hippo.

# Installation

Coming soon. I gotta actually build the thing first.

# About

Based on the state-of-the-art [FSRS-5 algorithm](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm). This is a ~30% efficiency improvement over the SM-2 algorithm which is the Anki default.

## Why not Anki?

* Anki's default algorithm is less efficient for memorizing things (but you can improve this with the [FSRS](https://github.com/open-spaced-repetition/fsrs4anki) plugin)
* I'm  not allowed to use Anki on my work laptop because of the copyleft GNU AGPL license 🙃
* [Mochi](https://mochi.cards) is a decent alternative but it only allows pass/fail and therefore uses a simpler, less efficient spacing algorithm
* I mainly use SRS for text so a CLI is a good fit
* I wanted to make this :)

## Why not add \<x feature\>?

Where \<x\> is tags, multiple decks, searching the deck, etc?

Because this was a weekend project and I wanted to keep it as simple as possible :)

Also I believe that searching the deck, deleting cards, synching between devices etc with full flexibility can be happily left to generalized systems, like text editors. If you're using this CLI you're probably pretty tech savvy and know how to use `grep` or VSCode or something to search your deck. All the card and config data is just JSON - you can put it in a git repo, rsync it, put it in a Dropbox, etc.

## Wait so what does this software even do then?

* Sorts your cards to give you the one you're most likely to forget first, based off a [sophisticated ML algorithm built on years of research](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm)
* Lets you decide what probability of recall you want to aim for (default is 90% which is a good balance between learning lots of new cards but not forgetting everything)
* Handles all the maths behind this as well as persisting all the card data to/from a file
* Exposes everything via a super simple CLI

## How does the algorithm work?

See https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm for the details. Briefly:
* Model human memory as a "forgetting curve"
* Aim to show you cards just before you forget them
* Fit each card to a model corresponding to memory stability (estimated number of days for recall to drop from 100% to 90%), intrinsic difficulty (some cards are harder than others), and recall probability (derived from stability + days since last shown)
* Factor in your feedback on each card flip (again, hard, good, easy) to update the stability and difficulty values each time
* Show you the cards you're most likely to be on the cusp of forgetting
