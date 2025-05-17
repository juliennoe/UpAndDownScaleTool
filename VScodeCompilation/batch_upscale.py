import os
import subprocess

# Dossiers d'entrée et de sortie sur le Bureau
input_folder = os.path.expanduser("~/Desktop/Input")
output_folder = os.path.expanduser("~/Desktop/Output")

# Création du dossier Output si nécessaire
os.makedirs(output_folder, exist_ok=True)

# Script d'inférence de Real-ESRGAN
script_path = "inference_realesrgan.py"
model_name = "RealESRGAN_x2plus"
model_path = os.path.join("weights", model_name + ".pth")

# Vérification du modèle
if not os.path.exists(model_path):
    print("❌ Modèle non trouvé :", model_path)
    print("📥 Télécharge-le ici : https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5/RealESRGAN_x2plus.pth")
    exit(1)

# Récupération des .png
files = [f for f in os.listdir(input_folder) if f.lower().endswith(".png")]
if not files:
    print("📂 Aucun fichier .png trouvé dans :", input_folder)
    exit(0)

print(f"🔄 Traitement de {len(files)} image(s) dans '{input_folder}'...\n")

# Traitement de chaque image
for i, filename in enumerate(files, 1):
    input_path = os.path.join(input_folder, filename)
    print(f"[{i}/{len(files)}] Upscale de : {filename}")

    cmd = [
        "python", script_path,
        "-i", input_path,
        "-n", model_name,
        "--outscale", "2",
        "--fp32",
        "-o", output_folder
    ]

    subprocess.run(cmd)

print("\n✅ Terminé ! Résultats enregistrés dans :", output_folder)
