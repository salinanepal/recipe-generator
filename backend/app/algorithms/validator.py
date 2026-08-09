import re

MIN_INGREDIENTS = 1
MAX_INGREDIENTS = 20

MIN_INGREDIENT_LENGTH = 2
MAX_INGREDIENT_LENGTH = 50

MAX_TOTAL_INPUT_LENGTH = 500

MIN_SERVINGS = 1
MAX_SERVINGS = 20


# Validate Input

def validate_input(
    ingredients,
    servings=1,
):
    """
    Validate recipe generation input.

    Returns:
    {
        "valid": bool,
        "errors": [],
        "warnings": []
    }

    NOTE:
    This function ONLY validates data.
    Cleaning, normalization, synonym mapping,
    spelling correction, etc. are handled
    in preprocessor.py.
    """

    errors = []
    warnings = []

    if ingredients is None:
        errors.append(
            "Ingredient list is required."
        )

    elif not isinstance(
        ingredients,
        list,
    ):
        errors.append(
            "Ingredients must be provided as a list."
        )

    else:

        if len(ingredients) < MIN_INGREDIENTS:
            errors.append(
                "At least one ingredient is required."
            )

        if len(ingredients) > MAX_INGREDIENTS:
            errors.append(
                f"Maximum {MAX_INGREDIENTS} ingredients are allowed."
            )

        total_length = sum(
            len(str(item))
            for item in ingredients
        )

        if total_length > MAX_TOTAL_INPUT_LENGTH:
            errors.append(
                "Total ingredient input is too long."
            )

        seen = set()

        for index, ingredient in enumerate(
            ingredients,
            start=1,
        ):

            if ingredient is None:
                errors.append(
                    f"Ingredient {index} cannot be empty."
                )
                continue

            if not isinstance(
                ingredient,
                str,
            ):
                errors.append(
                    f"Ingredient {index} must be a string."
                )
                continue

            ingredient = ingredient.strip()

            if ingredient == "":
                errors.append(
                    f"Ingredient {index} cannot be blank."
                )
                continue

            if len(ingredient) < MIN_INGREDIENT_LENGTH:
                errors.append(
                    f'"{ingredient}" is too short.'
                )

            if len(ingredient) > MAX_INGREDIENT_LENGTH:
                errors.append(
                    f'"{ingredient}" is too long.'
                )

            if ingredient.isdigit():
                errors.append(
                    f'"{ingredient}" cannot contain only numbers.'
                )

            if not re.fullmatch(
                r"[A-Za-z\\s\\-]+",
                ingredient,
            ):
                errors.append(
                    f'"{ingredient}" contains invalid characters.'
                )

            normalized = ingredient.lower()

            if normalized in seen:
                warnings.append(
                    f'Duplicate ingredient "{ingredient}" found.'
                )
            else:
                seen.add(normalized)

    if not isinstance(
        servings,
        int,
    ):
        errors.append(
            "Servings must be an integer."
        )

    else:

        if servings < MIN_SERVINGS:
            errors.append(
                "Servings must be greater than zero."
            )

        if servings > MAX_SERVINGS:
            errors.append(
                f"Maximum servings allowed is {MAX_SERVINGS}."
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }