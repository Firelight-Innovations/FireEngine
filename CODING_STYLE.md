# FireEngine Coding Style Guide

## Introduction

This document provides the coding conventions for the FireEngine project. Adhering to these guidelines will help maintain code consistency, readability, and quality.

## File Naming

- **File names should be in `snake_case`** (e.g., `resource_loading.py`, `game_ui.py`).

## Naming Conventions

- **Classes:** Use `PascalCase` (e.g., `GameManager`, `AudioSource`).
- **Functions and Methods:** Use `snake_case` (e.g., `play_next_song`, `draw_objects`).
- **Variables:** Use `snake_case` (e.g., `current_song_index`, `object_distances`).
- **Constants:** Use `UPPER_SNAKE_CASE` (e.g., `SCREEN_WIDTH`, `MAX_DEPTH`).

## Docstrings

- **All classes and public methods should have docstrings.**
- **Use the following format for docstrings:**

```python
def my_function(param1: int, param2: str) -> bool:
    """
    Brief description of the function.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter.

    Returns:
        Description of the return value.
    """
    # function body
    pass
```

## Type Hinting

- **Use type hints for all function signatures and variable declarations.** This improves code clarity and allows for static analysis.

## Imports

- **Imports should be placed at the top of the file.**
- **Exception:** To avoid circular dependencies or for lazy loading, imports can be placed inside functions or methods. This is a common pattern in this project and should be used when necessary.

## Decorators

The project uses the following custom decorators:

- **`@singleton`**: Ensures that only one instance of a class is created.
- **`@register`**: Automatically registers a class with the `GameManager`.

## Code Structure

- **Organize code into classes and functions with clear responsibilities.**
- **Keep classes focused on a single purpose.**
- **Use comments to explain complex logic, not to describe what the code does.**

## Class Instantiation

- A common pattern in this project is to instantiate a class at the end of the file (e.g., `Game = GameManager()`). This is used to create singleton-like objects that are easily accessible from other parts of the codebase.
