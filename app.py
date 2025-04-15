# File: app.py
import os
import base64
from io import BytesIO
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from shader_manager import ShaderManager

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Color Model Converter")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create shader manager
shader_manager = ShaderManager()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/convert/")
async def convert_image(
    file: UploadFile = File(...),
    model: str = Form(...),
    param1: float = Form(1.0),
    param2: float = Form(1.0),
    param3: float = Form(1.0),
    param4: float = Form(1.0)
):
    # Read image file
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return JSONResponse(
            content={"error": "Invalid image file"},
            status_code=400
        )
    
    # Parameters for shader
    params = {
        "param1": param1,
        "param2": param2,
        "param3": param3,
        "param4": param4
    }
    
    try:
        # Process image with selected model
        processed_img = shader_manager.render_image(img, model, params)
        
        # Encode images to base64
        _, original_buffer = cv2.imencode('.png', img)
        _, processed_buffer = cv2.imencode('.png', processed_img)
        
        original_base64 = base64.b64encode(original_buffer).decode('utf-8')
        processed_base64 = base64.b64encode(processed_buffer).decode('utf-8')
        
        return {
            "original": original_base64,
            "converted": processed_base64
        }
    
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run server
    uvicorn.run("app:app", host="localhost", port=port, reload=True)