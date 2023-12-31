import random
import socket
import time

cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def main():
    deck = [] + cards * 4
    random.shuffle(deck)

    sock = socket.socket()
    sock.bind(('', 9090))
    sock.listen()

    players = lobby(sock)
    first_turn = start_game(players, deck)

    loop(first_turn, players, deck)

    win(players)


def start_game(players, deck):

    for player in players:
        player["deck"] = make_deck(deck)
        player_deck = ", ".join(player["deck"])

    return random.randint(0, 1)


def make_deck(deck):
    result = []
    for i in range(8):
        result.append(deck.pop())
    return result


def count_cards(deck):
    count = {}
    for card in deck:
        try:
            if (count[card] != None):
                count[card] += 1
        except:
            count[card] = 1
    return count


def loop(first_turn, players, deck):
    current_turn = first_turn
    while True:
        print(players)
        time.sleep(1)

        current_player = players[current_turn]
        second_player = players[current_turn ^ 1]

        current_player_deck = ", ".join(current_player["deck"])
        second_player_deck = ", ".join(second_player["deck"])

        send_message(current_player, f"Your cards: {current_player_deck}")
        send_message(second_player, f"Your cards: {second_player_deck}")

        if (not len(deck)):
            send_message(current_player, "The deck is empty, game has ended!")
            send_message(second_player, "The deck is empty, game has ended!")
            break

        send_message(current_player, f"Your turn!")

        chosen_card = recive_message(current_player)

        send_message(current_player, f"You have chosen: {chosen_card}")
        send_message(second_player, f"Opponent have chosen: {chosen_card}")

        if (chosen_card not in current_player["deck"]):
            send_message(current_player, "Choose card that you have!")
            continue

        success = chosen_card in second_player["deck"]

        if (success):
            current_player_cards_count = count_cards(current_player["deck"])
            second_player_cards_count = count_cards(second_player["deck"])
            second_player["deck"] = filter_array(
                second_player["deck"], chosen_card)
            current_player["deck"] = current_player["deck"] + \
                [chosen_card for _ in range(
                    second_player_cards_count[chosen_card])]

            current_player_deck = ", ".join(current_player["deck"])
            second_player_deck = ", ".join(second_player["deck"])
            send_message(
                current_player, f"You got cards: +{second_player_cards_count[chosen_card]} of {chosen_card}")
            send_message(
                second_player, f"You lost cards: -{second_player_cards_count[chosen_card]} of {chosen_card}")

        else:
            send_message(current_player,
                         f"You missed... Waiting for opponent...")
            send_message(
                second_player, f"Opponent have missed! Now its your turn!")
            current_turn ^= 1
            current_player["deck"].append(deck.pop())

        chests = check_for_chests(current_player["deck"])

        time.sleep(1)

        if (len(chests)):
            for chest in chests:
                current_player["chests"] += 1
                send_message(current_player,
                             f"You got chest: {chest}")
                send_message(second_player,
                             f"Opponent got chest...")
                current_player["deck"] = filter_array(
                    current_player["deck"], chest)


def win(players):
    first_player = players[0]
    second_player = players[1]
    if (first_player["chests"] > second_player["chests"]):
        send_message(first_player, f"You won")
        send_message(second_player, f"You lose")
    else:
        send_message(second_player, f"You won")
        send_message(first_player, f"You lose")


def check_for_chests(deck):
    result = []
    cards_count = count_cards(deck)
    for card_count in cards_count.keys():
        if (cards_count[card_count] == 4):
            result.append(card_count)

    return result


def send_message(player, message):
    player["conn"].send(message.encode())


def recive_message(player):
    return player["conn"].recv(1024).decode("utf-8")


def filter_array(array, element):
    result = []
    for item in array:
        if (str(item) != str(element)):
            result.append(item)
    return result


def lobby(sock):
    players = []

    while True:
        conn, addr = sock.accept()
        data = conn.recv(1024)
        player_name = data.decode("utf-8")
        players.append({
            "name": player_name,
            "conn": conn,
            "deck": [],
            "chests": 0
        })
        if (len(players) == 1):
            send_message(
                players[0], f"Connected: {player_name}, waiting for second player...")
        else:
            first_player_name = players[0]["name"]
            send_message(
                players[1], f"Your opponent is {first_player_name}, starting game...")
        if (len(players) == 2):
            break

    return players


if __name__ == "__main__":
    main()
