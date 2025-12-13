import word_generator as wg


def w_game(word, user_word):
    if  not wg.chek_word(user_word):
        return False
    s = []
    for j in range(5):
        if user_word[j] == word[j]:
            s.append("🟩")
        elif user_word[j] in word:
            s.append("🟨")
        else:
            s.append("🟥")

    return "".join(s)