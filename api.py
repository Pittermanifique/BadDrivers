import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
import shutil, os
from uuid import uuid4
from starlette.middleware.cors import CORSMiddleware
from openCV import reconnaissance
import bdd
import re

app = FastAPI(title="report plaque")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verifier_format(chaine):
    motif = r'^[A-Z]{2}-\d{3}-[A-Z]{2}$'
    return re.match(motif, chaine) is not None

@app.get("/clasement/",summary="Clasement")
async def clasement(top: int = Query(10, ge=1, description="Nombre de plaques à retourner")):
    result = bdd.classement(top)
    return result


@app.post("/report/", summary="Analyse d'une plaque depuis une image ou un texte")
async def analyse(
    file: Optional[UploadFile] = File(None),
    note: int = Form(0),
    commentaire: Optional[str] = Form(None),
    plaque: Optional[str] = Form(None),
):

    verif =  await verifier_format(plaque)
    if verif:
        if not file and not plaque:
            raise HTTPException(status_code=400, detail="Veuillez fournir une image ou un texte.")

        if file:
            if not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Ce fichier n'est pas une image.")

            temp_dir = "temp_images"
            os.makedirs(temp_dir, exist_ok=True)
            extension = file.filename.split(".")[-1]
            temp_filename = f"{uuid4()}.{extension}"
            image_path = os.path.join(temp_dir, temp_filename)

            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            success = reconnaissance(image_path)
            print(success)
            os.remove(image_path)

            if not success:
                raise HTTPException(status_code=404, detail="Aucune plaque détectée.")

            # Enregistrement en basesss
            bdd.report(success[1][0], note, commentaire)

            return JSONResponse(content={
                "status": "ok",
            })

        else:
            # Traitement du texte directement soumis
            bdd.report(plaque, note, commentaire)

            return JSONResponse(content={
                "status": "ok",
            })
    else:
        return JSONResponse(content={
                "status": "none",
            })


if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

