"""Examples, as tests."""

from strarr import strarr


def _check(output: str, expected: str):
    expected_prefix = "Output:"
    assert expected.startswith(expected_prefix)
    print(expected)
    assert output.strip() == expected[len(expected_prefix) :].strip()


class Example:
    def __init__(self, an_id, name):
        self.id = an_id
        self.name = name


class ExampleWithProps:
    __props__ = ("the_name", "the_id")

    def __init__(self, the_id, name):
        self.the_id = the_id
        self.the_name = name
        self.not_displayed = the_id * 2
        self.not_displayed_again = the_id * 100


class ExampleWithSlots:
    __slots__ = ("displayed", "also_displayed", "the_id", "the_name")

    def __init__(self, the_id, name):
        self.the_name = name
        self.the_id = the_id
        self.displayed = the_id * 2
        self.also_displayed = the_id * 100


class ExampleWithSlotsAndProps(ExampleWithSlots):
    __props__ = ("displayed", "the_name")
    __slots__ = ()


def test_examples():
    data = [Example(1, "Alice"), Example(2, "Bob")]

    # Basic example
    _check(
        strarr(data),
        """Output:
#  [id]  [name]
1     1   Alice
2     2     Bob
""",
    )

    # You can add an indentation
    _check(
        strarr(data, indent="++++++++++|"),
        """Output:
++++++++++|#  [id]  [name]
++++++++++|1     1   Alice
++++++++++|2     2     Bob
""",
    )

    # You can remove index
    _check(
        strarr(data, index=None),
        """Output:
[id]  [name]
   1   Alice
   2     Bob
""",
    )

    # Or control the index start (default is 1).
    _check(
        strarr(data, index=0),
        """Output:
#  [id]  [name]
0     1   Alice
1     2     Bob
""",
    )

    # You can select the fields to display
    _check(
        strarr(data, include=["name"]),
        """Output:
#  [name]
1   Alice
2     Bob
""",
    )

    # Or you can exclude fields
    _check(
        strarr(data, exclude=["name"]),
        """Output:
#  [id]
1     1
2     2
""",
    )

    # You can change spaces between columns (default is 2)
    _check(
        strarr(data, space=0),
        """Output:
#[id][name]
1   1 Alice
2   2   Bob
""",
    )

    _check(
        strarr(data, space=7),
        """Output:
#       [id]       [name]
1          1        Alice
2          2          Bob
""",
    )

    # You can use a special class attribute __props__
    # to control which fields to include, and order in which they are displayed.
    _check(
        strarr([ExampleWithProps(1, "Alice"), ExampleWithProps(2, "Bob")]),
        """Output:
#  [the_name]  [the_id]
1       Alice         1
2         Bob         2
""",
    )

    # Or, you can display all fields but control display order with slots.
    _check(
        strarr([ExampleWithSlots(1, "Alice"), ExampleWithSlots(2, "Bob")]),
        """Output:
#  [displayed]  [also_displayed]  [the_id]  [the_name]
1            2               100         1       Alice
2            4               200         2         Bob
""",
    )

    # Note that __props__ is prioritized over __slots__
    _check(
        strarr(
            [ExampleWithSlotsAndProps(1, "Alice"), ExampleWithSlotsAndProps(2, "Bob")]
        ),
        """Output:
#  [displayed]  [the_name]
1            2       Alice
2            4         Bob
""",
    )

    # Everything works with dictionaries too
    data_dicts = [
        {"my_id": 1, "my_name": "Alice", "age": 44},
        {"my_id": 2, "my_name": "Bob", "age": 30},
    ]
    _check(
        strarr(data_dicts, exclude=("my_id",), index=133, indent="-- ", space=4),
        """Output:
--   #    [my_name]    [age]
-- 133        Alice       44
-- 134          Bob       30
""",
    )
