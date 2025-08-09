from __future__ import annotations

import re
from dataclasses import dataclass

from tinycss2 import parse_component_value_list, serialize

__all__ = ["Specificity", "SpecificityCalculator"]


@dataclass
class Specificity:
    a: int = 0  # ID selectors
    b: int = 0  # Class selectors, attribute selectors, and pseudo-classes
    c: int = 0  # Type selectors and pseudo-elements

    def __str__(self):
        return f"{self.a},{self.b},{self.c}"

    def __repr__(self):
        return f"Specificity(a={self.a}, b={self.b}, c={self.c})"

    def __add__(self, other):
        return Specificity(self.a + other.a, self.b + other.b, self.c + other.c)

    def __lt__(self, other):
        return (self.a, self.b, self.c) < (other.a, other.b, other.c)

    def __le__(self, other):
        return (self.a, self.b, self.c) <= (other.a, other.b, other.c)

    def __gt__(self, other):
        return (self.a, self.b, self.c) > (other.a, other.b, other.c)

    def __ge__(self, other):
        return (self.a, self.b, self.c) >= (other.a, other.b, other.c)

    def __eq__(self, other):
        return (self.a, self.b, self.c) == (other.a, other.b, other.c)

    def to_list(self) -> list[int]:
        return [self.a, self.b, self.c]

    @classmethod
    def max(cls, specs):
        return max(specs, default=Specificity(), key=lambda s: (s.a, s.b, s.c))


