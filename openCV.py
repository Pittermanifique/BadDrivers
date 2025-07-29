import cv2
import easyocr
import matplotlib.pyplot as plt

def reconnaissance(img_path, detail=False):
    # Chargement du classifieur Haar
    cascade = cv2.CascadeClassifier('modelsIA//eu.xml')
    img = cv2.imread(img_path)

    if img is None:
        return False, "Erreur : image non trouvée."

    # Prétraitement de l'image pour la détection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Détection des plaques
    plates = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # Initialisation de l'OCR
    reader = easyocr.Reader(['fr'], gpu=False)

    resultsdetect = []
    results = []

    for i, (x, y, w, h) in enumerate(plates):
        # Marges et découpage sécurisé
        x1 = max(x + 10, 0)
        x2 = min(x + w - 2, img.shape[1])
        y1 = max(y + 1, 0)
        y2 = min(y + h - 1, img.shape[0])
        plaque_roi = img[y1:y2, x1:x2]

        # Conversion en niveaux de gris et floutage
        plaque_gray = cv2.cvtColor(plaque_roi, cv2.COLOR_BGR2GRAY)
        plaque_blur = cv2.GaussianBlur(plaque_gray, (1, 1), 0)

        # Passage à l'OCR
        resultats = reader.readtext(plaque_blur)

        for detection in resultats:
            texte = detection[1]
            resultsdetect.append(f"{texte}")
            cv2.putText(img, texte, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        # Détail de traitement
        if detail:
            fig, axs = plt.subplots(1, 3, figsize=(14, 4))
            axs[0].imshow(cv2.cvtColor(plaque_roi, cv2.COLOR_BGR2RGB))
            axs[0].set_title("Originale")
            axs[1].imshow(plaque_gray, cmap='gray')
            axs[1].set_title("Gris")
            axs[2].imshow(plaque_blur, cmap='gray')
            axs[2].set_title("Réduction de bruit")
            for ax in axs:
                ax.axis('off')
            plt.suptitle(f"Étapes pour plaque {i+1}")
            plt.tight_layout()
            plt.show()

    if detail:
        # Affichage de l’image finale annotée
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.title("Plaques détectées et lues")
        plt.axis("off")
        plt.show()

    for result in resultsdetect:
        # Sécurisation de l'accès aux indices
        if len(result) > 9 and result[2] and result[6] != "-":
            pass  # On ignore ce résultat
        else:
            results.append(result)



    return (True, results) if results else (False, "Aucune plaque détectée.")
