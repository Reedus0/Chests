import socket

def main():
    player_name = input("Enter player name: ")
    sock = socket.socket()
    sock.connect(("localhost", 9090))
    sock.send(player_name.encode())

    print(sock.recv(1024).decode("utf-8"))

    while True:
        data = sock.recv(1024).decode("utf-8")
        if data:
            print(data)
        if data[:10] == "Your turn!":
            sock.send(input("Choose card: ").encode())

    sock.close()

if __name__ == "__main__":
    main()