"""Games of probability (Vietnamese: Trò chơi xác suất)

This module provides classes that are used as games of chance and things that based on probability, using the `random` module.

This module could be imported as `gop` or `tcxs`.

Classes: `Coin`, `FiftyTwoCardPack`, `Dice`, `UnoPack`, `Revolver`, `UnoFlipPack`."""

# Classes are sorted by time created

import random

class Coin:
    """A coin. Method: `flip()` — Flips the coin and returns either 'heads' or 'tails'."""
    def __init__(self): self.sides = ['heads', 'tails']
    def flip(self):
        """Flips the coin and returns either 'heads' or 'tails'."""
        return random.choice(self.sides)

class FiftyTwoCardPack:
    """A Standard 52-card pack. Methods:
    - `shuffle()` — Shuffles and returns the pack.
    - `draw()` — Draws and returns a card from the pack."""
    def __init__(self):
        self.pack = ['A♠','2♠','3♠','4♠','5♠','6♠','7♠','8♠','9♠','10♠','J♠','Q♠','K♠',
                     'A♣','2♣','3♣','4♣','5♣','6♣','7♣','8♣','9♣','10♣','J♣','Q♣','K♣',
                     'A♦','2♦','3♦','4♦','5♦','6♦','7♦','8♦','9♦','10♦','J♦','Q♦','K♦',
                     'A♥','2♥','3♥','4♥','5♥','6♥','7♥','8♥','9♥','10♥','J♥','Q♥','K♥']
    def shuffle(self, shuffle_times = 0):
        """Shuffles and returns the pack. Parameter: `shuffle_times` — The number of times the pack will be shuffled."""
        if shuffle_times < 0: raise ValueError("'shuffle_times' parameter must not have a negative value")
        self.shuffle_times = int(shuffle_times)
        self.shuffled_times = 0
        while self.shuffled_times < self.shuffle_times:
            random.shuffle(self.pack)
            self.shuffled_times += 1
        return self.pack
    def draw(self, drawn_card = 0):
        """Draws and returns a card from the pack. Parameter: `drawn_card` — The card which will be returned.
        `drawn_card = 0` will return the top card, `drawn_card = -1` will return the bottom card."""
        self.drawn_card = int(drawn_card)
        return self.pack.pop(self.drawn_card)

class Dice:
    """(A) regular dice. Method: `roll_the_dice()` — Roll the dice and returns the sum of all results.
    
    When used, it rolls the dice, the number of dice is based on the `number_of_dice` parameter,
    and returns the sum of all the results. Parameter:
    - `number_of_dice` — the number of dice that will be used"""
    def __init__(self):
        self.dice_numbers = [1, 2, 3, 4, 5, 6]
    def roll_the_dice(self, number_of_dice = 1):
        """Roll the dice and returns the sum of all results. Parameter: `number_of_dice` — The number of dice that will be used"""
        if number_of_dice < 0: raise ValueError("'number_of_dice' parameter must not have a negative value")
        self.number_of_dice = int(number_of_dice)
        self.all_result = 0
        self.dice_used = 0
        while self.dice_used < self.number_of_dice:
            self.all_result += random.choice(self.dice_numbers)
            self.dice_used += 1
        return self.all_result

