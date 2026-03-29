"""
OJT Project Custom Exceptions

OOP Concept Demonstrated: EXCEPTION HANDLING AND INHERITANCE
=======================================================================
This file demonstrates custom exception classes that inherit from Python's
built-in Exception class. Exception handling is a crucial OOP concept that
allows programs to gracefully handle errors and unexpected situations.

Key Points about Exception Handling in OOP:
1. Exceptions are objects (instances of exception classes)
2. Custom exceptions inherit from built-in Exception classes
3. They can carry additional data about the error
4. try-except blocks catch and handle exceptions
5. Custom exceptions make error handling more specific and meaningful

Inheritance Hierarchy for our exceptions:
    BaseException (Python built-in)
        └── Exception (Python built-in)
            └── OJTBaseException (our custom base)
                ├── OJTValidationError (validation errors)
                ├── OJTPermissionError (permission errors)
                └── OJTNotFoundError (resource not found)
=======================================================================
"""


class OJTBaseException(Exception):
    """
    Base exception class for OJT Management System.

    OOP Concept: INHERITANCE from built-in classes
    ---------------------------------------------
    This class inherits from Python's built-in Exception class.
    All custom exceptions in this project inherit from this base class.

    This demonstrates:
    1. Inheritance: OJTBaseException IS-A Exception
    2. Encapsulation: We encapsulate error details in instance variables
    3. Polymorphism: This exception can be caught as Exception or OJTBaseException

    Example usage:
        try:
            raise OJTBaseException("Something went wrong", "ERROR_CODE")
        except OJTBaseException as e:
            print(f"Error: {e.message}, Code: {e.error_code}")
    """

    def __init__(self, message, error_code=None):
        """
        Initialize the exception with a message and optional error code.

        OOP Concept: Constructor (__init__)
        ----------------------------------
        The constructor initializes instance variables (self.message, self.error_code)
        and calls the parent class constructor using super().

        Args:
            message (str): Human-readable error message
            error_code (str, optional): Machine-readable error code
        """
        # Call parent class constructor - this is the proper way to extend __init__
        super().__init__(message)

        # Instance variables (encapsulation)
        self.message = message
        self.error_code = error_code

    def __str__(self):
        """
        String representation of the exception.

        OOP Concept: Method Overriding
        -----------------------------
        We override the __str__ method from the base Exception class
        to provide a custom string representation.

        Returns:
            str: Formatted error message
        """
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class OJTValidationError(OJTBaseException):
    """
    Exception raised when validation fails.

    OOP Concept: SPECIALIZED SUBCLASS
    --------------------------------
    This class inherits from OJTBaseException and specializes it
    for validation-related errors.

    When to raise this exception:
    1. A student tries to edit an approved journal
    2. A DTR log has time_out before time_in
    3. Required hours is set to zero or negative
    4. Invalid data is submitted to a form

    Example:
        if journal.status == 'approved':
            raise OJTValidationError(
                "Cannot edit an approved journal",
                "JOURNAL_ALREADY_APPROVED"
            )
    """

    def __init__(self, message, error_code="VALIDATION_ERROR", field_name=None):
        """
        Initialize validation error with optional field name.

        Args:
            message (str): Description of the validation error
            error_code (str): Error code for programmatic handling
            field_name (str, optional): Name of the field that failed validation
        """
        super().__init__(message, error_code)
        self.field_name = field_name

    def __str__(self):
        """Override to include field name if present."""
        base_msg = super().__str__()
        if self.field_name:
            return f"{base_msg} (field: {self.field_name})"
        return base_msg


class OJTPermissionError(OJTBaseException):
    """
    Exception raised when a user lacks permission for an action.

    OOP Concept: Access Control through Exceptions
    ---------------------------------------------
    This exception is used to enforce role-based access control.
    When a user tries to access a resource they don't have permission
    for, this exception is raised.

    Example:
        if request.user.role != 'teacher':
            raise OJTPermissionError(
                "Only teachers can approve journals",
                "TEACHER_REQUIRED"
            )
    """

    def __init__(self, message, error_code="PERMISSION_DENIED", required_role=None):
        """
        Initialize permission error with optional required role.

        Args:
            message (str): Description of the permission error
            error_code (str): Error code for programmatic handling
            required_role (str, optional): The role required for the action
        """
        super().__init__(message, error_code)
        self.required_role = required_role


class OJTNotFoundError(OJTBaseException):
    """
    Exception raised when a requested resource is not found.

    OOP Concept: Semantic Exception Handling
    --------------------------------------
    Instead of using generic exceptions, we use specific exception
    types that communicate what went wrong. This makes error handling
    more precise and code more readable.

    Example:
        try:
            student = User.objects.get(pk=student_id, role='student')
        except User.DoesNotExist:
            raise OJTNotFoundError(
                f"Student with ID {student_id} not found",
                "STUDENT_NOT_FOUND"
            )
    """

    def __init__(self, message, error_code="NOT_FOUND", resource_type=None, resource_id=None):
        """
        Initialize not found error with resource details.

        Args:
            message (str): Description of what wasn't found
            error_code (str): Error code for programmatic handling
            resource_type (str, optional): Type of resource (e.g., "Student", "Journal")
            resource_id (optional): ID of the resource that wasn't found
        """
        super().__init__(message, error_code)
        self.resource_type = resource_type
        self.resource_id = resource_id


# Usage examples demonstrating exception handling patterns
"""
OOP Concept: EXCEPTION HANDLING PATTERNS

Pattern 1: Basic try-except
---------------------------
try:
    # Code that might raise an exception
    validate_journal(journal)
except OJTValidationError as e:
    # Handle the specific exception
    messages.error(request, str(e))

Pattern 2: Multiple except blocks (polymorphism)
------------------------------------------------
try:
    submit_dtr_log(student, data)
except OJTValidationError as e:
    # Handle validation errors
    return render(request, 'error.html', {'error': e.message})
except OJTPermissionError as e:
    # Handle permission errors
    return redirect('login')
except OJTBaseException as e:
    # Catch any other OJT exception
    logger.error(f"OJT Error: {e}")

Pattern 3: Re-raising exceptions
-------------------------------
try:
    process_data(data)
except OJTBaseException:
    # Log and re-raise
    logger.exception("Error processing data")
    raise

Pattern 4: Exception chaining
-----------------------------
try:
    external_api_call()
except APIError as e:
    raise OJTValidationError("External service failed") from e
"""
