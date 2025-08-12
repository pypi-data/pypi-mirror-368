import warnings

from yearn_treasury import budget
from yearn_treasury._db import prepare_db


prepare_db()


warnings.filterwarnings(
    "ignore",
    message=".Event log does not contain enough topics for the given ABI.",
    category=UserWarning,
    module="brownie.network.event",
)


__all__ = ["budget"]
