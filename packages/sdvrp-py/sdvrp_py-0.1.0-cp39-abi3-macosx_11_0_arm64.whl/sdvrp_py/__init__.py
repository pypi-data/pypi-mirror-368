from typing import Optional, Literal
from itertools import chain
from sdvrp_py import rstypes
import sdvrp_py._core


def solve_sdvrp(
    capacity: int,
    demands: list[int],
    distance_matrix: Optional[list[list[int]]] = None,
    coord_list: Optional[list[tuple[int, int]]] = None,
    random_seed: int = 42,
    time_limit: float = 20.0,
    blink_rate: float = 0.021,
    inter_operators: list[rstypes.InterOperator] = [
        "Relocate",
        "Swap<2, 0>",
        "Swap<2, 1>",
        "Swap<2, 2>",
        "Cross",
        "SwapStar",
        "SdSwapStar",
    ],
    intra_operators: list[rstypes.IntraOperator] = ["Exchange", "OrOpt<1>"],
    acceptance_rule_type: rstypes.AcceptanceRuleType = "LAHC",
    acceptance_rule_args: dict[
        Literal["length", "initial_temperature", "decay"], int | float
    ] = {"length": 83},
    ruin_method_type: rstypes.RuinMethodType = "SISRs",
    ruin_method_args: dict[
        Literal[
            "average_customers", "max_length", "split_rate", "preserved_probability"
        ],
        int | float,
    ]
    | list[int] = {
        "average_customers": 36,
        "max_length": 8,
        "split_rate": 0.740,
        "preserved_probability": 0.096,
    },
    sorters: dict[rstypes.Sorter, float] = {
        "random": 0.078,
        "demand": 0.225,
        "far": 0.942,
        "close": 0.120,
    },
) -> list[list[tuple[int, int]]]:
    assert not distance_matrix is coord_list is None
    assert isinstance(ruin_method_args, dict if ruin_method_type == "SISRs" else list)
    if distance_matrix is not None:
        assert all(
            (len(distance_matrix) == len(row) == len(demands) + 1)
            for row in distance_matrix
        )
        assert all(
            distance_matrix[i][j] == distance_matrix[j][i]
            for i in range(len(distance_matrix))
            for j in range(i)
        )
    else:
        assert len(coord_list) == len(demands) + 1

    flat_dist_matrix = (
        list(chain.from_iterable(distance_matrix))
        if distance_matrix is not None
        else []
    )

    return sdvrp_py._core.solve_sdvrp(
        random_seed=random_seed,
        time_limit=time_limit,
        blink_rate=blink_rate,
        inter_operators=inter_operators,
        intra_operators=intra_operators,
        acceptance_rule_type=acceptance_rule_type,
        lahc_length=acceptance_rule_args.get("length", 83),
        sa_initial_temperature=acceptance_rule_args.get("initial_temperature", 0.0),
        sa_decay=acceptance_rule_args.get("decay", 0.0),
        ruin_method_type=ruin_method_type,
        sisrs_average_customers=ruin_method_args.get("average_customers", 36),
        sisrs_max_length=ruin_method_args.get("max_length", 8),
        sisrs_split_rate=ruin_method_args.get("split_rate", 0.740),
        sisrs_preserved_probability=ruin_method_args.get(
            "preserved_probability", 0.096
        ),
        random_ruin_sizes=([] if ruin_method_type != "Random" else ruin_method_args),
        sorters=list(sorters.keys()),
        sorter_values=list(sorters.values()),
        capacity=capacity,
        demands=demands,
        input_format="DENSE_MATRIX" if distance_matrix is not None else "COORD_LIST",
        distance_matrix=flat_dist_matrix if distance_matrix is not None else [],
        coord_list_x=(
            [coord[0] for coord in coord_list] if coord_list is not None else []
        ),
        coord_list_y=(
            [coord[1] for coord in coord_list] if coord_list is not None else []
        ),
    )
