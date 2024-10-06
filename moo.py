from fsrs import FSRS, Card, Rating, ReviewLog, State
from datetime import datetime, timezone
import sys
import json
from uuid import uuid4
from getkey import getkey, keys


class MooState:
    def __init__(self):
        self.cards = []
        self.config = {
            "retention_goal": 0.9,
            "show_due_time": False,
        }
        self.reviews = {}
        self.cards_state = {}


    def load(self):
        with open("data/cards.json") as file:
            self.cards = json.load(file)
        with open("data/config.json") as file:
            self.config = json.load(file)
        with open("data/reviews.json") as file:
            reviews_json = json.load(file)
            self.reviews = {}
            for card_id in reviews_json.keys():
                self.reviews[card_id] = [ReviewLog.from_dict(review_log) for review_log in reviews_json[card_id]]
        with open("data/cards_state.json") as file:
            cards_state_json = json.load(file)
            self.cards_state = {}
            for card_id in cards_state_json.keys():
                self.cards_state[card_id] = Card.from_dict(cards_state_json[card_id])


    def save(self):
        with open("data/cards.json", "w") as file:
            json.dump(self.cards, file)
        with open("data/config.json", "w") as file:
            json.dump(self.config, file)
        with open("data/reviews.json", "w") as file:
            reviews_json = {card_id: [review_log.to_dict() for review_log in self.reviews[card_id]] for card_id in self.reviews.keys()}
            json.dump(reviews_json, file)
        with open("data/cards_state.json", "w") as file:
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


def practice(f, state, cards_to_practice):
    past_due = False

    for card in cards_to_practice:
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
        getkey()
        

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

        rating = getkey()
        if rating == "1":
            rating = Rating.Again
        elif rating == "2":
            rating = Rating.Hard
        elif rating == "3":
            rating = Rating.Good
        elif rating == "4":
            rating = Rating.Easy
        else:
            rating = Rating.Good

        new_card_state, review_log = f.review_card(card_state, rating)
        state.cards_state[card["id"]] = new_card_state
        if card["id"] not in state.reviews:
            state.reviews[card["id"]] = []
        state.reviews[card["id"]].append(review_log)
        state.save()

        print()
        print()
        print()
        print()
        print()


def learn(f, state):
    cards_to_learn = list(filter(lambda card: state.cards_state[card["id"]].state == State.New, state.cards))
    cards_to_learn.sort(key=lambda card: state.cards_state[card["id"]].due)
    practice(f, state, cards_to_learn)


def study(f, state):
    cards_to_study = list(filter(lambda card: state.cards_state[card["id"]].state != State.New, state.cards))
    cards_to_study.sort(key=lambda card: state.cards_state[card["id"]].due)
    practice(f, state, cards_to_study)


if __name__ == "__main__":
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
        print("Deng...")
    else:
        print("Moo")
