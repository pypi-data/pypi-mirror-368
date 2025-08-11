"""Intelligent Capability common tools."""

from collections import namedtuple

Mathematics = namedtuple("Mathematics", ("ADDITION", "SUBTRACTION", "MULTIPLICATION", "DIVISION"))
Capability = namedtuple("Capability", ("MATH",))

CAPABILITY = Capability(
    MATH=Mathematics(
        ADDITION="mathematics/addition",
        SUBTRACTION="mathematics/subtraction",
        MULTIPLICATION="mathematics/multiplication",
        DIVISION="mathematics/division",
    )
)

ITU_TYPES = {}  # Autopopulated


def aigarth_itu(class_obj: type) -> type:
    """Register a class as a type of Aigarth ITU."""
    ITU_TYPES[class_obj.__name__] = class_obj

    return class_obj
