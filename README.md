# moo-deng

Simple, cute command line spaced repetition system

# Setup

1. Clone the repo
2. Create a data dir, and update "data_path" in config.json to match it.
3. Run the following in the data directory (optional, gives you a git backup + nice diffs)

```
git init
yarn init
yarn add prettier
```

4. Then add these to your bashrc:

```
moo() {
        source ./path/to/venv/bin/activate
        python3 ./moo.py "$1" "$2" "$3"
}

moosave() {
        cd $HOME/c/moo-deng-data # Replace with your data directory (matching config.json)
        # Need to run `yarn init` and `yarn add prettier` in the data dir first
        yarn prettier . --write
        # Need to run `git init` in the data dir first
        git add .
        git commit -m "."
        git push
}
```

# Commands

## moo add "front" "back"

Adds a new card.

## moo learn

Learn new cards.

## moo study

Revise learned cards.

## moo deng

Show a cute ASCII hippo.

# About

Based on the state-of-the-art [FSRS-5 algorithm](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm). This is a ~30% efficiency improvement over the SM-2 algorithm which is the Anki default.

## Why not Anki?

- Anki's default algorithm is less efficient for memorizing things (but you can improve this with the [FSRS](https://github.com/open-spaced-repetition/fsrs4anki) plugin)
- I'm not allowed to use Anki on my work laptop because of the copyleft GNU AGPL license 🙃
- [Mochi](https://mochi.cards) is a decent alternative but it only allows pass/fail and therefore uses a simpler, less efficient spacing algorithm
- I mainly use SRS for text so a CLI is a good fit
- I wanted to make this :)

## Why not add \<x feature\>?

Where \<x\> is tags, multiple decks, searching the deck, etc?

Because this was a weekend project and I wanted to keep it as simple as possible :)

Also I believe that searching the deck, deleting cards, synching between devices etc with full flexibility can be happily left to generalized systems, like text editors. If you're using this CLI you're probably pretty tech savvy and know how to use `grep` or VSCode or something to search your deck. All the card and config data is just JSON - you can put it in a git repo, rsync it, put it in a Dropbox, etc.

## Wait so what does this software even do then?

- Sorts your cards to give you the one you're most likely to forget first, based off a [sophisticated ML algorithm built on years of research](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm)
- Lets you decide what probability of recall you want to aim for (default is 90% which is a good balance between learning lots of new cards but not forgetting everything)
- Handles all the maths behind this as well as persisting all the card data to/from a file (originally I planned on doing this myself but it turns out there's a [python library](https://github.com/open-spaced-repetition/py-fsrs) that gets us most of the way there already)
- Exposes everything via a super simple CLI

## How does the algorithm work?

See https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm for the details. Briefly:

- Model human memory as a "forgetting curve"
- Aim to show you cards just before you forget them
- Fit each card to a model corresponding to memory stability (= estimated number of days for recall to drop from 100% to 90%), intrinsic difficulty (= unitless value from 1-10 corresponding to how hard a card is to learn; some cards are harder than others), and recall probability (derived from stability and days since last shown)
- Factor in your feedback on each card flip (again, hard, good, easy) to update the stability and difficulty values each time
- Show you the cards you're most likely to be on the cusp of forgetting based on the recall probability

# Usage advice

Make smaller cards! See this HN comment: https://news.ycombinator.com/item?id=39002138

Don't be afraid to try to learn complex things with SRS - it's not just for rote memorization of foreign language vocabulary or medical terms like some believe. You can use it to help with understanding [mathematics](https://cognitivemedium.com/srs-mathematics), [research papers](https://augmentingcognition.com/ltm.html), [programming languages](https://sive.rs/srs), etc. I've personally used it for building a knowledge foundation in computability theory, remembering advanced Bash commands, and understanding the swathe of internal tools in my workplace and the relationships between them.

# Limitations

Currently the algorithm just uses the default params (which are determined from the model pre-trained on 200 million+ review logs), and doesn't self optimize over the user's own review history. This is still an improvement over SM-2, but the obvious next step would be to implement this optimization.
