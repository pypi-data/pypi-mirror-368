class EntityType:
    """EntityType class"""

    # TODO Why you changed main_entity_type_id to entity_type_id? -
    #  We might have multiple entity_type_ids, one of them will probably be
    #  the main_entity_type_id
    # TODO Shall we change is_test_data default to false everywhere?
    def __init__(self, *, name: str, **kwargs) -> None:
        """Initialize a EntityType object."""
        for key, value in locals().items():
            if key not in ["self", "kwargs", "__class__"]:
                setattr(self, key, value)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> dict:
        """Convert the EntityType object to a dictionary."""
        to_dict_result = {k: v for k, v in self.__dict__.items() if v is not None}
        return to_dict_result

    def __eq__(self, other: 'EntityType') -> bool:
        """Check if two EntityType objects are equal."""
        eq_result = self.to_dict() == other.to_dict()
        return eq_result

    # Performance
    def __hash__(self) -> int:
        hash_result = hash(tuple(sorted(self.to_dict().items())))
        return hash_result
