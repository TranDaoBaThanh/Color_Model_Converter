# File: shader_manager.py
import moderngl
import numpy as np
import cv2

class ShaderManager:
    def __init__(self):
        # Create standalone context
        self.ctx = moderngl.create_standalone_context()
        
        # Shader programs
        self.shaders = {}
        
        # Initialize shaders
        self.init_shaders()
    
    def init_shaders(self):
        # Common vertex shader
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
            float c = (1.0 - rgb.r - k) / (1.0 - k + 0.000001);
            float m = (1.0 - rgb.g - k) / (1.0 - k + 0.000001);
            float y = (1.0 - rgb.b - k) / (1.0 - k + 0.000001);
            
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
        
        # File: shader_manager.py (tiếp theo từ phần trước)
        # RGB to YUV shader
        yuv_fragment_shader = """
        #version 330

        in vec2 texcoord;
        out vec4 fragColor;

        uniform sampler2D texture0;
        uniform float param1; // Y adjustment
        uniform float param2; // U adjustment
        uniform float param3; // V adjustment

        // RGB to YUV matrix
        const mat3 rgb2yuv_matrix = mat3(
            0.299, 0.587, 0.114,
            -0.147, -0.289, 0.436,
            0.615, -0.515, -0.100
        );

        // YUV to RGB matrix
        const mat3 yuv2rgb_matrix = mat3(
            1.0, 0.0, 1.14,
            1.0, -0.39, -0.58,
            1.0, 2.03, 0.0
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

        // RGB to YCbCr
        vec3 rgb2ycbcr(vec3 rgb) {
            float y = 0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b;
            float cb = 128.0/255.0 + (-0.169 * rgb.r - 0.331 * rgb.g + 0.5 * rgb.b);
            float cr = 128.0/255.0 + (0.5 * rgb.r - 0.419 * rgb.g - 0.081 * rgb.b);
            return vec3(y, cb, cr);
        }

        // YCbCr to RGB
        vec3 ycbcr2rgb(vec3 ycbcr) {
            float y = ycbcr.x;
            float cb = ycbcr.y - 128.0/255.0;
            float cr = ycbcr.z - 128.0/255.0;
            
            float r = y + 1.402 * cr;
            float g = y - 0.344 * cb - 0.714 * cr;
            float b = y + 1.772 * cb;
            
            return vec3(r, g, b);
        }

        void main() {
            vec4 color = texture(texture0, texcoord);
            vec3 ycbcr = rgb2ycbcr(color.rgb);
            
            // Apply adjustments
            ycbcr.x = clamp(ycbcr.x * param1, 0.0, 1.0); // Y adjustment
            ycbcr.y = clamp(((ycbcr.y - 128.0/255.0) * param2) + 128.0/255.0, 0.0, 1.0); // Cb adjustment
            ycbcr.z = clamp(((ycbcr.z - 128.0/255.0) * param3) + 128.0/255.0, 0.0, 1.0); // Cr adjustment
            
            vec3 rgb = ycbcr2rgb(ycbcr);
            fragColor = vec4(clamp(rgb, 0.0, 1.0), color.a);
        }
        """
        
        # sRGB shader
        srgb_fragment_shader = """
        #version 330

        in vec2 texcoord;
        out vec4 fragColor;

        uniform sampler2D texture0;
        uniform float param1; // Gamma adjustment

        // Linear to sRGB conversion
        vec3 linear_to_srgb(vec3 linear) {
            vec3 a = 12.92 * linear;
            vec3 b = 1.055 * pow(linear, vec3(1.0/2.4)) - 0.055;
            vec3 select = step(vec3(0.0031308), linear);
            return mix(a, b, select);
        }

        // sRGB to linear conversion
        vec3 srgb_to_linear(vec3 srgb) {
            vec3 a = srgb / 12.92;
            vec3 b = pow((srgb + 0.055) / 1.055, vec3(2.4));
            vec3 select = step(vec3(0.04045), srgb);
            return mix(a, b, select);
        }

        void main() {
            vec4 color = texture(texture0, texcoord);
            vec3 linear = srgb_to_linear(color.rgb);
            
            // Apply gamma adjustment
            linear = pow(linear, vec3(param1));
            
            vec3 srgb = linear_to_srgb(linear);
            fragColor = vec4(clamp(srgb, 0.0, 1.0), color.a);
        }
        """
        
        # Adobe RGB shader
        adobergb_fragment_shader = """
        #version 330

        in vec2 texcoord;
        out vec4 fragColor;

        uniform sampler2D texture0;
        uniform float param1; // Gamma adjustment

        // sRGB to Adobe RGB conversion matrix
        const mat3 srgb_to_adobe_matrix = mat3(
            0.7161, 0.1009, 0.1471,
            0.2722, 0.6780, 0.0498,
            0.0138, 0.0947, 0.7175
        );

        // Adobe RGB to sRGB conversion matrix
        const mat3 adobe_to_srgb_matrix = mat3(
            1.4599, -0.2205, -0.0782,
            -0.5867, 1.3523, 0.0833,
            0.0334, -0.1151, 1.0526
        );

        void main() {
            vec4 color = texture(texture0, texcoord);
            
            // Convert to Adobe RGB
            vec3 adobergb = srgb_to_adobe_matrix * color.rgb;
            
            // Apply gamma adjustment
            adobergb = pow(adobergb, vec3(param1));
            
            // Convert back to sRGB
            vec3 srgb = adobe_to_srgb_matrix * adobergb;
            
            fragColor = vec4(clamp(srgb, 0.0, 1.0), color.a);
        }
        """
        
        # Compile and store shaders
        self.shaders["grayscale"] = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=grayscale_fragment_shader)
        self.shaders["hsv"] = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=hsv_fragment_shader)
        self.shaders["cmyk"] = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=cmyk_fragment_shader)
        self.shaders["yiq"] = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=yiq_fragment_shader)
        self.shaders["yuv"] = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=yuv_fragment_shader)
        self.shaders["ycbcr"] = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=ycbcr_fragment_shader)
        self.shaders["srgb"] = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=srgb_fragment_shader)
        self.shaders["adobergb"] = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=adobergb_fragment_shader)
    
    def render_image(self, image, color_model, params):
        """
        Render an image using specified color model and parameters
        
        Args:
            image: numpy array of BGR image
            color_model: string, type of color model to use
            params: dict of parameters for the shader
            
        Returns:
            numpy array of processed image
        """
        # Ensure valid model
        if color_model not in self.shaders:
            raise ValueError(f"Unsupported color model: {color_model}")
        
        # Get shader program
        program = self.shaders[color_model]
        
        # Convert to RGB for OpenGL
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get dimensions
        height, width = image_rgb.shape[0], image_rgb.shape[1]
        
        # Prepare texture
        texture = self.ctx.texture((width, height), 3, image_rgb.tobytes())
        texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        texture.swizzle = 'RGB'
        
        # Prepare framebuffer
        fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((width, height), 3)]
        )
        fbo.use()
        
        # Prepare vertex buffer
        vertices = np.array([
            # Position (x, y), TexCoord (x, y)
            -1.0, -1.0, 0.0, 0.0,  # bottom left
            1.0, -1.0, 1.0, 0.0,   # bottom right
            -1.0, 1.0, 0.0, 1.0,   # top left
            1.0, 1.0, 1.0, 1.0,    # top right
        ], dtype='f4')
        
        vbo = self.ctx.buffer(vertices)
        vao = self.ctx.vertex_array(
            program, 
            [
                (vbo, '2f 2f', 'in_position', 'in_texcoord')
            ]
        )
        
        # Bind texture
        texture.use(0)
        program['texture0'] = 0
        
        # Set parameters
        for key, value in params.items():
            if key in program:
                program[key] = float(value)
        
        # Render
        vao.render(moderngl.TRIANGLE_STRIP)
        
        # Read pixels
        data = fbo.read(components=3)
        output = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
        
        # Convert back to BGR for OpenCV
        output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        
        # Clean up
        fbo.release()
        texture.release()
        vbo.release()
        vao.release()
        
        return output_bgr