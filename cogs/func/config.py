# Dynamic storage for magic numbers, added as an attribute to "bot" so it is accessible everywhere and consistent.

config_store = {
    "dice_count_lim": 100,
    "dice_sides_lim": 1000,
    "roulette_prob": 1/6
}

expected_type = {
    "dice_count_lim": int,
    "dice_sides_lim": int,
    "roulette_prob": float
}


def get_type(key):
    return expected_type[key]


def get_key(key):
    return config_store[key]


def set_key(key, val):
    config_store[key] = get_type(key)(val)


def __getattr__(key):
    return get_key(key)


def __setattr__(key, val):
    set_key(key, val)
