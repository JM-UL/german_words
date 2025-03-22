import random
import json


def create_dics(json_dic):
    gender_dic = json_dic["word_kind"]["with_gender"]
    mistakes_dic = json_dic.get("mistakes", [])
    nogender_dic = json_dic["word_kind"]["no_gender"]
    all_dic = gender_dic + nogender_dic
    return gender_dic, mistakes_dic, all_dic

def gender_only(dic):
    errors = 0
    words = dic.copy()
    while words:
        word = random.choice(words)
        english = word.get("english")
        eng_gen = word.get("eng_gen")
        gender = word.get("gender")
        german = word.get("german")
        if eng_gen:
            print(f"{english} ({eng_gen.upper()})")
        else:
            print(english)
        # asks the gender until gotten right
        guess = input("The German gender is: ")
        while guess != gender:
            guess = input("Wrong, try again: ")
            errors += 1
        print(f"That's right! The full translation is: '{gender} {german}'")
        words.remove(word)
    return errors

def full_translation(dic):
    errors = 0
    error_list = []
    words = dic.copy()
    while words:
        word = random.choice(words)
        english = word.get("english")
        eng_gen = word.get("eng_gen")
        gender = word.get("gender")
        german = word.get("german")
        # prints the English gender if necessary
        if eng_gen:
            print(f"{english} ({eng_gen.upper()})")
        else:
            print(english)
        # if there is one, start with the gender (mistakes will be counted)
        # this will loop until gotten right to help memorization
        if gender:
            guess_gen = input("Let's start with the gender: ").strip() #remove spaces in guesses
            while guess_gen != gender:
                guess_gen = input("Wrong, try again: ").strip()
                errors += 1
        guess_word = input("The German word (capital letters count): ").strip()
        if guess_word == (f"{german}"):
            print("Yep, that's right!")
            words.remove(word)
        # if the translation is wrong the game will move on to another word
        # and come back later to the current one
        else:
            if gender:
                print(f"Wrong, the answer was: {gender} {german}")
            else:
                print(f"Wrong, the answer was: {german}")
            
            if word not in error_list:
                error_list.append(word)
            errors += 1

    for word in error_list:
        if word not in json_dic["mistakes"]:  # prevents duplicates
            json_dic["mistakes"].append(word)
    return errors

def read_json(file):
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

def remove_errors(file, dic):
    try:
        data = read_json(file)

        for mistake in dic.get("mistakes", []):
            data["mistakes"].remove(mistake)

    # Write the updated data in the file
        with open(file, 'w', encoding="utf8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

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
    gender_dic, mistakes_dic, all_dic = create_dics(json_dic)
    mode = input("""
Do you want to study gender only? [1]
Review your mistakes? [2]
Or study full translations? [3]
""")
    while mode not in {"1", "2", "3"}:
        mode = input("Please only enter 1, 2, or 3 :) : ")
    if mode == "1":
        print("Ok, let's nail those genders!")
        mistakes = gender_only(gender_dic)
        print(f"You made {mistakes} mistakes.")
    elif mode == "2":
        if mistakes_dic:
            print("Let's fix those mistakes")
            mistakes = full_translation(mistakes_dic)
        else:
            print("Nothing to review here :)")
            mistakes = 0
        remove_errors("words.json", json_dic)
    else:
        print("Let's see those translations")
        mistakes = full_translation(all_dic)
        write_errors("words.json", json_dic)
        print(f"You made {mistakes} mistakes.")

    print("Ok, that's it for now!")
    play_again = input("Want to play again? (y/n): ").strip().lower() #takes into account capital answers
    while play_again not in {"y", "n"} :
        play_again = input("Sorry, didn't understand that. Play again? (y/n): ").strip().lower()