import boundml.instances
from boundml.evaluation import evaluate_solvers
from boundml.solvers import DefaultScipSolver, ModularSolver
from boundml.components import Pseudocosts, StrongBranching, ConditionalBranchingComponent

instances = boundml.instances.CombinatorialAuctionGenerator(100, 500)
instances.seed(0)

c = ConditionalBranchingComponent(
    (StrongBranching(), lambda m: m.getDepth() < 3),
    (Pseudocosts(), lambda _: True)
)


solvers = [
    DefaultScipSolver("vanillafullstrong"),
    # ModularSolver(StrongBranching()),
    # ModularSolver(StrongBranching(True, False)),
    # ModularSolver(Pseudocosts()),
    # ModularSolver(c),
]

evaluate_solvers(solvers, instances, 5, ["nnodes", "time"], 0)
