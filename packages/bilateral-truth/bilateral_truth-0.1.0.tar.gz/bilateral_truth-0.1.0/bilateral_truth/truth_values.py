"""
Truth value representations for the ζ_c function implementation.

Implements 3-valued logic components and generalized truth values
as described in the bilateral factuality evaluation framework.
"""

from enum import Enum
from typing import Tuple


class TruthValueComponent(Enum):
    """
    Three-valued logic components: true (t), undefined (e), false (f)
    """

    TRUE = "t"
    UNDEFINED = "e"
    FALSE = "f"


class EpistemicPolicy(Enum):
    """
    Epistemic policies for mapping generalized truth values to classical 3-valued logic.

    Each policy defines designated (→ t) and anti-designated (→ f) value sets:
    - CLASSICAL: Designated {<t,f>}, Anti-designated {<f,t>}
    - PARACONSISTENT: Designated {<u,v> | u=t}, Anti-designated {<u,v> | v=t}
    - PARACOMPLETE: Designated {<u,v> | v=f}, Anti-designated {<u,v> | u=f}
    """

    CLASSICAL = "classical"
    PARACONSISTENT = "paraconsistent"
    PARACOMPLETE = "paracomplete"


class GeneralizedTruthValue:
    """
    Generalized truth value <u,v> where:
    - u represents verifiability component
    - v represents refutability component
    Both u and v are elements of {t, e, f}
    """

    def __init__(
        self, verifiability: TruthValueComponent, refutability: TruthValueComponent
    ):
        """
        Initialize a generalized truth value.

        Args:
            verifiability: The verifiability component (u)
            refutability: The refutability component (v)
        """
        self.u = verifiability
        self.v = refutability

    def __repr__(self) -> str:
        return f"<{self.u.value},{self.v.value}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, GeneralizedTruthValue):
            return False
        return self.u == other.u and self.v == other.v

    def __hash__(self) -> int:
        return hash((self.u, self.v))

    @property
    def components(self) -> Tuple[TruthValueComponent, TruthValueComponent]:
        """Return the (u, v) components as a tuple."""
        return (self.u, self.v)

    def project(
        self, policy: EpistemicPolicy = EpistemicPolicy.CLASSICAL
    ) -> TruthValueComponent:
        """
        Project generalized truth value to classical 3-valued logic using designated value sets.

        Args:
            policy: Epistemic policy defining designated/anti-designated value sets

        Returns:
            TruthValueComponent: t (designated), f (anti-designated), or e (neither)

        Epistemic Policies:
        - CLASSICAL: Designated {<t,f>}, Anti-designated {<f,t>}
        - PARACONSISTENT: Designated {u=t}, Anti-designated {v=t}
        - PARACOMPLETE: Designated {v=f}, Anti-designated {u=f}
        """
        if policy == EpistemicPolicy.CLASSICAL:
            # Classical: strict correspondence
            if (
                self.u == TruthValueComponent.TRUE
                and self.v == TruthValueComponent.FALSE
            ):
                return TruthValueComponent.TRUE  # <t,f> → t
            elif (
                self.u == TruthValueComponent.FALSE
                and self.v == TruthValueComponent.TRUE
            ):
                return TruthValueComponent.FALSE  # <f,t> → f
            else:
                return TruthValueComponent.UNDEFINED  # all others → e

        elif policy == EpistemicPolicy.PARACONSISTENT:
            # Paraconsistent: allows contradictions
            if self.u == TruthValueComponent.TRUE:
                return TruthValueComponent.TRUE  # {<t,*>} → t
            elif self.v == TruthValueComponent.TRUE:
                return TruthValueComponent.FALSE  # {<*,t>} → f
            else:
                return TruthValueComponent.UNDEFINED  # all others → e

        elif policy == EpistemicPolicy.PARACOMPLETE:
            # Paracomplete: allows truth value gaps
            if self.v == TruthValueComponent.FALSE:
                return TruthValueComponent.TRUE  # {<*,f>} → t
            elif self.u == TruthValueComponent.FALSE:
                return TruthValueComponent.FALSE  # {<f,*>} → f
            else:
                return TruthValueComponent.UNDEFINED  # all others → e
        else:
            raise ValueError(f"Unknown projection policy: {policy}")
