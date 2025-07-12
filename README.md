# FireEngine

FireEngine is a pseudo-3D raycasting game engine written in Python, inspired by classic games like Wolfenstein 3D. It is built on top of the [Arcade](https://api.arcade.academy/en/latest/) library and features a flexible system for creating custom game content.

## ✨ Features

- **Pseudo-3D Rendering:** Uses raycasting to render walls and textured floors/ceilings with GLSL shaders.
- **Sprite & Entity System:** Supports dynamic 2D sprites for enemies, items, and decorations, with automatic sorting by distance.
- **Data-Driven Content:** Game objects, scenes, textures, and weapons are defined in simple `.dat` and `.scene` files, allowing for easy modification and expansion without changing engine code.
- **Game Manager:** A central manager handles game state, automatically registering and calling update/render methods on all game objects.
- **Player & Controls:** Includes a first-person player controller with movement, collision detection, and combat mechanics.
- **Resource Management:** A robust system for loading textures, sounds, animations, and game data from the `Game/` directory.
- **Basic AI:** Enemies have simple patrol, line-of-sight detection, and combat behaviors.
- **UI System:** Provides a basic UI for displaying health, score, and a crosshair, plus a debug overlay.

## 📂 Project Structure

The project is organized into two main parts: the engine and the game content.

```
├── FireEngine/       # Core engine code
│   ├── core/         # Engine fundamentals (manager, rendering, resource loading)
│   ├── objects/      # Base classes for game objects (entities, sprites)
│   ├── player/       # Player logic and interaction system
│   └── ui/           # Game UI and debug overlay
│
├── Game/             # Game-specific assets and data
│   ├── Assets/       # Textures and audio files
│   ├── Objects/      # Data files (.dat, .scene) defining all game content
│   └── Code/         # Game-specific scripts
│
├── Mods/             # Directory for user-created mods (currently unused)
│
└── main.py           # Main entry point to run the game
```

## ⚙️ How It Works

FireEngine uses a combination of modern and classic techniques to create its 3D world.

### Game Manager & Decorators
The engine is built around a central `game_manager` instance. Game objects (like the player, enemies, or UI elements) are automatically registered with this manager using the `@register` decorator. The manager then calls specific methods on these objects during the game loop (`on_update`, `on_render`, `on_key_press`, etc.). This creates a decoupled and event-driven architecture.

### Data-Driven Design
All game content is loaded from the `Game/Objects/` directory.
- **`.scene` files:** These are simple text files that define the layout of a level. Different characters represent walls, player spawn points, enemies, and items.
- **`.dat` files:** These are configuration files (`configparser` format) that define the properties of textures, enemies, weapons, and other objects. They link assets (like PNGs and WAVs) to game logic and define attributes like health, speed, and damage.

### Rendering Pipeline
The 3D scene is rendered in layers:
1.  **Floor & Ceiling:** A full-screen quad is rendered using GLSL shaders (`floor.frag`, `ceiling.frag`) to create the perspective effect for textured floors and ceilings.
2.  **Walls:** The engine casts rays from the player's position for each column of pixels on the screen. When a ray hits a wall, the distance is calculated to determine the height of the wall slice to be drawn. This is the core of the raycasting algorithm. A Z-buffer is populated with these distances.
3.  **Sprites & Entities:** All 3D objects (enemies, items) are sorted by their distance from the player (farthest to nearest). They are then drawn one by one. The Z-buffer is checked to ensure sprites are correctly drawn in front of or behind walls.

## 🚀 Creating Content

You can easily create your own content for the engine.

### 1. Define a Texture
- Add a texture image to `Game/Assets/Textures/`.
- Create a `.dat` file in `Game/Objects/Textures/` to define its properties, including the icon that will represent it in `.scene` files.

### 2. Create an Entity (Enemy)
- Add an animation sprite sheet to `Game/Assets/Textures/Entities/`.
- Create a `.dat` file in `Game/Objects/Entities/` specifying the entity's stats (health, speed), animation sheet, sounds, and the icon used to place it in a map.

### 3. Design a Scene
- Create a `.scene` file in `Game/Objects/Scenes/`.
- Draw your map layout using characters defined in your `.dat` files. Here are some defaults:
  - `W`, `#`: Wall textures
  - `*`: Player spawn point
  - `$`, `S`: Enemy spawn points
  - `D`: A door
  - `H`, `p`, `l`, `b`: Item pickups

### 4. Run the Game
Execute the main script to play your creation:
```bash
python main.py
```

## 🎯 Future Goals & Roadmap

FireEngine is under active development with an ambitious roadmap. The goal is to evolve it from a classic raycaster into a more powerful and modern pseudo-3D engine, while retaining the simplicity and moddability of Python.

Here are some of the major features and improvements planned:

-   **Entity Component System (ECS):** A complete rewrite of the data management system to implement a flexible ECS architecture, similar to how modern engines like Unity handle game objects and their data.

-   **GPU-Powered Rendering:** Overhaul the rendering pipeline to be fully GPU-accelerated. This includes:
    -   **Batching & Chunking:** Optimize rendering by batching draw calls and loading the world in chunks.
    -   **Doom-Style Maps:** Move beyond simple grid-based maps to support non-orthogonal walls and varying floor/ceiling heights for more dynamic and complex level design.

-   **Advanced Effects & Shaders:**
    -   **Voxel-Based Systems:** Implement voxel-based lighting and spatial audio to create more realistic and immersive environments.
    -   **Custom Shader Pipeline:** Develop a system that allows for post-processing effects like color grading, depth of field (DoF), and ambient occlusion (AO).

-   **Developer & Modding Tools:**
    -   **Visual Editor GUI:** Create a dedicated GUI for designing maps, editing game objects, and managing assets, inspired by the Unity editor.
    -   **VS Code Extension:** Build a plugin for Visual Studio Code to streamline game and mod development, allowing for rapid iteration and in-editor testing.
    -   **Robust Modding API:** Formalize and document a powerful modding system to make it easy for the community to create and share content.

-   **Deployment & Networking:**
    -   **Secure Build System:** Create a build process that obfuscates the source code to prepare a game for secure deployment.
    -   **Multiplayer Networking:** Implement a networking solution to allow for multiplayer game modes.

-   **Core Optimization:** Continuously optimize all parts of the engine to ensure it runs as fast as possible, leveraging the strengths of Python for its ease of use and modding capabilities.

## 📦 Dependencies

- **Python 3.9+**
- **Arcade:** `pip install arcade`
- **Pydub:** `pip install pydub` (for audio conversion)
- **Chardet:** `pip install chardet` (for detecting file encodings)
- **OpenAL:** May require installing the OpenAL Soft library on your system for spatial audio to work.
