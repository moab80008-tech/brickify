from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import numpy as np
import trimesh
import os

app = FastAPI()

LEGO_SIZE = 8
LEGO_HEIGHT = 9.6
MAX_LAYERS = 12

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <body style='font-family:sans-serif;padding:40px'>
        <h2>Brickify 3D - 50cm Deep Model</h2>
        <form action="/generate/" enctype="multipart/form-data" method="post">
            <input name="file" type="file"/>
            <button type="submit">Generate</button>
        </form>
    </body>
    </html>
    """

@app.post("/generate/")
async def generate(file: UploadFile):

    image = Image.open(file.file).convert("L")

    studs = 62
    image = image.resize((studs, studs))

    img_array = np.array(image)

    cubes = []

    for y in range(studs):
        for x in range(studs):
            brightness = img_array[y][x]
            layers = int((brightness / 255) * MAX_LAYERS)

            for z in range(layers):
                cube = trimesh.creation.box(
                    extents=[LEGO_SIZE, LEGO_SIZE, LEGO_HEIGHT]
                )
                cube.apply_translation([
                    x * LEGO_SIZE,
                    y * LEGO_SIZE,
                    z * LEGO_HEIGHT
                ])
                cubes.append(cube)

    model = trimesh.util.concatenate(cubes)

    output_path = "lego_model.stl"
    model.export(output_path)

    return FileResponse(output_path)
