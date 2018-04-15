def page(string, length):
    return [string[start:start + length] for start in range(0, len(string), length)]


def paginate(string, page_length, prepend='', append=''):
    extra = len(prepend) + len(append)
    if len(string) + extra < page_length:
        return [prepend + string + append]
    else:
        return [prepend + p + append for p in page(string, page_length - extra)]
