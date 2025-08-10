from typing import Literal

type InterOperator = Literal[
    "Swap<2, 0>",
    "Swap<2, 1>",
    "Swap<2, 2>",
    "Relocate",
    "SwapStar",
    "Cross",
    "SdSwapStar",
    "SdSwapOneOne",
    "SdSwapTwoOne",
]

type IntraOperator = Literal[
    "Exchange",
    "OrOpt<1>",
    "OrOpt<2>",
    "OrOpt<3>",
]

type AcceptanceRuleType = Literal["HC", "HCWE", "LAHC", "SA"]

type RuinMethodType = Literal["SISRs", "Random"]

type Sorter = Literal[
    "random",
    "demand",
    "far",
    "close",
]

type InputFormat = Literal["DENSE_MATRIX", "COORD_LIST"]