class UnoPack:
    """An *UNO* pack. Methods:
    - `shuffle()` — Shuffles and returns the pack.
    - `draw()` — Draws and returns a card from the pack.

    The order of the cards is based on https://commons.wikimedia.org/wiki/File:UNO_cards_deck.svg."""

    def __init__(self):
        self.pack = ['Red 0','Red 1','Red 2','Red 3','Red 4','Red 5','Red 6','Red 7','Red 8','Red 9','Red Skip','Red Reverse',
                         'Red Draw 2','Wild',
                     'Yellow 0','Yellow 1','Yellow 2','Yellow 3','Yellow 4','Yellow 5','Yellow 6','Yellow 7','Yellow 8','Yellow 9',
                         'Yellow Skip','Yellow Reverse','Yellow Draw 2','Wild',
                     'Green 0','Green 1','Green 2','Green 3','Green 4','Green 5','Green 6','Green 7','Green 8','Green 9','Green Skip',
                         'Green Reverse','Green Draw 2','Wild',
                     'Blue 0','Blue 1','Blue 2','Blue 3','Blue 4','Blue 5','Blue 6','Blue 7','Blue 8','Blue 9','Blue Skip',
                         'Blue Reverse','Blue Draw 2','Wild',
                     'Red 1','Red 2','Red 3','Red 4','Red 5','Red 6','Red 7','Red 8','Red 9','Red Skip','Red Reverse','Red Draw 2',
                         'Wild Draw 4',
                     'Yellow 1','Yellow 2','Yellow 3','Yellow 4','Yellow 5','Yellow 6','Yellow 7','Yellow 8','Yellow 9','Yellow Skip',
                         'Yellow Reverse','Yellow Draw 2','Wild Draw 4',
                     'Green 1','Green 2','Green 3','Green 4','Green 5','Green 6','Green 7','Green 8','Green 9','Green Skip',
                         'Green Reverse','Green Draw 2','Wild Draw 4',
                     'Blue 1','Blue 2','Blue 3','Blue 4','Blue 5','Blue 6','Blue 7','Blue 8','Blue 9','Blue Skip','Blue Reverse',
                         'Blue Draw 2','Wild Draw 4']
    def shuffle(self, shuffle_times = 0):
        """Shuffles and returns the pack. Parameter: `shuffle_times` — The number of times the pack will be shuffled."""
        if shuffle_times < 0: raise ValueError("'shuffle_times' parameter must not have a negative value")
        self.shuffle_times = int(shuffle_times)
        self.shuffled_times = 0
        while self.shuffled_times < self.shuffle_times:
            random.shuffle(self.pack)
            self.shuffled_times += 1
        return self.pack
    def draw(self, drawn_card = 0):
        """Draws and returns a card from the pack. Parameter: `drawn_card` — The card which will be returned.
        `drawn_card = 0` will return the top card, `drawn_card = -1` will return the bottom card."""
        self.drawn_card = int(drawn_card)
        return self.pack.pop(self.drawn_card)

class Revolver:
    """THESE ARE JUST GAMES OF CHANCE. I DO NOT SUPPORT VIOLENCE.

    A revolver has a cylinder that contains 7 chambers. There is a single cartridge in one of the chambers. Methods:
    - `spin()` — Spins the cylinder and returns the cylinder.
    - `russian_roulette()` — Rotates the cylinder, fires and reuturns what inside the current (first) chamber,
    which can be either 'Empty' or 'Cartridge'."""
    def __init__(self):
        self.cylinder = ['Empty', 'Empty', 'Empty', 'Empty', 'Empty', 'Empty', 'Empty']
        self.cylinder[random.choice([0, 1, 2, 3, 4, 5, 6])] = 'Cartridge'
    def spin(self, spin_times = 0):
        """Spins the cylinder and returns the cylinder. Parameter: `spin_times` — The number of times the cylinder will be spinned."""
        if spin_times < 0: raise ValueError("'spin_times' parameter must not have a negative value")
        self.spin_times = int(spin_times)
        self.spinned_times = 0
        while self.spinned_times < self.spin_times:
            random.shuffle(self.cylinder)
            self.spinned_times += 1
        return self.cylinder
    def russian_roulette(self, rotate_times = 1):
        """Rotates the cylinder, fires and reuturns what inside the current (first) chamber,
        which can be either 'Empty' or 'Cartridge'. Parameter:
        - `rotate_times` — Rotates the cylinder."""
        self.rotate_times = int(rotate_times)
        self.rotated_times = 0
        while self.rotated_times < self.rotate_times:
            self.cylinder.insert(0, self.cylinder.pop())
            self.rotated_times += 1
        if rotate_times < 0: raise ValueError("'shuffle_times' parameter must not have a negative value")
        return self.cylinder[0]

