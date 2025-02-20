#version 330 core

in vec2 in_vert;
out vec2 frag_pos;

void main()
{
    frag_pos = in_vert;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
