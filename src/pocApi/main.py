from fastapi import FastAPI, File, UploadFile
from analyzer import analisar_frame

app = FastAPI()

@app.post("/analisar/")
async def analisar_exercicio(exercicio: str, file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = analisar_frame(image_bytes, exercicio)
    return result
