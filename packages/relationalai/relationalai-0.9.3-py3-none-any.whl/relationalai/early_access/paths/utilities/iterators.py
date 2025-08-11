from relationalai.early_access.builder import Integer
from relationalai.early_access.builder import define, max


def setup_iteration(model, condition, initial = 0, final = 50):
    iter = model.Relationship("Current value of the iterator is {Integer}")
    next = model.Relationship("{Integer} is a candidate for the next value of the iterator")

    m, n = Integer.ref(), Integer.ref()

    define(next(initial))

    define(next(n)).where(
        iter(n)
    )

    define(next(n)).where(
        iter(m),
        n == m + 1,
        condition(m),
        n <= final
    )

    define(iter(max(n))).where(
        next(n)
    )

    return iter