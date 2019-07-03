import random
import socket
import threading
import time
from tkinter import *


class Server:

    def __init__(self, hostIP, port, maxListen, gameMaster):

        self.game = gameMaster
        self.alleNamen = []
        self.maxPlayer = maxListen

        self.ip = str(hostIP)
        self.port = int(port)

        print("Server startet...")
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(self.maxPlayer)

        self.clientWaitingThread = threading.Thread(target=self.waitForClients, args=()).start()

    def waitForClients(self):
        self.clients = []
        print("Server wartet auf Verbindungen...")
        while True:
            client, addr = self.sock.accept()
            print(f"Verbunden mit {addr}")
            if client not in self.clients:
                self.clients.append(client)
            self.receivingFromClientThread = threading.Thread(target=self.receivingFromClient, args=(client,)).start()

            if len(self.clients) == self.maxPlayer:
                time.sleep(2)
                self.game.newGame(self.alleNamen)   # Alle Spieler sind da ,Spiel startet

    def receivingFromClient(self, client):

        while True:
            data = client.recv(1024).decode()

            if data.split(":")[0] == "name":
                self.alleNamen.append(data.split(":")[1])
                for c in self.clients:
                    c.sendall(f'{data.split(":")[1]} spielt mit!'.encode())


class Client:

    def connect(self, hostIP, port):
        try:
            self.ip = str(hostIP)
            self.port = int(port)

            print("Client startet...")
            self.sock = socket.socket()
            self.sock.connect((self.ip, self.port))

            self.receivingThread = threading.Thread(target=self.receiving, args=()).start()
        except:
            print("Ungültige Verbindung")

    def receiving(self):
        while True:
            data = self.sock.recv(1024)
            data = str(data.decode())
            print(data)


class Spieler(Client):

    def __init__(self, name):
        self.name = name
        self.money = 5000  # Startkapital
        self.position = 0  # Startposition
        self.property = []  # Liste der Grundstücke in Besitz

    def changeMoney(self, value):
        self.money += value  # Änderung des Kapitals

    def walk(self, value):
        newPosition = (self.position + value) % 40  # Änderung der Position auf dem Spielfeld

        if newPosition < self.position:  # Bei Passierung des LOS-Feldes wird dem Spieler Geld hinzugefügt
            self.changeMoney(2000)

        self.position = newPosition

    def setPosition(self, newPosition):
        if newPosition < self.position:  # Bei Passierung des LOS-Feldes wird dem Spieler Geld hinzugefügt
            self.changeMoney(2000)

        self.position = newPosition

    def gotoPrison(self):
        self.position = 10


class Master:

    def __init__(self):
        self.main = Tk()
        self.main.title("Monopoly")
        self.main.geometry("700x700")
        self.main.resizable(0, 0)

        self.bg_image = PhotoImage(file="board.png")
        self.bg_label = Label(self.main, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relheight=1, relwidth=1)

    def newGame(self, spieler):
        self.alleSpielerNamen = [x for x in spieler]
        self.alleSpielerObjekte = {}
        self.anzahlSpieler = len(self.alleSpielerNamen)
        self.spielerAmZug = 0

        print(f"Das Spiel started mit {', '.join(self.alleSpielerNamen)}")

        for name in spieler:
            self.alleSpielerObjekte[name] = Spieler(name)  # Für jeden Spieler wird ein neues
            # SPIELER Objekt angelegt und in einem dictionary gespeichert


class Launcher:

    def __init__(self):

        while True:
            serverClient = str(input("[H]ost / [J]oin: ")).upper()
            if serverClient in ["H", "J"]:
                break
            else:
                print("Ungültige Wahl!\n")

        while True:
            name = str(input("Dein Name: ")).strip()
            if len(name) > 0:
                break
            else:
                print("Ungültige Eingabe!\n")

        if serverClient == "H":
            while True:
                try:
                    maxPlayer = int(input("Spieleranzahl (2-8): "))
                except:
                    print("Ungültige Eingabe")
                finally:
                    if maxPlayer not in range(2, 9):
                        print("Ungültige Eingabe")
                    else:
                        break

            self.gameMaster = Master()
            server = Server("127.0.0.1", 5000, maxPlayer, self.gameMaster)
            time.sleep(2)
            spieler = Spieler(name)
            spieler.connect("127.0.0.1", 5000)



        else:
            while True:
                ip = str(input("Host IP: "))
                try:
                    spieler = Spieler(name)
                    spieler.connect(ip, 5000)
                    break
                except:
                    print("Das hat nicht geklappt!")

            self.gameMaster = Master()

        spieler.sock.send(f"name:{name}".encode())

        self.gameMaster.main.mainloop()


if __name__ == "__main__":
    l = Launcher()
