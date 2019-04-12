# Dynamic storage for magic numbers, added as an attribute to "bot" so it is accessible everywhere and consistent.

config_store = {
    "dice_count_lim": [100, int, 100],
    "dice_sides_lim": [1000, int, 1000],
    "roulette_prob": [1/6, float, 1/6]
}


def get_type(key):
    return config_store[key][1]


def get_val(key):
    return config_store[key][0]


def set_val(key, val):
    config_store[key][0] = get_type(key)(val)


def update_default(key):
    config_store[key][0] = config_store[key][2]


def __getattr__(key):
    return get_val(key)


def __setattr__(key, val):
    set_val(key, val)
