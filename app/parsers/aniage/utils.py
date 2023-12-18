types = {
    "Повнометражне": "movie",
    "ТБ-Серіал": "series",
    "ONA": "series",
    "OVA": "series",
    "SPECIALS": "series",
    "ТБ-Спешл": "series",
    "Короткометражне": "movie",
}


def get_type(type_) -> str:
    return types.get(type_, "series")
