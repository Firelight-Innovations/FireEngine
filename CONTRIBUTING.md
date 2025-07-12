# Contributing to FireEngine

First off, thank you for considering contributing to FireEngine! We welcome any help, whether it's fixing bugs, adding new features, or improving documentation.

## How to Contribute

We encourage you to contribute to the project! Please follow these steps:

1.  **Fork the Repository:** Start by forking the main repository to your own GitHub account.

2.  **Create a New Branch:** Create a new branch for your changes. Use a descriptive name that summarizes your work, like `feature/new-weapon-system` or `bugfix/player-collision-error`.
    ```bash
    git checkout -b your-branch-name
    ```

3.  **Make Your Changes:** Make your changes to the code. Please adhere to the coding style and conventions already present in the project.

4.  **Commit Your Changes:** Write a clear and concise commit message. A good commit message should explain *what* the change is and *why* it was made.
    ```bash
    git commit -m "feat: Add rocket launcher and corresponding ammo type"
    ```

5.  **Push to Your Branch:** Push your changes to your forked repository.
    ```bash
    git push origin your-branch-name
    ```

6.  **Submit a Pull Request:** Open a pull request from your branch to the `main` branch of the original repository. In the description, please provide details about the changes you made.

## Development Guidelines

To maintain the quality and consistency of the codebase, please keep the following guidelines in mind:

### Coding Style

- **Follow Existing Conventions:** The most important rule is to follow the style and patterns of the existing code. Look at the surrounding files to understand the project's conventions for naming, formatting, and architecture.
- **Python Style:** The project follows standard Python style guidelines (PEP 8).
- **Comments:** Add comments only when necessary to explain complex logic. Focus on the *why*, not the *what*.

### Creating New Content

FireEngine is a data-driven engine. When adding new game elements, please use the existing systems:

- **Game Objects:** New entities, sprites, weapons, and items should be defined in `.dat` files in the `Game/Objects/` directory.
- **Scenes:** New levels should be created as `.scene` files.
- **Engine Code:** Only modify the core `FireEngine/` code if you are adding a new engine-level feature or fixing a bug. New weapons or enemies should not require changes to the engine itself.

### Submitting Pull Requests

When you submit a pull request, please ensure the following:

- **Clear Description:** Your PR description should clearly explain the purpose of your changes. If it fixes an issue, please reference the issue number (e.g., `Fixes #42`).
- **Testing:** While the project currently lacks a formal testing suite, please ensure that your changes do not break existing functionality. Test your changes in a few different scenes to confirm they work as expected.

Thank you again for your interest in contributing!