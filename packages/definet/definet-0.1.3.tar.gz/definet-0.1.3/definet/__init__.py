import enchant
import requests

from .rgb import rgb

__all__ = ["definet"]

SUCCESS = rgb(64, 219, 66)
FAIL = rgb(212, 54, 54)


class Definet:
    def __init__(self) -> None:
        self.url = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        self.D = enchant.Dict("en_US")
        self.tabstop = 4
        self.tab = " " * self.tabstop

    def get(self, word: str):
        r = requests.get(self.url + word)
        if r.status_code != 200:
            print(FAIL(f"❌ '{word}' not found in the dictionary."))
            print(f"Did you mean: {', '.join(self.D.suggest(word)[:3])}")
            print(f"Resolution: {r.json()['resolution']}")
            return

        data = r.json()

        print(SUCCESS(f"\n📖 Word: {data[0]['word'].title()}"))
        print(f"🔊 Phonetic: {data[0].get('phonetic', 'N/A')}")

        for meaning in data[0]["meanings"]:
            print(f"\n📝 Part of Speech: {meaning['partOfSpeech']}")
            for idx, definition in enumerate(meaning["definitions"], start=1):
                print(f"{self.tab}{idx}. {definition['definition']}")
                if "example" in definition:
                    print(f"{self.tab}{self.tab}💡 Example: {definition['example']}")


def definet(*, single: str = ""):
    defi = Definet()

    if single != "":
        defi.get(single)

    exit_key = "."
    print(f"type a word to see its info.. type {exit_key} to exit")
    end = False
    while not end:
        word = input("\n $ ").lower()
        end = word == exit_key or end
        defi.get(word)
