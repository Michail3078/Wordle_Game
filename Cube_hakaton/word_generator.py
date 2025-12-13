import random


def get_rand_word():
    with open('words.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        random_line = random.choice(lines).strip()
        return random_line

def chek_word(word):
    word = word.lower().strip()
    with open("words.txt", 'r', encoding='utf-8') as file:
        for line in file:
            if word in (w.lower() for w in line.split()):
                return True
    return False