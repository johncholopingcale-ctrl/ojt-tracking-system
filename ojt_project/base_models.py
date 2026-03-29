"""
OJT Project Base Models

OOP Concept Demonstrated: ABSTRACTION
=======================================================================
This file contains abstract base classes that cannot be instantiated directly.
Abstract classes define a common interface and shared behavior that subclasses
must implement or inherit.

Key Points about Abstraction:
1. Abstract classes define "what" an object does, not "how" it does it
2. They provide a template for subclasses to follow
3. They enforce a contract - subclasses MUST implement abstract methods
4. They can contain both abstract methods and concrete implementations

In this file:
- OJTBaseModel is an ABSTRACT class (class Meta: abstract = True)
- It defines common fields (created_at, updated_at) that ALL subclasses inherit
- It declares an abstract method get_display_info() that subclasses MUST implement
- You CANNOT create an OJTBaseModel object directly - only its subclasses
=======================================================================
"""

from django.db import models
from abc import abstractmethod


class OJTBaseModel(models.Model):
    """
    Abstract Base Model for OJT System entities.

    OOP Concept: ABSTRACTION
    -----------------------
    This is an ABSTRACT CLASS - it cannot be instantiated directly.
    It serves as a blueprint/template for concrete model classes.

    Why use abstraction?
    1. Code Reuse: Common fields (created_at, updated_at) are defined once
    2. Consistency: All subclasses will have the same timestamp fields
    3. Contract: Subclasses must implement get_display_info() method

    Example of what you CANNOT do:
        obj = OJTBaseModel()  # This will raise an error!

    Example of what you CAN do:
        class Journal(OJTBaseModel):  # Inherit from abstract class
            content = models.TextField()

            def get_display_info(self):  # Implement the abstract method
                return f"Journal submitted"

        journal = Journal()  # This works! Journal is a concrete class
    """

    # These fields are inherited by ALL subclasses
    # OOP Concept: Inheritance of attributes
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Automatically set when the object is first created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Automatically updated every time the object is saved"
    )

    class Meta:
        # This is what makes the class ABSTRACT
        # Django will NOT create a database table for this model
        abstract = True

    def get_display_info(self):
        """
        Abstract method that subclasses MUST implement.

        OOP Concept: Abstract Method
        ---------------------------
        This method defines WHAT subclasses should do (return display info)
        but not HOW they should do it. Each subclass implements this
        differently based on its specific data.

        This is part of the "contract" that abstract classes establish.
        If a subclass doesn't implement this method, Python will raise
        a NotImplementedError when it's called.

        Returns:
            str: A human-readable summary of the object
        """
        raise NotImplementedError(
            "Subclasses of OJTBaseModel must implement get_display_info() method. "
            "This is an abstract method that defines the contract for all OJT entities."
        )

    def get_created_date_formatted(self):
        """
        Concrete method that all subclasses inherit and can use as-is.

        OOP Concept: Concrete method in abstract class
        ---------------------------------------------
        Abstract classes can have both abstract methods (must be overridden)
        and concrete methods (can be used directly or overridden).

        Returns:
            str: Formatted creation date
        """
        return self.created_at.strftime("%B %d, %Y at %I:%M %p")

    def get_updated_date_formatted(self):
        """
        Another concrete method that provides common functionality.

        Returns:
            str: Formatted last update date
        """
        return self.updated_at.strftime("%B %d, %Y at %I:%M %p")


class TimestampMixin(models.Model):
    """
    Mixin class for adding timestamp fields.

    OOP Concept: MIXIN CLASSES
    -------------------------
    A mixin is a class that provides methods and attributes to other classes
    through multiple inheritance. Unlike regular inheritance, mixins:
    1. Are designed to be combined with other classes
    2. Usually don't work standalone
    3. Add specific functionality without creating deep inheritance hierarchies

    Usage:
        class MyModel(TimestampMixin, models.Model):
            name = models.CharField(max_length=100)
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
