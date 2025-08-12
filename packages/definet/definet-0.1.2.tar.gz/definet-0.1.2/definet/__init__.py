import enchant
import requests

__all__ = ["definet"]


class Definet:
    def __init__(self) -> None:
        self.url = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        self.D = enchant.Dict("en_US")

    def get(self, word: str):
        r = requests.get(self.url + word)
        if r.status_code != 200:
            print(r.json())


def definet(*, single: str = ""):
    defi = Definet()

    def get(word: str):
        defi.get(word)

    if single != "":
        get(single)

    exit_key = "(|=|)"
    print(f"type a word to see its info.. type {exit_key} to exit")
    end = False
    while not end:
        word = input(" $ ")
        if word == exit_key:
            end = True
        get(word)
