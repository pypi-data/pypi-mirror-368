"""
Class to provide interface for the Stable Marriage Problem algorithm.
"""

import os

from algmatch.stableMatchings.stableMarriageProblem.noTies.smManOptimal import (
    SMManOptimal,
)
from algmatch.stableMatchings.stableMarriageProblem.noTies.smWomanOptimal import (
    SMWomanOptimal,
)


class StableMarriageProblem:
    def __init__(
        self,
        filename: str | None = None,
        dictionary: dict | None = None,
        optimised_side: str = "men",
    ) -> None:
        """
        Initialise the Stable Marriage Problem algorithm.

        :param filename: str, optional, default=None, the path to the file to read in the preferences from.
        :param dictionary: dict, optional, default=None, the dictionary of preferences.
        :param optimised_side: str, optional, default="men", whether the algorithm is "men" (default) or "woman" sided.
        """
        if filename is not None:
            filename = os.path.join(os.getcwd(), filename)

        assert type(optimised_side) is str, "Param optimised_side must be of type str"
        optimised_side = optimised_side.lower()
        assert optimised_side in ("men", "women"), (
            "Optimised side must either be 'men' or 'women'"
        )

        if optimised_side == "men":
            self.sm_alg = SMManOptimal(filename=filename, dictionary=dictionary)
        else:
            self.sm_alg = SMWomanOptimal(filename=filename, dictionary=dictionary)

    def get_stable_matching(self) -> dict | None:
        """
        Get the stable matching for the Stable Marriage Problem algorithm.

        :return: dict, the stable matching for this instance
        """
        self.sm_alg.run()
        if self.sm_alg.is_stable:
            return self.sm_alg.stable_matching
        return None