class SpecificityCalculator:
    """
    Represents a calculator for computing the specificity of CSS selectors.

    This class provides a method for calculating CSS selector specificity based on
    a simplified approach using regular expressions. The specificity rules
    follow the general CSS specificity formula (a, b, c). Proper processing and
    parsing of CSS selectors, including different selector components like IDs,
    classes, attributes, pseudo-classes, and pseudo-elements, are supported, with
    some simplifications or assumptions.

    Attributes:
        ATTRIBUTE_RE (Pattern): A compiled regular expression to match CSS attribute selectors.
        ID_RE (Pattern): A compiled regular expression to match CSS ID selectors.
        CLASS_RE (Pattern): A compiled regular expression to match CSS class selectors.
        PSEUDO_CLASS_RE (Pattern): A compiled regular expression to match pseudo-classes
            in CSS selectors.
        PSEUDO_ELEMENT_RE (Pattern): A compiled regular expression to match pseudo-elements
            in CSS selectors.
        PSEUDO_ELEMENT_CUSTOM_RE (Pattern): A compiled regular expression to match
            custom pseudo-elements in CSS selectors.

    Methods:
        calculate(selector: str) -> Specificity: Calculates the specificity of a CSS selector.
    """

    # A: Regex patterns for ID selectors
    ID_RE = re.compile(r"#[a-zA-Z_][\w\-]*")

    # B: Regex patterns for class selectors, attribute selectors, and pseudo-classes
    ATTRIBUTE_RE = re.compile(
        r"\[\s*([a-zA-Z_-][a-zA-Z0-9_-]*)"
        r"(?:\s*([~|^$*]?=)\s*(?:\"[^\"]*\"|'[^']*'|[^]\s]+))?\s*]",
    )
    CLASS_RE = re.compile(r"\.[a-zA-Z_][\w\-]*")
    PSEUDO_CLASS_RE = re.compile(
        r"(?<!:):(?!before\b|after\b|first-line\b|first-letter\b)[a-zA-Z_][\w\-]*(?:\([^)]*\))?",
    )

    # C: Regex patterns for type selectors and pseudo-elements
    TYPE_SELECTOR_RE = re.compile(
        r"(?<![#.\[:\w-])"
        r"([a-zA-Z_][\w-]*(?:\|[a-zA-Z_][\w-]*)?)",
    )
    PSEUDO_ELEMENT_RE = re.compile(
        r"::[a-zA-Z_][\w\-]*"
        # INFO: For old syntaxe of the pseudo-element with only one ":"
        r"|:(before|after|first-line|first-letter)\b",
        re.IGNORECASE,
    )
    PSEUDO_ELEMENT_CUSTOM_RE = re.compile(r"::[a-zA-Z_][\w\-]*(?:\([^)]*\))?")

    # Regex pattern for special pseudo-classes functions
    # TODO: Doesn't handle complex nested parentheses yet
    SPECIAL_PSEUDO_FUNC_RE = re.compile(r"(?<!:):(is|not|has)\s*\(([^()]*)\)")
    SPECIAL_WHERE_FUNC_RE = re.compile(r"(?<!:):where\s*\(([^()]*)\)")

    @staticmethod
    def _count_matches(matches: list[str | tuple[str, ...]]) -> int:
        """
        Counts the number of non-empty elements in the provided list of matches.

        The method evaluates each element in the input list and increments the count
        if the element is a tuple containing at least one truthy value or if the
        element is a non-empty string.

        Args:
            matches (list): A list of elements where each element is either a string
                or a tuple. The method counts non-empty strings and tuples with at
                least one truthy value.

        Returns:
            int: The count of non-empty elements in the list.
        """
        return sum(1 for m in matches if (isinstance(m, tuple) and any(m)) or (isinstance(m, str) and m))

    @classmethod
    def _specificity_of_selector(cls, selector: str) -> Specificity:
        """
        Calculates the CSS selector specificity based on the provided selector string.
        The specificity is determined using the number of ID selectors, class selectors,
        and type selectors in the CSS selector.

        Args:
            selector (str): The CSS selector string to analyze.

        Returns:
            Specificity: An object representing the specificity with three components:
            (a) the count of ID selectors,
            (b) the combined count of class selectors, attribute selectors, and pseudo-class, and
            (c) the combined count of type selectors and pseudo-element.
        """
        a = cls._count_matches(cls.ID_RE.findall(selector))
        b = (
            cls._count_matches(cls.CLASS_RE.findall(selector)) +
            cls._count_matches(cls.ATTRIBUTE_RE.findall(selector)) +
            cls._count_matches(cls.PSEUDO_CLASS_RE.findall(selector))
        )
        c = (
            cls._count_matches(cls.TYPE_SELECTOR_RE.findall(selector)) +
            cls._count_matches(cls.PSEUDO_ELEMENT_RE.findall(selector)) +
            cls._count_matches(cls.PSEUDO_ELEMENT_CUSTOM_RE.findall(selector))
        )

        return Specificity(a, b, c)

    @classmethod
    def calculate(cls, selector: str) -> Specificity:
        """
        Calculates the specificity of a given CSS selector string. Specificity is a measure
        used to determine which CSS rule is applied when multiple rules match the same
        element. This method takes into account pseudo-classes, and special functions
        like "where/not/is/has" following the rules defined by the CSS specification.
        https://www.w3.org/TR/selectors-4/#specificity-rules

        Args:
            selector (str): The CSS selector string whose specificity is to be calculated.

        Returns:
            Specificity: The calculated specificity of the given selector.

        Raises:
            TypeError: If the provided selector is not a valid CSS selector.
        """
        try:
            work_selector = serialize(parse_component_value_list(selector, skip_comments=True))

            # INFO: Remove the "where" pseudo-class function because its specificity is replaced by
            #  zero (https://www.w3.org/TR/selectors-4/#specificity-rules)
            re.sub(cls.SPECIAL_WHERE_FUNC_RE, "", work_selector)

            while True:
                match = cls.SPECIAL_PSEUDO_FUNC_RE.search(work_selector)
                if not match:
                    break

                inner = match.group(2)

                inners = [selector.strip() for selector in inner.split(",")]
                specificities = [cls._specificity_of_selector(selector) for selector in inners]

                max_specificity = Specificity.max(specificities)

                work_selector = work_selector[:match.start()] + work_selector[match.end():]

                if not hasattr(cls, "_specials_max_specificities"):
                    cls._specials_max_specificities = []

                cls._specials_max_specificities.append(max_specificity)

            base_specificity = cls._specificity_of_selector(work_selector)

            total_special_specificity = sum(getattr(cls, "_specials_max_specificities", []), Specificity(0, 0, 0))

            if hasattr(cls, "_specials_max_specificities"):
                delattr(cls, "_specials_max_specificities")

            return base_specificity + total_special_specificity
        except TypeError as e:
            raise TypeError(f"Invalid CSS selector: {selector}\n{e}") from e
