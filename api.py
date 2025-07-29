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

# ✅ CORS CORRIGÉ : enlever le slash à la fin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pittermanifique.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Validation du format de plaque
async def verifier_format(chaine):
    motif = r'^[A-Z]{2}-\d{3}-[A-Z]{2}$'
    return re.match(motif, chaine) is not None

# ✅ Route pour le classement
@app.get("/clasement/", summary="Classement")
async def clasement(top: int = Query(10, ge=1, description="Nombre de plaques à retourner")):
    result = bdd.classement(top)
    return result

# ✅ Route pour le signalement
@app.post("/report/", summary="Analyse d'une plaque depuis une image ou un texte")
async def analyse(
    file: Optional[UploadFile] = File(None),
    note: int = Form(0),
    commentaire: Optional[str] = Form(None),
    plaque: Optional[str] = Form(None),
):
    verif = await verifier_format(plaque) if plaque else False

    if not file and not plaque:
        raise HTTPException(status_code=400, detail="Veuillez fournir une image ou un texte.")

    if verif:
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

            bdd.report(success[1][0], note, commentaire)

            return JSONResponse(content={"status": "ok"})
        else:
            bdd.report(plaque, note, commentaire)
            return JSONResponse(content={"status": "ok"})
    else:
        return JSONResponse(content={"status": "none"})

# ✅ Code nécessaire pour Render (ou autre plateforme cloud)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))  # Render utilise une variable PORT
    uvicorn.run("api:app", host="0.0.0.0", port=port)
