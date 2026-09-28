import math


def calculate_hoeffding_bound(
    m_trials: int,
    delta: float = 0.05
) -> float:
    if m_trials <= 0:
        raise ValueError(
            "Number of trials must be greater than zero"
        )

    if not 0 < delta < 1:
        raise ValueError(
            "Delta must be between 0 and 1"
        )

    bound = math.sqrt(
        math.log(2 / delta)
        / (2 * m_trials)
    )

    return bound