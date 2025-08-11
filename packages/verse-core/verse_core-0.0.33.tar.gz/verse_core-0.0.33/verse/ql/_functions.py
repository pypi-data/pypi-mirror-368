from ._models import Field, Function, Value


class QueryFunctionName:
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"

    IS_DEFINED = "is_defined"
    IS_NOT_DEFINED = "is_not_defined"
    IS_TYPE = "is_type"

    LENGTH = "length"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"

    ARRAY_LENGTH = "array_length"
    ARRAY_CONTAINS = "array_contains"
    ARRAY_CONTAINS_ANY = "array_contains_any"

    STARTS_WITH_DELIMITED = "starts_with_delimited"

    RANDOM = "random"
    NOW = "now"

    VECTOR_SEARCH = "vector_search"


class QueryFunction:
    @staticmethod
    def exists() -> Function:
        return Function(name=QueryFunctionName.EXISTS)

    @staticmethod
    def not_exists() -> Function:
        return Function(name=QueryFunctionName.NOT_EXISTS)

    @staticmethod
    def is_defined(field: str) -> Function:
        return Function(
            name=QueryFunctionName.IS_DEFINED, args=[Field(path=field)]
        )

    @staticmethod
    def is_not_defined(field: str) -> Function:
        return Function(
            name=QueryFunctionName.IS_NOT_DEFINED, args=[Field(path=field)]
        )

    @staticmethod
    def is_type(field: str, type: str) -> Function:
        return Function(
            name=QueryFunctionName.IS_TYPE,
            args=[
                Field(path=field),
                type,
            ],
        )

    @staticmethod
    def starts_with(field: str, value: str) -> Function:
        return Function(
            name=QueryFunctionName.STARTS_WITH,
            args=[
                Field(path=field),
                value,
            ],
        )

    @staticmethod
    def ends_with(field: str, value: str) -> Function:
        return Function(
            name=QueryFunctionName.ENDS_WITH,
            args=[
                Field(path=field),
                value,
            ],
        )

    @staticmethod
    def contains(field: str, value: str) -> Function:
        return Function(
            name=QueryFunctionName.CONTAINS,
            args=[
                Field(path=field),
                value,
            ],
        )

    @staticmethod
    def length(field: str) -> Function:
        return Function(
            name=QueryFunctionName.LENGTH, args=[Field(path=field)]
        )

    @staticmethod
    def array_contains(field: str, value: Value) -> Function:
        return Function(
            name=QueryFunctionName.ARRAY_CONTAINS,
            args=[
                Field(path=field),
                value,
            ],
        )

    @staticmethod
    def array_contains_any(field: str, value: list[Value]) -> Function:
        return Function(
            name=QueryFunctionName.ARRAY_CONTAINS_ANY,
            args=[
                Field(path=field),
                value,
            ],
        )

    @staticmethod
    def array_length(field: str) -> Function:
        return Function(
            name=QueryFunctionName.ARRAY_LENGTH, args=[Field(path=field)]
        )

    @staticmethod
    def starts_with_delimited(
        field: str,
        value: str,
        delimiter: str,
    ) -> Function:
        return Function(
            name=QueryFunctionName.STARTS_WITH_DELIMITED,
            args=[Field(path=field), value, delimiter],
        )

    @staticmethod
    def random() -> Function:
        return Function(name=QueryFunctionName.RANDOM)

    @staticmethod
    def now() -> Function:
        return Function(name=QueryFunctionName.NOW)

    @staticmethod
    def vector_search(
        vector: list[float] | None = None,
        sparse_vector: dict[int, float] | None = None,
        field: str | None = None,
    ):
        return Function(
            name=QueryFunctionName.VECTOR_SEARCH,
            named_args=dict(
                vector=vector, sparse_vector=sparse_vector, field=field
            ),
        )