class UnoFlipPack:
    """An *UNO FLIP!* pack. Methods:
    - `shuffle()` — Shuffles and returns the pack.
    - `draw()` — Draws and returns a card from the pack."""
    def __init__(self):
        self.light_pack = [
                     'Red 1','Red 2','Red 3','Red 4','Red 5','Red 6','Red 7','Red 8','Red 9','Red Skip','Red Reverse','Red Draw 1',
                         'Wild', 'Red Flip',
                     'Yellow 1','Yellow 2','Yellow 3','Yellow 4','Yellow 5','Yellow 6','Yellow 7','Yellow 8','Yellow 9',
                         'Yellow Skip','Yellow Reverse','Yellow Draw 1','Wild','Yellow Flip',
                     'Green 1','Green 2','Green 3','Green 4','Green 5','Green 6','Green 7','Green 8','Green 9','Green Skip',
                         'Green Reverse','Green Draw 1','Wild','Green Flip',
                     'Blue 1','Blue 2','Blue 3','Blue 4','Blue 5','Blue 6','Blue 7','Blue 8','Blue 9','Blue Skip','Blue Reverse',
                         'Blue Draw 1','Wild','Blue Flip',
                     'Red 1','Red 2','Red 3','Red 4','Red 5','Red 6','Red 7','Red 8','Red 9','Red Skip','Red Reverse','Red Draw 1',
                         'Wild Draw 2','Red Flip',
                     'Yellow 1','Yellow 2','Yellow 3','Yellow 4','Yellow 5','Yellow 6','Yellow 7','Yellow 8','Yellow 9','Yellow Skip',
                         'Yellow Reverse','Yellow Draw 1','Wild Draw 2','Yellow Flip',
                     'Green 1','Green 2','Green 3','Green 4','Green 5','Green 6','Green 7','Green 8','Green 9','Green Skip',
                         'Green Reverse','Green Draw 1','Wild Draw 2','Green Flip',
                     'Blue 1','Blue 2','Blue 3','Blue 4','Blue 5','Blue 6','Blue 7','Blue 8','Blue 9','Blue Skip','Blue Reverse',
                         'Blue Draw 1','Wild Draw 2','Blue Flip']
        self.dark_pack = [
                     'Teal 1','Teal 2','Teal 3','Teal 4','Teal 5','Teal 6','Teal 7','Teal 8','Teal 9','Teal Skip','Teal Reverse',
                         'Teal Draw 5','Wild','Teal Flip',
                     'Pink 1','Pink 2','Pink 3','Pink 4','Pink 5','Pink 6','Pink 7','Pink 8','Pink 9','Pink Skip','Pink Reverse',
                         'Pink Draw 5','Wild','Pink Flip',
                     'Purple 1','Purple 2','Purple 3','Purple 4','Purple 5','Purple 6','Purple 7','Purple 8','Purple 9','Purple Skip',
                         'Purple Reverse','Purple Draw 5','Wild','Purple Flip',
                     'Orange 1','Orange 2','Orange 3','Orange 4','Orange 5','Orange 6','Orange 7','Orange 8','Orange 9','Orange Skip',
                         'Orange Reverse','Orange Draw 5','Wild','Orange Flip',
                    'Teal 1','Teal 2','Teal 3','Teal 4','Teal 5','Teal 6','Teal 7','Teal 8','Teal 9','Teal Skip','Teal Reverse',
                         'Teal Draw 5', 'Wild Draw Color','Teal Flip',
                     'Pink 1','Pink 2','Pink 3','Pink 4','Pink 5','Pink 6','Pink 7','Pink 8','Pink 9','Pink Skip','Pink Reverse',
                         'Pink Draw 5','Wild Draw Color','Pink Flip',
                     'Purple 1','Purple 2','Purple 3','Purple 4','Purple 5','Purple 6','Purple 7','Purple 8','Purple 9','Purple Skip',
                         'Purple Reverse','Purple Draw 5','Wild Draw Color','Purple Flip',
                     'Orange 1','Orange 2','Orange 3','Orange 4','Orange 5','Orange 6','Orange 7','Orange 8','Orange 9','Orange Skip',
                         'Orange Reverse','Orange Draw 5','Wild Draw Color','Orange Flip']
        random.shuffle(self.dark_pack)
        self.pack = []
        for card in range(0, 112): self.pack.append(f'{self.light_pack[card]} | {self.dark_pack[card]}')
    def shuffle(self, shuffle_times = 0):
        """Shuffles and returns the pack. Parameter: `shuffle_times` — The number of times the pack will be shuffled."""
        if shuffle_times < 0: raise ValueError("'shuffle_times' parameter must not have a negative value")
        self.shuffle_times = int(shuffle_times)
        self.shuffled_times = 0
        while self.shuffled_times < self.shuffle_times:
            random.shuffle(self.pack)
            self.shuffled_times += 1
        return self.pack
    def draw(self, drawn_card = 0):
        """Draws and returns a card from the pack. Parameter: `drawn_card` — The card which will be returned.
        `drawn_card = 0` will return the top card, `drawn_card = -1` will return the bottom card."""
        self.drawn_card = int(drawn_card)
        return self.pack.pop(self.drawn_card)

# SPECIAL SECTION — ANYTHING ELSE THAT RELATES TO THE MODULE
MEMORIAL = ['flip_the_coin()', 'shuffle_pack()', 'shuffle_reveal_pack()', 'roll_the_dice()', 'roll_the_dice()', 'shuffle_uno_pack()',
'shuffle_reveal_uno_pack()', 'russian_roulette()', 'russian_roulette_reveal()']
"""In memory of all functions that only existed in the very first version and were removed on the next version
(They are sorted by time created)"""