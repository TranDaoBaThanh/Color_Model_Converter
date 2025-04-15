# File: main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
import cv2
import moderngl
import base64
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize ModernGL context
ctx = moderngl.create_standalone_context()

# Shader programs for each color model conversion
shaders = {}

# Common vertex shader for all models
vertex_shader = """
#version 330

in vec2 in_position;
in vec2 in_texcoord;

out vec2 texcoord;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    texcoord = in_texcoord;
}
"""

# Fragment shaders for each color model

# RGB to Grayscale shader
grayscale_fragment_shader = """
#version 330

in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D texture0;
uniform float param1; // Weight for red channel
uniform float param2; // Weight for green channel
uniform float param3; // Weight for blue channel

void main() {
    vec4 color = texture(texture0, texcoord);
    float gray = param1 * color.r + param2 * color.g + param3 * color.b;
    fragColor = vec4(gray, gray, gray, color.a);
}
"""

# RGB to HSV shader
hsv_fragment_shader = """
#version 330

in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D texture0;
uniform float param1; // Hue adjustment
uniform float param2; // Saturation adjustment
uniform float param3; // Value adjustment

// RGB to HSV conversion
vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

// HSV to RGB conversion
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec4 color = texture(texture0, texcoord);
    vec3 hsv = rgb2hsv(color.rgb);
    
    // Apply adjustments
    hsv.x = mod(hsv.x + param1, 1.0); // Hue adjustment
    hsv.y = clamp(hsv.y * param2, 0.0, 1.0); // Saturation adjustment
    hsv.z = clamp(hsv.z * param3, 0.0, 1.0); // Value adjustment
    
    vec3 rgb = hsv2rgb(hsv);
    fragColor = vec4(rgb, color.a);
}
"""

# RGB to CMYK shader
cmyk_fragment_shader = """
#version 330

in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D texture0;
uniform float param1; // Cyan adjustment
uniform float param2; // Magenta adjustment
uniform float param3; // Yellow adjustment
uniform float param4; // Key (black) adjustment

// RGB to CMYK
vec4 rgb2cmyk(vec3 rgb) {
    float k = 1.0 - max(max(rgb.r, rgb.g), rgb.b);
    float c = (1.0 - rgb.r - k) / (1.0 - k);
    float m = (1.0 - rgb.g - k) / (1.0 - k);
    float y = (1.0 - rgb.b - k) / (1.0 - k);
    
    return vec4(c, m, y, k);
}

// CMYK to RGB
vec3 cmyk2rgb(vec4 cmyk) {
    float c = cmyk.x;
    float m = cmyk.y;
    float y = cmyk.z;
    float k = cmyk.w;
    
    float r = (1.0 - c) * (1.0 - k);
    float g = (1.0 - m) * (1.0 - k);
    float b = (1.0 - y) * (1.0 - k);
    
    return vec3(r, g, b);
}

void main() {
    vec4 color = texture(texture0, texcoord);
    vec4 cmyk = rgb2cmyk(color.rgb);
    
    // Apply adjustments
    cmyk.x = clamp(cmyk.x * param1, 0.0, 1.0); // Cyan adjustment
    cmyk.y = clamp(cmyk.y * param2, 0.0, 1.0); // Magenta adjustment
    cmyk.z = clamp(cmyk.z * param3, 0.0, 1.0); // Yellow adjustment
    cmyk.w = clamp(cmyk.w * param4, 0.0, 1.0); // Key adjustment
    
    vec3 rgb = cmyk2rgb(cmyk);
    fragColor = vec4(rgb, color.a);
}
"""

