# 2D-Project-2---Battle-Ships
 2nd project for 2D Game Design. Nautical rendition of the classic "Battle Tanks" genre.
 
 Project Written by:\
 Huy Le and Brenner Campos


Objective:\
This game is a person vs. person (PVP) style game where two players will battle each other. There will be\
three rounds of game play and for each round, each player will have five lives. If a player loses all three\
lives, then the other player will gain one point. The winner will have the most wins between three rounds\
of game play.

Controls:

Player:\
            UP KEY              move up\
            DOWN KEY            move down\
            LEFT KEY            move left\
            RIGHT KEY           move right\
            S KEY               rotate cannon counter-clockwise\
            W KEY               rotate cannon clockwise\
            F KEY               shoot in direction of the facing direction of ship\
            SPACE KEY           shoot in the direction of the cannon

This game has been programmed for local wireless multiplayer. To do so:\
    Open Server.py to get the server's IP Address and Port number.\
    Run Client2.py to connect to the server\
        At this point, you cannot play the game until a second client has connected\
        with another machine, run the same client2.py and enter the IP address and port number\
    Once two clients have been connected, the game is able to play.\

Not completed:\
    Game ender - end the game after completion of the third map\
    Items - items were not handled, will pop up locally but have no effect\
    Whirlpools - not implemented\

Completed:\
    Barrels - moveable sprite to use as a shield or strategy\
    Shooting and adjust lives accordingly\
    Switching level maps\
    Collision detection\