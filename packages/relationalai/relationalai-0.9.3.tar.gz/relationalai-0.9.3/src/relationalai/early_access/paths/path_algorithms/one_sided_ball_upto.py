import time
from relationalai.early_access.builder import Integer
from relationalai.early_access.builder import define, not_

from ..graph import Graph
from ..utilities.iterators import setup_iteration


# Source and Target are concepts representing sets of nodes
def ball_upto(g:Graph, Source, Target, max_length=None):
    edge = g.Edge
    Node = g.Node

    # ball(d, ⋅) is the sphere of nodes at distance d from the source node
    # visited(d, ⋅) is the union of all balls up to distance d

    ball = g.model.Relationship(f"At hop {{d:Integer}} ball has node {{v:{Node}}} {time.time_ns()}") # , [Integer, Node])
    visited = g.model.Relationship(f"At hop {{d:Integer}} node {{v:{Node}}} has been visited {time.time_ns()}") # , [Integer, Node])
    condition = g.model.Relationship(f"The iteration can continue from {{Integer}} {time.time_ns()}")

    if max_length is None:
        iter = setup_iteration(g.model, condition, 0, 1000000)
    else:
        iter = setup_iteration(g.model, condition, 0, max_length)

    src, tgt = Node.ref(), Node.ref()

    # Ball around src contains src at distance 0:
    define(ball(0, src)).where(Source(src))

    u, v = g.Node.ref(), g.Node.ref()
    n, k = Integer.ref(), Integer.ref()

    # Recursive case:
    define(ball(k, v)).where(
        iter(k),
        ball(k - 1, u),
        edge(u, v),
        not_(
            visited(k - 1, v),
        ),
    )

    define(ball(k, u)).where(
        ball(k, u)
    )

    define(visited(k, u)).where(
        ball(k, u)
    )

    define(visited(k, u)).where(
        ball(k - 1, u)
    )

    define(condition(n)).where(
        iter(n),
        ball(n, u),
        not_(
            ball(n, tgt),
            Target(tgt)
        )
    )

    return ball


def ball_upto_alt(g:Graph, Source, Target, max_length=None):
    edge = g.Edge
    Node = g.Node

    # ball(d, ⋅) is the sphere of nodes at distance d from the source node

    ball = g.model.Relationship(f"At hop {{d:Integer}} ball has node {{v:{Node}}} {time.time_ns()}") # , [Integer, Node])
    condition = g.model.Relationship(f"The iteration can continue from {{Integer}} {time.time_ns()}")

    if max_length is None:
        iter = setup_iteration(g.model, condition, 0, 1000000)
    else:
        iter = setup_iteration(g.model, condition, 0, max_length)

    src, tgt = Node.ref(), Node.ref()

    # Ball around src contains src at distance 0:
    define(ball(0, src)).where(Source(src))

    u, v = g.Node.ref(), g.Node.ref()
    n, k = Integer.ref(), Integer.ref()

    # Recursive case:
    define(ball(k, v)).where(
        iter(k),
        ball(k - 1, u),
        edge(u, v),
        not_(
            ball(n, v),
        ),
    )

    define(ball(k, u)).where(
        ball(k, u)
    )

    define(condition(n)).where(
        iter(n),
        ball(n, u),
        not_(
            ball(n, tgt),
            Target(tgt)
        )
    )

    return ball