# RGB to YIQ shader
yiq_fragment_shader = """
#version 330

in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D texture0;
uniform float param1; // Y adjustment
uniform float param2; // I adjustment
uniform float param3; // Q adjustment

// RGB to YIQ matrix
const mat3 rgb2yiq_matrix = mat3(
    0.299, 0.587, 0.114,
    0.596, -0.274, -0.322,
    0.211, -0.523, 0.312
);

// YIQ to RGB matrix
const mat3 yiq2rgb_matrix = mat3(
    1.0, 0.956, 0.621,
    1.0, -0.272, -0.647,
    1.0, -1.105, 1.702
);

void main() {
    vec4 color = texture(texture0, texcoord);
    vec3 yiq = rgb2yiq_matrix * color.rgb;
    
    // Apply adjustments
    yiq.x = clamp(yiq.x * param1, 0.0, 1.0); // Y adjustment
    yiq.y = clamp(yiq.y * param2, -0.6, 0.6); // I adjustment
    yiq.z = clamp(yiq.z * param3, -0.6, 0.6); // Q adjustment
    
    vec3 rgb = yiq2rgb_matrix * yiq;
    fragColor = vec4(clamp(rgb, 0.0, 1.0), color.a);
}
"""

# RGB to YUV shader
yuv_fragment_shader = """
#version 330

in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D texture0;
uniform float param1; // Y adjustment
uniform float param2; // U adjustment
uniform float param3; // V adjustment

// RGB to YUV matrix (BT.601)
const mat3 rgb2yuv_matrix = mat3(
    0.299, 0.587, 0.114,
    -0.14713, -0.28886, 0.436,
    0.615, -0.51499, -0.10001
);

// YUV to RGB matrix (BT.601)
const mat3 yuv2rgb_matrix = mat3(
    1.0, 0.0, 1.13983,
    1.0, -0.39465, -0.58060,
    1.0, 2.03211, 0.0
);

void main() {
    vec4 color = texture(texture0, texcoord);
    vec3 yuv = rgb2yuv_matrix * color.rgb;
    
    // Apply adjustments
    yuv.x = clamp(yuv.x * param1, 0.0, 1.0); // Y adjustment
    yuv.y = clamp(yuv.y * param2, -0.5, 0.5); // U adjustment
    yuv.z = clamp(yuv.z * param3, -0.5, 0.5); // V adjustment
    
    vec3 rgb = yuv2rgb_matrix * yuv;
    fragColor = vec4(clamp(rgb, 0.0, 1.0), color.a);
}
"""

# RGB to YCbCr shader
ycbcr_fragment_shader = """
#version 330

in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D texture0;
uniform float param1; // Y adjustment
uniform float param2; // Cb adjustment
uniform float param3; // Cr adjustment

// RGB to YCbCr matrix (BT.601)
const mat3 rgb2ycbcr_matrix = mat3(
    0.299, 0.587, 0.114,
    -0.168736, -0.331264, 0.5,
    0.5, -0.418688, -0.081312
);

// YCbCr to RGB matrix (BT.601)
const mat3 ycbcr2rgb_matrix = mat3(
    1.0, 0.0, 1.402,
    1.0, -0.344136, -0.714136,
    1.0, 1.772, 0.0
);

void main() {
    vec4 color = texture(texture0, texcoord);
    vec3 ycbcr = rgb2ycbcr_matrix * color.rgb;
    
    // YCbCr typically has Y in [0,1] and Cb,Cr in [-0.5,0.5]
    ycbcr.x = clamp(ycbcr.x * param1, 0.0, 1.0); // Y adjustment
    ycbcr.y = clamp(ycbcr.y * param2, -0.5, 0.5); // Cb adjustment
    ycbcr.z = clamp(ycbcr.z * param3, -0.5, 0.5); // Cr adjustment
    
    vec3 rgb = ycbcr2rgb_matrix * ycbcr;
    fragColor = vec4(clamp(rgb, 0.0, 1.0), color.a);
}
"""

