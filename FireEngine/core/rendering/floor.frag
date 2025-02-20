#version 330 core

uniform float SCREEN_WIDTH;
uniform float SCREEN_HEIGHT;

// posZ is how high the camera is above the "floor." E.g., 0.5 * SCREEN_HEIGHT.
uniform float posZ;

// Player position
uniform vec2 playerPos;

// Leftmost and rightmost ray directions
uniform vec2 rayDir0;
uniform vec2 rayDir1;

// Floor texture. Make sure it's set to REPEAT wrap mode in Python
uniform sampler2D floor_texture;

out vec4 fragColor;

void main()
{
    // Convert the current fragment’s coordinates
    float xScreen = gl_FragCoord.x;                 // 0 .. SCREEN_WIDTH-1
    float yScreen = gl_FragCoord.y;                 // 0 .. SCREEN_HEIGHT-1

    if (yScreen >= SCREEN_HEIGHT / 2.0) {
        discard;
    }

    float p = yScreen - (SCREEN_HEIGHT * 0.5);

    // Avoid division by zero
    if (abs(p) < 0.000001) {
        p = 0.000001;
    }

    float rowDistance = posZ / -p;

    // X/Y increments for each pixel in this row
    float floorStepX = rowDistance * (rayDir1.x - rayDir0.x) / SCREEN_WIDTH;
    float floorStepY = rowDistance * (rayDir1.y - rayDir0.y) / SCREEN_WIDTH;

    // Starting floorX/floorY for the leftmost column
    float floorX = playerPos.x + rowDistance * rayDir0.x;
    float floorY = playerPos.y + rowDistance * rayDir0.y;

    // Advance by xScreen worth of steps
    floorX += floorStepX * xScreen;
    floorY += floorStepY * xScreen;

    // We only actually need the fractional part for sampling
    float cellX = floor(floorX);
    float cellY = floor(floorY);

    float fracX = floorX - cellX;
    float fracY = floorY - cellY;

    // Sample the floor texture with fractional coords in [0..1].
    // For EXACT behavior (wrapping), set TEXTURE_WRAP to REPEAT in Python.
    // e.g., floor_gl_texture.wrap_x = arcade.gl.REPEAT;
    //       floor_gl_texture.wrap_y = arcade.gl.REPEAT;
    vec4 floorColor = texture(floor_texture, vec2(fracX, fracY));

    // Write final color
    fragColor = floorColor;
}
