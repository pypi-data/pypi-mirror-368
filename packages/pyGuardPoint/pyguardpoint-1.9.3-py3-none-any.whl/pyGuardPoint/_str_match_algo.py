import json
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

def fuzzy_match(search_words: str, cardholders: list, threshold: int = 75):
    if not search_words:
        return cardholders

    cardholder_patterns = []
    for cardholder in cardholders:
        cardholder_patterns.append(cardholder.to_search_pattern())

    match_ratios = process.extract(search_words, cardholder_patterns, scorer=fuzz.token_sort_ratio)

    sorted_cardholders = []
    for match in match_ratios:
        if match[1] >= threshold:
            pos = cardholder_patterns.index(match[0])
            sorted_cardholders.append(cardholders[pos])

    return sorted_cardholders


if __name__ == "__main__":
    from pyGuardPoint_Build.pyGuardPoint import Cardholder

    EXPORT_FILENAME = '../../cardholder_export.json'
    with open(EXPORT_FILENAME) as f:
        entries = json.load(f)
    count = len(entries)
    print(f"Importing {str(count)} entries from {EXPORT_FILENAME}.")

    cardholders = []
    for entry in entries:
        cardholders.append(Cardholder(entry))

    search_pattern = "john owen"
    print("Search Pattern:" + search_pattern)
    sorted_cardholders = fuzzy_match(search_pattern, cardholders, 50)

    print(f"Got {len(sorted_cardholders)} matches")
    print(f"Best Match: {sorted_cardholders[0].firstName} {sorted_cardholders[0].lastName}")
    print(f"Second Best Match: {sorted_cardholders[1].firstName} {sorted_cardholders[1].lastName}")
    # pos = cardholder_patterns.index(match_ratios[0][0])

    # print(cardholders[pos].pretty_print())
