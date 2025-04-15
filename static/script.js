// File: static/script.js
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const imageUpload = document.getElementById('imageUpload');
    const uploadBtn = document.getElementById('uploadBtn');
    const applyBtn = document.getElementById('applyBtn');
    const colorModelSelect = document.getElementById('colorModel');
    const originalImg = document.getElementById('original');
    const convertedImg = document.getElementById('converted');
    const modelInfo = document.getElementById('model-info');
    
    // Current file
    let currentFile = null;
    
    // Parameter values
    let params = {
        param1: 0.299,
        param2: 0.587,
        param3: 0.114,
        param4: 1.0
    };
    
    // Update visible parameter controls based on selected color model
    function updateParamControls() {
        const model = colorModelSelect.value;
        
        // Hide all param divs
        document.querySelectorAll('[id$="-params"]').forEach(div => {
            div.classList.add('hidden');
        });
        
        // Show selected model's params
        document.getElementById(`${model}-params`).classList.remove('hidden');
        
        // Reset parameter values for the active model
        const activeSliders = document.querySelectorAll(`#${model}-params .param-slider`);
        activeSliders.forEach(slider => {
            const paramName = slider.dataset.param;
            params[paramName] = parseFloat(slider.value);
        });
        
        // Update model info
        updateModelInfo(model);
    }
    
    // Update model info text
    function updateModelInfo(model) {
        const modelInfoText = {
            grayscale: `
                <h4>Grayscale</h4>
                <p>The grayscale color model converts colored images to shades of gray. It works by applying weights to the red, green, and blue channels of an image and summing them to produce a single intensity value.</p>
                <p>The standard weights (0.299, 0.587, 0.114) are based on human perception of brightness in different color channels.</p>
            `,
            hsv: `
                <h4>HSV (Hue, Saturation, Value)</h4>
                <p>HSV is a cylindrical color model that remaps the RGB color space to be more intuitive for human perception:</p>
                <ul>
                    <li><strong>Hue</strong>: Represents the color type (red, blue, etc.) and ranges from 0 to 360 degrees.</li>
                    <li><strong>Saturation</strong>: Represents the intensity of the color (0 is grayscale, 1 is fully saturated).</li>
                    <li><strong>Value</strong>: Represents the brightness of the color (0 is black, 1 is full brightness).</li>
                </ul>
                <p>HSV is commonly used in color pickers and image editing applications.</p>
            `,
            cmyk: `
                <h4>CMYK (Cyan, Magenta, Yellow, Key/Black)</h4>
                <p>CMYK is a subtractive color model used primarily in printing:</p>
                <ul>
                    <li><strong>Cyan</strong>: Absorbs red light, appears as blue-green.</li>
                    <li><strong>Magenta</strong>: Absorbs green light, appears as purplish-red.</li>
                    <li><strong>Yellow</strong>: Absorbs blue light.</li>
                    <li><strong>Key (Black)</strong>: Used to improve contrast and save colored ink.</li>
                </ul>
                <p>Unlike RGB (which is additive), CMYK is subtractive, meaning the colors are created by subtracting light.</p>
            `,
            yiq: `
                <h4>YIQ</h4>
                <p>YIQ is a color model developed for NTSC television transmission:</p>
                <ul>
                    <li><strong>Y</strong>: Luminance (brightness) component.</li>
                    <li><strong>I</strong>: In-phase component, carries orange-blue chrominance information.</li>
                    <li><strong>Q</strong>: Quadrature component, carries green-purple chrominance information.</li>
                </ul>
                <p>YIQ was designed to allow backward compatibility with black and white television while adding color information.</p>
            `,
            yuv: `
                <h4>YUV</h4>
                <p>YUV is a color model used in analog television broadcasting:</p>
                <ul>
                    <li><strong>Y</strong>: Luminance (brightness) component.</li>
                    <li><strong>U</strong>: Blue-luminance difference (blue minus luminance).</li>
                    <li><strong>V</strong>: Red-luminance difference (red minus luminance).</li>
                </ul>
                <p>YUV was developed to separate luminance from color information, allowing backward compatibility with black and white systems.</p>
            `,
            ycbcr: `
                <h4>YCbCr</h4>
                <p>YCbCr is a digital color model similar to YUV but used in digital video and JPEG compression:</p>
                <ul>
                    <li><strong>Y</strong>: Luminance component.</li>
                    <li><strong>Cb</strong>: Blue-difference chroma component.</li>
                    <li><strong>Cr</strong>: Red-difference chroma component.</li>
                </ul>
                <p>YCbCr allows for chroma subsampling, which reduces file size while minimally affecting perceived image quality.</p>
            `,
            srgb: `
                <h4>sRGB (Standard RGB)</h4>
                <p>sRGB is the standard color space used for web graphics, monitors, and many digital cameras:</p>
                <p>It has a defined gamma curve that maps RGB values to the actual intensity of light displayed on a typical monitor.</p>
                <p>The sRGB color space covers about 35% of the visible colors specified by CIE and is designed to be consistent across different displays.</p>
            `,
            adobergb: `
                <h4>Adobe RGB</h4>
                <p>Adobe RGB is a color space developed by Adobe Systems in 1998:</p>
                <p>It has a wider gamut than sRGB, particularly in the cyan-green colors, covering approximately 50% of the visible colors specified by CIE.</p>
                <p>Adobe RGB uses a gamma of 2.2 and is often used in professional photography and printing.</p>
            `
        };
        
        modelInfo.innerHTML = modelInfoText[model] || '<p>Select a color model to see information about it.</p>';
    }
    
    // Handle file selection
    imageUpload.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            currentFile = e.target.files[0];
        }
    });
    
    // Handle model selection change
    colorModelSelect.addEventListener('change', updateParamControls);
    
    // Handle parameter changes
    document.querySelectorAll('.param-slider').forEach(slider => {
        slider.addEventListener('input', function() {
            const paramName = this.dataset.param;
            const value = parseFloat(this.value);
            
            // Update display value
            this.nextElementSibling.textContent = value.toFixed(3);
            
            // Update params object
            params[paramName] = value;
        });
    });
    
    // Handle upload and initial conversion
    uploadBtn.addEventListener('click', function() {
        if (!currentFile) {
            alert('Please select an image file first.');
            return;
        }
        
        convertImage();
    });
    
    // Handle parameter changes and reconversion
    applyBtn.addEventListener('click', function() {
        if (!currentFile) {
            alert('Please upload an image first.');
            return;
        }
        
        convertImage();
    });
    
    // Convert image with current parameters
    function convertImage() {
        const formData = new FormData();
        formData.append('file', currentFile);
        formData.append('model', colorModelSelect.value);
        
        // Add parameters
        for (const [key, value] of Object.entries(params)) {
            formData.append(key, value);
        }
        
        // Show loading state
        uploadBtn.disabled = true;
        applyBtn.disabled = true;
        uploadBtn.textContent = 'Processing...';
        applyBtn.textContent = 'Processing...';
        
        // Send to server
        fetch('/convert/', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update images
            originalImg.src = 'data:image/png;base64,' + data.original;
            convertedImg.src = 'data:image/png;base64,' + data.converted;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error processing image: ' + error.message);
        })
        .finally(() => {
            // Reset button states
            uploadBtn.disabled = false;
            applyBtn.disabled = false;
            uploadBtn.textContent = 'Upload & Convert';
            applyBtn.textContent = 'Apply Changes';
        });
    }
    
    // Initialize parameter controls
    updateParamControls();
});