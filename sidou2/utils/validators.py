# Import necessary modules
import re  # Regular expression module, used for pattern matching in strings (e.g., for email and phone validation)
from utils.error_handler import (
    ValidationError,
)  # Custom exception class for handling validation-specific errors


# --- General Purpose Validators ---


def validate_required(value, field_name):
    """
    Validates that a given field/value is not empty or just whitespace.

    Args:
        value: The value to validate.
        field_name (str): The user-friendly name of the field being validated (e.g., "Nom du produit").

    Raises:
        ValidationError: If the value is empty or None.

    Returns:
        The original value if it's valid.
    """
    # Check if the value is None, or if it's a string that is empty or contains only whitespace.
    if not value or (isinstance(value, str) and value.strip() == ""):
        raise ValidationError(
            f"{field_name} est requis."
        )  # Raise an error if validation fails.
    return value  # Return the value if it passes validation.


def validate_numeric(value, field_name, min_value=None, max_value=None):
    """
    Validates that a value can be converted to a float and optionally checks if it
    falls within a specified minimum and maximum range.

    Args:
        value: The value to validate.
        field_name (str): The user-friendly name of the field.
        min_value (float, optional): The minimum allowed value. Defaults to None.
        max_value (float, optional): The maximum allowed value. Defaults to None.

    Raises:
        ValidationError: If the value is not numeric or falls outside the specified range.

    Returns:
        float: The validated numeric value.
    """
    try:
        num_value = float(value)  # Attempt to convert the value to a float.

        # Check if a minimum value is specified and if the number is less than it.
        if min_value is not None and num_value < min_value:
            raise ValidationError(
                f"{field_name} doit être supérieur ou égal à {min_value}."
            )

        # Check if a maximum value is specified and if the number is greater than it.
        if max_value is not None and num_value > max_value:
            raise ValidationError(
                f"{field_name} doit être inférieur ou égal à {max_value}."
            )

        return num_value  # Return the validated float value.
    except (ValueError, TypeError):  # Catch errors if conversion to float fails.
        raise ValidationError(f"{field_name} doit être une valeur numérique.")


def validate_integer(value, field_name, min_value=None, max_value=None):
    """
    Validates that a value can be converted to an integer and optionally checks
    if it falls within a specified minimum and maximum range.

    Args:
        value: The value to validate.
        field_name (str): The user-friendly name of the field.
        min_value (int, optional): The minimum allowed integer value. Defaults to None.
        max_value (int, optional): The maximum allowed integer value. Defaults to None.

    Raises:
        ValidationError: If the value is not an integer or falls outside the specified range.

    Returns:
        int: The validated integer value.
    """
    try:
        # First, try to convert to float to catch non-numeric strings, then to int.
        float_value = float(value)
        int_value = int(float_value)

        # Check if the float value is different from its integer conversion (e.g., 3.14 vs 3).
        if float_value != int_value:
            raise ValidationError(f"{field_name} doit être un nombre entier.")

        # Check if a minimum value is specified and if the integer is less than it.
        if min_value is not None and int_value < min_value:
            raise ValidationError(
                f"{field_name} doit être supérieur ou égal à {min_value}."
            )

        # Check if a maximum value is specified and if the integer is greater than it.
        if max_value is not None and int_value > max_value:
            raise ValidationError(
                f"{field_name} doit être inférieur ou égal à {max_value}."
            )

        return int_value  # Return the validated integer value.
    except (
        ValueError,
        TypeError,
    ):  # Catch errors if conversion to int (via float) fails.
        raise ValidationError(f"{field_name} doit être un nombre entier.")


def validate_email(email):
    """
    Validates the format of an email address using a regular expression.
    Allows empty or None emails as they might be optional fields.

    Args:
        email (str): The email address string to validate.

    Raises:
        ValidationError: If the email format is invalid.

    Returns:
        str: The original email string if valid or if it's empty/None.
    """
    # If the email is None or an empty string (or whitespace), consider it valid (optional field).
    if not email or email.strip() == "":
        return email

    # Regular expression for a common email pattern.
    # - Starts with one or more alphanumeric characters, dots, underscores, percent, plus, or hyphen.
    # - Followed by an '@' symbol.
    # - Followed by one or more alphanumeric characters or hyphens (domain name).
    # - Followed by a '.' symbol.
    # - Ends with 2 or more alphabetic characters (top-level domain).
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    if not email_pattern.match(email):  # Check if the email matches the pattern.
        raise ValidationError("Format d'email invalide.")

    return email  # Return the email if valid.


def validate_phone(phone):
    """
    Validates the format of a phone number.
    Allows empty or None phone numbers as they might be optional.
    Cleans the phone number by removing common separators before validation.

    Args:
        phone (str): The phone number string to validate.

    Raises:
        ValidationError: If the phone number format is invalid after cleaning.

    Returns:
        str: The original phone string if valid or if it's empty/None.
    """
    # If the phone number is None or an empty string (or whitespace), consider it valid (optional field).
    if not phone or phone.strip() == "":
        return phone

    # Remove common phone number separators like spaces, hyphens, and parentheses.
    clean_phone = re.sub(r"[\s\-\(\)]", "", phone)

    # Regular expression for a basic phone number pattern:
    # - Optional '+' at the beginning (for country codes).
    # - Followed by 8 to 15 digits.
    # This is a general pattern; for specific country formats, a more precise regex would be needed.
    phone_pattern = re.compile(r"^\+?[0-9]{8,15}$")
    if not phone_pattern.match(
        clean_phone
    ):  # Check if the cleaned phone number matches the pattern.
        raise ValidationError("Format de numéro de téléphone invalide.")

    return phone  # Return the original phone string if valid.


# --- Application-Specific Validators ---


def validate_product_data(name, purchase_price, selling_price, quantity=None):
    """
    Validates a set of data fields typically associated with a product.
    Uses the general-purpose validators defined above.

    Args:
        name (str): The name of the product.
        purchase_price (float/str): The purchase price of the product.
        selling_price (float/str): The selling price of the product.
        quantity (int/str, optional): The quantity of the product. Defaults to None if not applicable.

    Raises:
        ValidationError: If any of the product fields fail their respective validations.

    Returns:
        tuple: A tuple containing the validated (and possibly type-converted)
               name, purchase_price, selling_price, and quantity.
    """
    validate_required(name, "Nom du produit")  # Product name is required.

    # Validate purchase price: must be numeric and not negative.
    purchase_price = validate_numeric(purchase_price, "Prix d'achat", min_value=0)
    # Validate selling price: must be numeric and not negative.
    selling_price = validate_numeric(selling_price, "Prix de vente", min_value=0)

    # If quantity is provided, validate it: must be an integer and not negative.
    if quantity is not None:
        quantity = validate_integer(quantity, "Quantité", min_value=0)

    return name, purchase_price, selling_price, quantity


def validate_customer_data(name, phone=None, email=None):
    """
    Validates a set of data fields typically associated with a customer.

    Args:
        name (str): The name of the customer.
        phone (str, optional): The customer's phone number. Defaults to None.
        email (str, optional): The customer's email address. Defaults to None.

    Raises:
        ValidationError: If any of the customer fields fail their respective validations.

    Returns:
        tuple: A tuple containing the validated name, phone (if provided), and email (if provided).
    """
    validate_required(name, "Nom du client")  # Customer name is required.

    # If a phone number is provided, validate its format.
    if phone:
        phone = validate_phone(phone)

    # If an email address is provided, validate its format.
    if email:
        email = validate_email(email)

    return name, phone, email
