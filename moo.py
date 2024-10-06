from fsrs import FSRS, Card, Rating, ReviewLog, State
from datetime import datetime, timezone
import sys
import json
from uuid import uuid4
from getkey import getkey
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))

class MooState:
    def __init__(self):
        self.cards = []
        self.config = {
            "retention_goal": 0.9,
            "show_due_time": False,
            "data_path": dir_path + "/data",
        }
        self.reviews = {}
        self.cards_state = {}
        self.load_config()


    def load_config(self):
        with open(dir_path + "/config.json") as file:
            self.config = self.config.update(json.load(file))


    def load(self):
        path = self.config["data_path"]
        with open(path + "/cards.json") as file:
            self.cards = json.load(file)
        with open(path + "/reviews.json") as file:
            reviews_json = json.load(file)
            self.reviews = {}
            for card_id in reviews_json.keys():
                self.reviews[card_id] = [ReviewLog.from_dict(review_log) for review_log in reviews_json[card_id]]
        with open(path + "/cards_state.json") as file:
            cards_state_json = json.load(file)
            self.cards_state = {}
            for card_id in cards_state_json.keys():
                self.cards_state[card_id] = Card.from_dict(cards_state_json[card_id])


    def save(self):
        path = self.config["data_path"]
        with open(path + "/cards.json", "w") as file:
            json.dump(self.cards, file)
        with open(path + "/reviews.json", "w") as file:
            reviews_json = {card_id: [review_log.to_dict() for review_log in self.reviews[card_id]] for card_id in self.reviews.keys()}
            json.dump(reviews_json, file)
        with open(path + "/cards_state.json", "w") as file:
            cards_state_json = {card_id: self.cards_state[card_id].to_dict() for card_id in self.cards_state.keys()}
            json.dump(cards_state_json, file)


    def __str__(self):
        return f"State(cards={self.cards}, config={self.config}, reviews={self.reviews}, cards_state={self.cards_state})"


def add_card(state, front, back):
    id = str(uuid4())
    card = {
        "id": id,
        "front": front,
        "back": back,
    }
    state.cards.append(card)
    state.cards_state[id] = Card()
    state.save()


def minutes(interval, rating):
  return ((interval[rating].card.due - datetime.now(timezone.utc)).seconds + 1) // 60


def humanize_interval(interval, rating):
    mins = minutes(interval, rating)
    if mins < 60:
        return f"{mins} minutes"
    else:
        hours = mins // 60
        mins = mins % 60
        return f"{hours} hours"


def num_to_rating(num):
    if num == 1:
        return Rating.Again
    elif num == 2:
        return Rating.Hard
    elif num == 3:
        return Rating.Good
    elif num == 4:
        return Rating.Easy
    else:
        return Rating.Good


def practice(f, state, cards_to_practice):
    past_due = False

    for i, card in enumerate(cards_to_practice):
        card_state = state.cards_state[card["id"]]
        now = datetime.now(timezone.utc)

        if card_state.due > now and not past_due:
            print(f"Ran out of due cards. Showing cards due in future...")
            print()
            past_due = True
        
        if state.config["show_due_time"]:
            if card_state.due > now:
                print(f"Due in {(card_state.due - now).seconds // 60} minutes")
                print()
            else:
                print(f"Was due {(now - card_state.due).seconds // 60} minutes ago")
                print()

        print("========================================")
        print(card["front"])
        print("========================================")
        getkey() # ignore input; any key continues

        next_interval_info = f.repeat(card_state)
        intervals = {
            Rating.Again: humanize_interval(next_interval_info, Rating.Again),
            Rating.Hard: humanize_interval(next_interval_info, Rating.Hard),
            Rating.Good: humanize_interval(next_interval_info, Rating.Good),
            Rating.Easy: humanize_interval(next_interval_info, Rating.Easy),
        }

        print()
        print(f"1 - again ({intervals[Rating.Again]})")
        print(f"2 - hard ({intervals[Rating.Hard]})")
        print(f"3 - good ({intervals[Rating.Good]})")
        print(f"4 - easy ({intervals[Rating.Easy]})")
        print()

        print("========================================")
        print(card["front"])
        print("========================================")
        print(card["back"])
        print("========================================")

        rating = num_to_rating(getkey())

        new_card_state, review_log = f.review_card(card_state, rating)
        id = card["id"]
        state.cards_state[id] = new_card_state
        if id not in state.reviews:
            state.reviews[id] = []
        state.reviews[id].append(review_log)
        state.save()

        if i < len(cards_to_practice) - 1:
            for _ in range(5):
                print()


def learn(f, state):
    cards_to_learn = list(filter(lambda card: state.cards_state[card["id"]].state == State.New, state.cards))
    cards_to_learn.sort(key=lambda card: state.cards_state[card["id"]].due)
    practice(f, state, cards_to_learn)


def study(f, state):
    cards_to_study = list(filter(lambda card: state.cards_state[card["id"]].state != State.New, state.cards))
    cards_to_study.sort(key=lambda card: state.cards_state[card["id"]].due)
    practice(f, state, cards_to_study)


hippo = """
  .-''''-. _    
 ('    '  '0)-/)
 '..____..:    \\._
   \\u  u (        '-..------._
   |     /      :   '.        '--.
  .nn_nn/ (      :   '            '\\
 ( '' '' /      ;     .             \\
  ''----' "\\          :            : '.
         .'/                           '.
        / /                             '.
       /_|       )                     .\\|
         |      /\\                     . '
         '--.__|  '--._  ,            /
                      /'-,          .'
                     /   |        _.' 
                snd (____\\       /    
                          \\      \\    
                           '-'-'-' 
Art credit: Shanaka Dias, http://www.ascii-art.de/ascii/ghi/hippo.txt
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: moo [learn|study|add|deng|wipe] <args>")
        print("e.g. moo add 'front' 'back'")
        print(hippo)
        sys.exit(0)

    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "wipe":
        state = MooState()
        state.save()
        sys.exit(0)

    state = MooState()
    state.load()
    f = FSRS(request_retention = state.config["retention_goal"])

    if command == "learn":
        learn(f, state)
    elif command == "study":
        study(f, state)
    elif command == "add":
        front = args[0]
        back = args[1]
        add_card(state, front, back)
    elif command == "deng":
        print(hippo)
    else:
        print("Moo")
