
class PersonError(Exception):
    pass


def assert_person(expr, text='Person error'):
    if not expr:
        raise PersonError(text)