# RGB to sRGB shader
srgb_fragment_shader = """
#version 330

in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D texture0;
uniform float param1; // Gamma adjustment

// Linear RGB to sRGB transformation
vec3 linear_to_srgb(vec3 linear) {
    vec3 srgb;
    for (int i = 0; i < 3; i++) {
        if (linear[i] <= 0.0031308)
            srgb[i] = 12.92 * linear[i];
        else
            srgb[i] = 1.055 * pow(linear[i], 1.0/2.4) - 0.055;
    }
    return srgb;
}

// sRGB to linear RGB transformation
vec3 srgb_to_linear(vec3 srgb) {
    vec3 linear;
    for (int i = 0; i < 3; i++) {
        if (srgb[i] <= 0.04045)
            linear[i] = srgb[i] / 12.92;
        else
            linear[i] = pow((srgb[i] + 0.055) / 1.055, 2.4);
    }
    return linear;
}

void main() {
    vec4 color = texture(texture0, texcoord);
    
    // Convert sRGB to linear
    vec3 linear = srgb_to_linear(color.rgb);
    
    // Apply gamma adjustment
    linear = pow(linear, vec3(param1));
    
    // Convert back to sRGB
    vec3 srgb = linear_to_srgb(linear);
    
    fragColor = vec4(clamp(srgb, 0.0, 1.0), color.a);
}
"""

# RGB to Adobe RGB shader
adobe_rgb_fragment_shader = """
#version 330

in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D texture0;
uniform float param1; // Gamma adjustment

// sRGB to linear RGB
vec3 srgb_to_linear(vec3 srgb) {
    vec3 linear;
    for (int i = 0; i < 3; i++) {
        if (srgb[i] <= 0.04045)
            linear[i] = srgb[i] / 12.92;
        else
            linear[i] = pow((srgb[i] + 0.055) / 1.055, 2.4);
    }
    return linear;
}

// Linear RGB to Adobe RGB (using gamma 2.2)
vec3 linear_to_adobe_rgb(vec3 linear) {
    return pow(linear, vec3(1.0/2.2 * param1));
}

// Adobe RGB to linear RGB
vec3 adobe_rgb_to_linear(vec3 adobe) {
    return pow(adobe, vec3(2.2 / param1));
}

// Linear RGB to sRGB
vec3 linear_to_srgb(vec3 linear) {
    vec3 srgb;
    for (int i = 0; i < 3; i++) {
        if (linear[i] <= 0.0031308)
            srgb[i] = 12.92 * linear[i];
        else
            srgb[i] = 1.055 * pow(linear[i], 1.0/2.4) - 0.055;
    }
    return srgb;
}

// sRGB to Adobe RGB conversion
void main() {
    vec4 color = texture(texture0, texcoord);
    
    // Convert sRGB to linear RGB
    vec3 linear = srgb_to_linear(color.rgb);
    
    // Convert linear RGB to Adobe RGB
    vec3 adobe = linear_to_adobe_rgb(linear);
    
    // For display purposes, convert back to sRGB
    vec3 display_srgb = linear_to_srgb(adobe_rgb_to_linear(adobe));
    
    fragColor = vec4(clamp(display_srgb, 0.0, 1.0), color.a);
}
"""

# Initialize shader programs
def init_shaders():
    global shaders
    
    try:
        shaders["grayscale"] = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=grayscale_fragment_shader
        )
        
        shaders["hsv"] = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=hsv_fragment_shader
        )
        
        shaders["cmyk"] = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=cmyk_fragment_shader
        )
        
        shaders["yiq"] = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=yiq_fragment_shader
        )
        
        shaders["yuv"] = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=yuv_fragment_shader
        )
        
        shaders["ycbcr"] = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=ycbcr_fragment_shader
        )
        
        shaders["srgb"] = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=srgb_fragment_shader
        )
        
        shaders["adobergb"] = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=adobe_rgb_fragment_shader
        )
        
    except Exception as e:
        print(f"Error initializing shaders: {e}")

