import random
import json

def read_json(file):
    # opens a json and imports it for python usage
    try:
        with open(file, 'r', encoding="utf8") as f:
            dic = json.load(f)

        # in case the file is new and doesn't have a mistake section yet
        if "mistakes" not in dic:
            dic["mistakes"] = []

    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        print("The json is missing or invalid :(")
        input("Press Enter to exit")
        return None
    return dic

def create_dics(json_dic):
    # creates dictionaries used by the program
    gender_entries = json_dic['word_kind']['with_gender']
    gender_words = [word['fields'] for word in gender_entries]
    nogender_words = json_dic['word_kind']['no_gender']
    all_words = gender_words + nogender_words

    # loads mistakes if they exist
    mistakes_list = json_dic.get("mistakes", [])

    return {
        'gender_entries': gender_entries,
        'all_words': all_words,
        'gender_words': gender_words,
        'mistakes_list': mistakes_list    
            }

def select_mode():
    # lets the user select the game mode they want
    mode = input("""
Do you want to study gender only? [1]
Review your mistakes? [2]
Study words from a specific gender? [3]
Or study full translations? [4]

""")
    while mode not in {"1", "2", "3", "4"}:
        mode = input("Please only enter 1, 2, 3 or 4 :) : ")
        
    return mode

def gameplay(german_modes):
    # pretty much the game

    mistakes_list = german_modes['mistakes_list']
    mode = select_mode()

    if mode == "1":
        # creates a list relevant to this exercise
        gender_words = german_modes['gender_words']

        print("Ok, let's nail those genders!")
        mistakes = gender_only(gender_words)
    elif mode == "2":
        if mistakes_list:
            print("Let's fix those mistakes")
            mistakes = full_translation(mistakes_list)
        else:
            print("Nothing to review here :)")
            mistakes = 0
        remove_errors("words.json", json_dic)
    elif mode == "3":
        # creates a list relevant to this exercise
        gender_entries = german_modes['gender_entries']

        choice = gen_choice()
        gender_study = [item["fields"] for item in gender_entries if item["gender_type"] == choice]
        mistakes = word_only(gender_study)

    else:
        # creates a list relevant to this exercise
        all_words = german_modes['all_words']

        print("Let's see those translations")
        mistakes = full_translation(all_words)
        write_errors("words.json", json_dic)
    
    return mistakes
        
def replay_option():
        print("Ok, that's it for now!")
        play_again = input("Want to play again? (y/n): ").strip().lower() #takes into account capital answers
        while play_again not in {"y", "n"} :
            play_again = input("Sorry, didn't understand that. Play again? (y/n): ").strip().lower()
        return play_again

def gen_choice():
        # lets the user choose the gender they want to study
        choice = input("Which gender do you wish to review: F, M or N?\n").strip().upper()
        while choice not in ("F", "M", "N"):
            choice = input("Wrong gender, choose between F, M or N: ").strip().upper()
        return choice

def get_word(word_list):
    # gets a word from a list of words
    word = random.choice(word_list)
    english = word.get("english")
    eng_gen = word.get("eng_gen")
    gender = word.get("gender")
    german = word.get("german")
    return word, english, eng_gen, gender, german

def print_word(english, eng_gen):
    # prints the message that needs to be translated
    if eng_gen:
        print(f"{english} ({eng_gen.upper()})")
    else:
        print(english)

def guess_word(word, guess_message, found_message):
        # asks the word until it's found and keeps track of errors
        errors = 0
        guess = input(guess_message).strip()
        while guess != word:
            print("Wrong, try again ;)")
            guess = input(guess_message).strip()
            errors += 1
        print(found_message)
        return errors

def gender_only(dic):
    errors = 0
    words = dic.copy()
    while words:
        word, english, eng_gen, gender, german = get_word(words)
        print_word(english, eng_gen)
        errors += guess_word(gender, "The German Gender is: ", f"That's right! The full translation is: '{gender} {german}'")
        words.remove(word)
    return errors

def word_only(dic):
    errors = 0
    words = dic.copy()
    while words:
        word, english, eng_gen, _, german = get_word(words)
        print_word(english, eng_gen)
        errors += guess_word(german, "The German word is: ", "That's right!")
        words.remove(word)
    return errors

def full_translation(dic):
    errors = 0
    error_list = []
    words = dic.copy()
    while words:
        word, english, eng_gen, gender, german = get_word(words)
        print_word(english, eng_gen)
        # if there is one, start with the gender (mistakes will be counted)
        # this will loop until gotten right to help memorization
        if gender:
            errors += guess_word(gender, "Let's start with the gender: ", "OK")
        guess_the_word = input("The German word (capital letters count): ").strip()
        if guess_the_word == (f"{german}"):
            print("Yep, that's right!")
            words.remove(word)
        # if the translation is wrong the game will move on to another word
        # and come back later to the current one
        else:
            print(f"Wrong, the answer was: {gender + ' ' if gender else ''}{german}")
            if word not in error_list:
                error_list.append(word)
            errors += 1

    for word in error_list:
        if word not in json_dic["mistakes"]:  # prevents duplicates
            json_dic["mistakes"].append(word)
    return errors

def remove_errors(file, dic):
    try:
        data = read_json(file)

        for mistake in dic.get("mistakes", []):
            data["mistakes"].remove(mistake)

    # write the updated data in the file
        with open(file, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=4)

    except (FileNotFoundError, ValueError):
        print("Error: Could not write to json :(")

def write_errors(file, dic):
    try:
        data = read_json(file)

        for mistake in dic.get("mistakes", []):
            # checks if there is already the entry in the file
            if mistake not in data["mistakes"]:
                data["mistakes"].append(mistake)

    # Write the updated data in the file
        with open(file, 'w', encoding="utf8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    except (FileNotFoundError, ValueError):
        print("Error: Could not write to json :(")


play_again = "y"
while play_again == "y":
    json_dic = read_json("words.json")
    german_modes = create_dics(json_dic)
    mistakes = gameplay(german_modes)
    if mistakes:
        print(f"You made {mistakes} mistakes")
    play_again = replay_option()