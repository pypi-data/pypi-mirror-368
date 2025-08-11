# For builder components.
from relationalai.early_access.builder import Integer
from relationalai.early_access.builder import define, sum, not_

from relationalai.early_access.paths.graph import Graph
from relationalai.early_access.paths.path_algorithms.one_sided_ball_upto import ball_upto
from relationalai.early_access.paths.path_algorithms.one_sided_ball_repetition import ball_with_repetition


def compute_usp(g: Graph, Source, Target, max_length=None):
    # Computes the Union of Shortest Paths (USP) from a source set to a destination set
    # USP is a subgraph of the original graph

    edge = g.Edge
    Node = g.Node

    n, d = Integer.ref(), Integer.ref()
    tgt, u, v = Node.ref(), g.Node.ref(), g.Node.ref()

    ball = ball_upto(g, Source, Target, max_length)
    usp_nodes = g.model.Relationship(f"Node {{u:{Node}}} is in the USP")
    usp = g.model.Relationship(f"Edge {{u:{Node}}} to {{v:{Node}}} is in the USP")
    boundary = g.model.Relationship(f"Target node {{u:{Node}}} is in the boundary of the ball")

    # propagate backwards to find the nodes that are in the USP:
    define(boundary(tgt)).where(
        Target(tgt),
        ball(n, tgt)
    )

    define(usp_nodes(tgt)).where(
        boundary(tgt)
    )

    define(usp_nodes(u)).where(
        usp(u, v)
    )

    define(usp(u, v)).where(
        usp_nodes(v),
        ball(d, v),
        ball(d - 1, u),
        edge(u, v)
    )

    return usp, boundary


def compute_uw(g: Graph, Source, Target, max_length):
    # Computes the Union of Walks (UW) up to a given length from a source set to a destination set

    edge = g.Edge
    Node = g.Node

    n = Integer.ref()
    tgt, u, v, w = Node.ref(), g.Node.ref(), g.Node.ref(), g.Node.ref()

    ball = ball_with_repetition(g, Source, max_length)
    uw = g.model.Relationship(f"{{{Node}}} at distance {{Integer}} from the source nodes is connected with {{v:{Node}}}")
    boundary = g.model.Relationship(f"Target pair {{u:{Node}}} {{Integer}} is in the boundary of the ball")

    define(uw(u, n, tgt)).where(
        Target(tgt),
        ball(n + 1, tgt),
        ball(n, u),
        edge(u, tgt)
    )

    define(uw(u, n, v)).where(
        uw(v, n + 1, w),
        ball(n, u),
        edge(u, v)
    )

    define(boundary(tgt, n)).where(
        Target(tgt),
        ball(n, tgt),
        not_(uw(tgt, n, u))
    )

    return uw, boundary


def compute_nsp_from_usp(g: Graph, usp, Source, Target, Boundary):
    Node = g.Node

    n = Integer.ref()
    tgt, u, v = Node.ref(), Node.ref(), Node.ref()

    nsp = g.model.Relationship(f"Number of shortest paths from {{{Node}}} to destination is {{Integer}}")

    define(nsp(tgt, 1)).where(
        Boundary(tgt)
    )

    define(nsp(tgt, 1)).where(
        Target(tgt),
        Source(tgt)
    )

    define(nsp(u, sum(v, n).per(u))).where(
        nsp(v, n),
        usp(u, v)
    )

    return nsp


def compute_nw_from_uw(g: Graph, usp, Target, Boundary):
    Node = g.Node

    n, m = Integer.ref(), Integer.ref()
    tgt, u, v = Node.ref(), Node.ref(), Node.ref()

    nw = g.model.Relationship(f"Number of shortest paths from pair {{{Node}}} {{Integer}} to destination is {{Integer}}")

    define(nw(tgt, n, 1)).where(
        Boundary(tgt, n)
    )

    define(nw(u, n, sum(v, n + 1, m).per(u, n))).where(
        nw(v, n + 1, m),
        usp(u, n, v),
        not_(Target(u))
    )

    define(nw(u, n, 1 + sum(v, n + 1, m).per(u, n))).where(
        nw(v, n + 1, m),
        usp(u, n, v),
        Target(u),
        not_(Boundary(u, n))
    )

    return nw


def compute_nsp(g: Graph, Source, Target):
    # Computes the number of shortest paths (NSP) from a source set to a destination set

    usp, Boundary  = compute_usp(g, Source, Target)
    nsp = compute_nsp_from_usp(g, usp, Source, Target, Boundary)

    return nsp


def compute_nw(g: Graph, Source, Target, max_length):
    # Computes the number of shortest paths (NSP) from a source set to a destination set

    uw, Boundary  = compute_uw(g, Source, Target, max_length)
    nw = compute_nw_from_uw(g, uw, Target, Boundary)

    return nw
