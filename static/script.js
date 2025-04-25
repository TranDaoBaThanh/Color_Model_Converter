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
    const fileName = document.getElementById('fileName');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    
    // Current file
    let currentFile = null;
    
    // Parameter values
    let params = {
        param1: 0.299,
        param2: 0.587,
        param3: 0.114,
        param4: 1.0
    };
    
    // Show toast notification
    function showToast(message, type = 'success') {
        toastMessage.textContent = message;
        toast.className = `toast show toast-${type}`;
        
        // Change icon based on type
        const iconContainer = toast.querySelector('svg');
        if (type === 'success') {
            iconContainer.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />';
            iconContainer.classList.remove('text-red-600');
            iconContainer.classList.add('text-emerald-600');
        } else {
            iconContainer.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />';
            iconContainer.classList.remove('text-emerald-600');
            iconContainer.classList.add('text-red-600');
        }
        
        // Hide toast after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
    
    // Update visible parameter controls based on selected color model
    function updateParamControls() {
        const model = colorModelSelect.value;
        
        // Hide all param divs with animation
        document.querySelectorAll('[id$="-params"]').forEach(div => {
            div.classList.add('hidden');
        });
        
        // Show selected model's params with animation
        const selectedParams = document.getElementById(`${model}-params`);
        selectedParams.classList.remove('hidden');
        
        // Trigger reflow to restart animation
        void selectedParams.offsetWidth;
        
        // Apply animation again
        selectedParams.classList.remove('animated-fade');
        void selectedParams.offsetWidth;
        selectedParams.classList.add('animated-fade');
        
        // Reset parameter values for the active model
        const activeSliders = document.querySelectorAll(`#${model}-params .param-slider`);
        activeSliders.forEach(slider => {
            const paramName = slider.dataset.param;
            params[paramName] = parseFloat(slider.value);
            slider.nextElementSibling.textContent = parseFloat(slider.value).toFixed(3);
        });
        
        // Update model info
        updateModelInfo(model);
    }
    
    // Update model info text with enhanced styling
    function updateModelInfo(model) {
        const modelInfoText = {
            grayscale: `
                <h4 class="flex items-center">
                    <span class="inline-block w-3 h-3 rounded-full bg-gray-500 mr-2"></span>
                    Grayscale
                </h4>
                <p>The grayscale color model converts colored images to shades of gray. It works by applying weights to the red, green, and blue channels of an image and summing them to produce a single intensity value.</p>
                <p>The standard weights (0.299, 0.587, 0.114) are based on human perception of brightness in different color channels.</p>
                <div class="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <strong class="block mb-1 text-gray-700">Formula:</strong>
                    <code class="text-sm bg-gray-100 p-1 rounded">Gray = (R × 0.299) + (G × 0.587) + (B × 0.114)</code>
                </div>
            `,
            hsv: `
                <h4 class="flex items-center">
                    <span class="inline-block w-3 h-3 rounded-full bg-yellow-500 mr-2"></span>
                    HSV (Hue, Saturation, Value)
                </h4>
                <p>HSV is a cylindrical color model that remaps the RGB color space to be more intuitive for human perception:</p>
                <ul>
                    <li><strong>Hue</strong>: Represents the color type (red, blue, etc.) and ranges from 0 to 360 degrees.</li>
                    <li><strong>Saturation</strong>: Represents the intensity of the color (0 is grayscale, 1 is fully saturated).</li>
                    <li><strong>Value</strong>: Represents the brightness of the color (0 is black, 1 is full brightness).</li>
                </ul>
                <p>HSV is commonly used in color pickers and image editing applications.</p>
                <div class="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <strong class="block mb-1 text-gray-700">Key Property:</strong>
                    <span class="text-sm">Separates color information (hue, saturation) from intensity information (value)</span>
                </div>
            `,
            cmyk: `
                <h4 class="flex items-center">
                    <span class="inline-block w-3 h-3 rounded-full bg-green-500 mr-2"></span>
                    CMYK (Cyan, Magenta, Yellow, Key/Black)
                </h4>
                <p>CMYK is a subtractive color model used primarily in printing:</p>
                <ul>
                    <li><strong>Cyan</strong>: Absorbs red light, appears as blue-green.</li>
                    <li><strong>Magenta</strong>: Absorbs green light, appears as purplish-red.</li>
                    <li><strong>Yellow</strong>: Absorbs blue light.</li>
                    <li><strong>Key (Black)</strong>: Used to improve contrast and save colored ink.</li>
                </ul>
                <p>Unlike RGB (which is additive), CMYK is subtractive, meaning the colors are created by subtracting light.</p>
                <div class="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <strong class="block mb-1 text-gray-700">Application:</strong>
                    <span class="text-sm">Standard in color printing, magazines, brochures, and other print media</span>
                </div>
            `,
            yiq: `
                <h4 class="flex items-center">
                    <span class="inline-block w-3 h-3 rounded-full bg-blue-500 mr-2"></span>
                    YIQ
                </h4>
                <p>YIQ is a color model developed for NTSC television transmission:</p>
                <ul>
                    <li><strong>Y</strong>: Luminance (brightness) component.</li>
                    <li><strong>I</strong>: In-phase component, carries orange-blue chrominance information.</li>
                    <li><strong>Q</strong>: Quadrature component, carries green-purple chrominance information.</li>
                </ul>
                <p>YIQ was designed to allow backward compatibility with black and white television while adding color information.</p>
                <div class="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <strong class="block mb-1 text-gray-700">Historical Note:</strong>
                    <span class="text-sm">Used in NTSC television broadcasting in North America until the digital transition</span>
                </div>
            `,
            yuv: `
                <h4 class="flex items-center">
                    <span class="inline-block w-3 h-3 rounded-full bg-purple-500 mr-2"></span>
                    YUV
                </h4>
                <p>YUV is a color model used in analog television broadcasting:</p>
                <ul>
                    <li><strong>Y</strong>: Luminance (brightness) component.</li>
                    <li><strong>U</strong>: Blue-luminance difference (blue minus luminance).</li>
                    <li><strong>V</strong>: Red-luminance difference (red minus luminance).</li>
                </ul>
                <p>YUV was developed to separate luminance from color information, allowing backward compatibility with black and white systems.</p>
                <div class="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <strong class="block mb-1 text-gray-700">Modern Usage:</strong>
                    <span class="text-sm">Used in PAL, SECAM, and component video standards; basis for many video compression algorithms</span>
                </div>
            `,
            ycbcr: `
                <h4 class="flex items-center">
                    <span class="inline-block w-3 h-3 rounded-full bg-pink-500 mr-2"></span>
                    YCbCr
                </h4>
                <p>YCbCr is a digital color model similar to YUV but used in digital video and JPEG compression:</p>
                <ul>
                    <li><strong>Y</strong>: Luminance component.</li>
                    <li><strong>Cb</strong>: Blue-difference chroma component.</li>
                    <li><strong>Cr</strong>: Red-difference chroma component.</li>
                </ul>
                <p>YCbCr allows for chroma subsampling, which reduces file size while minimally affecting perceived image quality.</p>
                <div class="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <strong class="block mb-1 text-gray-700">Key Advantage:</strong>
                    <span class="text-sm">Enables efficient compression in formats like JPEG, MPEG, and H.264</span>
                </div>
            `,
            srgb: `
                <h4 class="flex items-center">
                    <span class="inline-block w-3 h-3 rounded-full bg-red-500 mr-2"></span>
                    sRGB (Standard RGB)
                </h4>
                <p>sRGB is the standard color space used for web graphics, monitors, and many digital cameras:</p>
                <p>It has a defined gamma curve that maps RGB values to the actual intensity of light displayed on a typical monitor.</p>
                <p>The sRGB color space covers about 35% of the visible colors specified by CIE and is designed to be consistent across different displays.</p>
                <div class="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <strong class="block mb-1 text-gray-700">Significance:</strong>
                    <span class="text-sm">The default color space for most consumer digital cameras, monitors, and the web</span>
                </div>
            `,
            adobergb: `
                <h4 class="flex items-center">
                    <span class="inline-block w-3 h-3 rounded-full bg-orange-500 mr-2"></span>
                    Adobe RGB
                </h4>
                <p>Adobe RGB is a color space developed by Adobe Systems in 1998:</p>
                <p>It has a wider gamut than sRGB, particularly in the cyan-green colors, covering approximately 50% of the visible colors specified by CIE.</p>
                <p>Adobe RGB uses a gamma of 2.2 and is often used in professional photography and printing.</p>
                <div class="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <strong class="block mb-1 text-gray-700">Professional Use:</strong>
                    <span class="text-sm">Preferred for professional photography, printing, and design workflows where color accuracy is critical</span>
                </div>
            `
        };
        
        // Animate model info update
        modelInfo.style.opacity = "0";
        setTimeout(() => {
            modelInfo.innerHTML = modelInfoText[model] || '<p>Select a color model to see information about it.</p>';
            modelInfo.style.opacity = "1";
        }, 300);
    }
    
    // Handle file selection with visual feedback
    imageUpload.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            currentFile = e.target.files[0];
            fileName.textContent = currentFile.name;
            fileName.classList.add('text-indigo-600', 'font-medium');
            
            // Preview the image in the original container
            const reader = new FileReader();
            reader.onload = function(e) {
                originalImg.src = e.target.result;
                originalImg.classList.add('animate__animated', 'animate__fadeIn');
                
                // Remove animation class after animation completes
                setTimeout(() => {
                    originalImg.classList.remove('animate__animated', 'animate__fadeIn');
                }, 1000);
            };
            reader.readAsDataURL(currentFile);
        }
    });
    
    // Handle model selection change with visual feedback
    colorModelSelect.addEventListener('change', function() {
        updateParamControls();
        
        // Add brief highlight animation
        this.classList.add('ring', 'ring-indigo-300');
        setTimeout(() => {
            this.classList.remove('ring', 'ring-indigo-300');
        }, 300);
    });
    
    // Handle parameter changes with visual feedback
    document.querySelectorAll('.param-slider').forEach(slider => {
        slider.addEventListener('input', function() {
            const paramName = this.dataset.param;
            const value = parseFloat(this.value);
            
            // Update display value with animation
            const valueDisplay = this.nextElementSibling;
            valueDisplay.textContent = value.toFixed(3);
            valueDisplay.classList.add('animate__animated', 'animate__pulse');
            
            // Remove animation class after animation completes
            setTimeout(() => {
                valueDisplay.classList.remove('animate__animated', 'animate__pulse');
            }, 500);
            
            // Update params object
            params[paramName] = value;
        });
    });
    
    // Handle upload and initial conversion
    uploadBtn.addEventListener('click', function() {
        if (!currentFile) {
            showToast('Please select an image file first.', 'error');
            return;
        }
        
        convertImage();
    });
    
    // Handle parameter changes and reconversion
    applyBtn.addEventListener('click', function() {
        if (!currentFile) {
            showToast('Please upload an image first.', 'error');
            return;
        }
        
        convertImage();
    });
    
    // Convert image with current parameters and visual feedback
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
        
        // Add loading class to buttons
        uploadBtn.classList.add('loading');
        uploadBtn.textContent = '';
        applyBtn.classList.add('loading');
        applyBtn.textContent = '';
        
        // Show processing toast
        showToast('Processing image...', 'info');
        
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
            // Update images with animation
            originalImg.src = 'data:image/png;base64,' + data.original;
            
            // Add fade in animation to the converted image
            convertedImg.classList.add('animate__animated', 'animate__fadeIn');
            convertedImg.src = 'data:image/png;base64,' + data.converted;
            
            // Remove animation class after animation completes
            setTimeout(() => {
                convertedImg.classList.remove('animate__animated', 'animate__fadeIn');
            }, 1000);
            
            // Show success toast
            showToast('Image converted successfully!', 'success');
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error processing image: ' + error.message, 'error');
        })
        .finally(() => {
            // Reset button states
            uploadBtn.disabled = false;
            applyBtn.disabled = false;
            
            // Remove loading class and restore text
            uploadBtn.classList.remove('loading');
            uploadBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
                Convert
            `;
            
            applyBtn.classList.remove('loading');
            applyBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Apply Changes
            `;
        });
    }
    
    // Initialize parameter controls
    updateParamControls();
    
    // Add mouse wheel support for sliders
    document.querySelectorAll('.param-slider').forEach(slider => {
        slider.addEventListener('wheel', function(e) {
            e.preventDefault();
            if (e.deltaY < 0) {
                // Scroll up, increase value
                this.value = parseFloat(this.value) + parseFloat(this.step);
            } else {
                // Scroll down, decrease value
                this.value = parseFloat(this.value) - parseFloat(this.step);
            }
            
            // Trigger input event to update the display
            this.dispatchEvent(new Event('input'));
        });
    });
    
    // Add keyboard navigation for better accessibility
    document.querySelectorAll('.param-slider').forEach(slider => {
        slider.addEventListener('keydown', function(e) {
            let newValue = parseFloat(this.value);
            let step = parseFloat(this.step);
            
            if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
                newValue += step;
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
                newValue -= step;
            }
            
            // Enforce min/max
            newValue = Math.max(parseFloat(this.min), Math.min(parseFloat(this.max), newValue));
            
            if (newValue !== parseFloat(this.value)) {
                this.value = newValue;
                this.dispatchEvent(new Event('input'));
            }
        });
    });
    
    // Add hover effect to cards
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});