# Create quad for rendering
def create_quad():
    vertices = np.array([
        # position    # texcoord
        -1.0, -1.0,   0.0, 0.0,
         1.0, -1.0,   1.0, 0.0,
         1.0,  1.0,   1.0, 1.0,
        -1.0,  1.0,   0.0, 1.0,
    ], dtype='f4')
    
    indices = np.array([
        0, 1, 2,
        0, 2, 3,
    ], dtype='i4')
    
    vbo = ctx.buffer(vertices)
    ibo = ctx.buffer(indices)
    
    return ctx.vertex_array(
        None,
        [
            (vbo, '2f 2f', 'in_position', 'in_texcoord'),
        ],
        ibo
    )

# Apply shader to image
def apply_shader(image, shader_name, params):
    h, w = image.shape[:2]
    
    # Create texture
    texture = ctx.texture((w, h), 4)
    texture.write(image.tobytes())
    
    # Create framebuffer
    fbo = ctx.framebuffer(
        color_attachments=[ctx.texture((w, h), 4)]
    )
    
    # Set up shader program
    prog = shaders[shader_name]
    quad = create_quad()
    
    # Bind texture and set uniforms
    texture.use(0)
    prog['texture0'] = 0
    
    # Set parameters based on shader type
    if shader_name == "grayscale":
        prog['param1'] = params.get('param1', 0.299)  # Red weight
        prog['param2'] = params.get('param2', 0.587)  # Green weight
        prog['param3'] = params.get('param3', 0.114)  # Blue weight
    elif shader_name == "hsv":
        prog['param1'] = params.get('param1', 0.0)    # Hue adjustment
        prog['param2'] = params.get('param2', 1.0)    # Saturation adjustment
        prog['param3'] = params.get('param3', 1.0)    # Value adjustment
    elif shader_name == "cmyk":
        prog['param1'] = params.get('param1', 1.0)    # Cyan adjustment
        prog['param2'] = params.get('param2', 1.0)    # Magenta adjustment
        prog['param3'] = params.get('param3', 1.0)    # Yellow adjustment
        prog['param4'] = params.get('param4', 1.0)    # Key adjustment
    elif shader_name in ["yiq", "yuv", "ycbcr"]:
        prog['param1'] = params.get('param1', 1.0)    # Y adjustment
        prog['param2'] = params.get('param2', 1.0)    # I/U/Cb adjustment
        prog['param3'] = params.get('param3', 1.0)    # Q/V/Cr adjustment
    elif shader_name in ["srgb", "adobergb"]:
        prog['param1'] = params.get('param1', 1.0)    # Gamma adjustment
    
    # Render
    fbo.use()
    quad.render()
    
    # Read result
    data = fbo.read(components=4)
    result = np.frombuffer(data, dtype=np.uint8).reshape(h, w, 4)
    
    return result

# Convert image to base64
def image_to_base64(image):
    _, buffer = cv2.imencode(".png", image)
    return base64.b64encode(buffer).decode('utf-8')

# Initialize shaders when app starts
@app.on_event("startup")
async def startup_event():
    init_shaders()

# API endpoint for converting image
@app.post("/convert/")
async def convert_image(
    file: UploadFile = File(...),
    model: str = "grayscale",
    param1: float = 1.0,
    param2: float = 1.0,
    param3: float = 1.0,
    param4: float = 1.0
):
    if model not in shaders:
        raise HTTPException(status_code=400, detail=f"Model {model} not supported")
    
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Convert to RGBA
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    
    # Apply shader
    params = {
        'param1': param1,
        'param2': param2,
        'param3': param3,
        'param4': param4
    }
    
    result = apply_shader(img, model, params)
    
    # Convert back to BGR for saving
    result_bgr = cv2.cvtColor(result, cv2.COLOR_RGBA2BGR)
    
    # Convert to base64
    original_base64 = image_to_base64(cv2.cvtColor(img, cv2.COLOR_RGBA2BGR))
    result_base64 = image_to_base64(result_bgr)
    
    return {
        "original": original_base64,
        "converted": result_base64
    }

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return html_content