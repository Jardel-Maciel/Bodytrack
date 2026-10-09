"""
Gera o catálogo de exercícios com imagens de demonstração.

O que faz:
1. Baixa o dataset aberto "free-exercise-db" (Unlicense / domínio público):
   https://github.com/yuhonas/free-exercise-db
2. Para cada exercício da lista CURATED abaixo (nome em português + apelidos
   que as pessoas costumam digitar), baixa as 2 imagens (posição inicial e
   final do movimento), reduz para 480px e salva em WEBP em
   frontend/public/exercises/<id>/0.webp e 1.webp.
3. Escreve backend/app/data/exercise_catalog.json (fonte única de verdade,
   lida pelo backend e entregue ao frontend pelo endpoint /exercise-catalog).

Uso (a partir da pasta backend/):
    python -m scripts.build_exercise_catalog

Só precisa rodar de novo quando você quiser ADICIONAR/EDITAR exercícios
da lista CURATED. Os arquivos gerados são versionados no Git.
"""
import io
import json
import sys
from pathlib import Path

import httpx
from PIL import Image

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BACKEND_DIR.parent
OUT_JSON = BACKEND_DIR / "app" / "data" / "exercise_catalog.json"
OUT_IMAGES = REPO_DIR / "frontend" / "public" / "exercises"

DATASET_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
IMAGE_BASE = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises"

MAX_WIDTH = 480
WEBP_QUALITY = 78

# (id no dataset, nome em português, [apelidos])
CURATED: list[tuple[str, str, list[str]]] = [
    # ---------------- Peito ----------------
    ("Barbell_Bench_Press_-_Medium_Grip", "Supino reto com barra", ["supino reto", "supino", "supino com barra", "supino barra", "bench press"]),
    ("Dumbbell_Bench_Press", "Supino reto com halteres", ["supino halteres", "supino com halter", "supino reto halter", "supino reto com halter"]),
    ("Incline_Dumbbell_Press", "Supino inclinado com halteres", ["supino inclinado", "supino inclinado halter", "supino inclinado com halter"]),
    ("Barbell_Incline_Bench_Press_-_Medium_Grip", "Supino inclinado com barra", ["supino inclinado barra"]),
    ("Decline_Barbell_Bench_Press", "Supino declinado com barra", ["supino declinado"]),
    ("Machine_Bench_Press", "Supino na máquina", ["supino maquina", "chest press", "supino articulado"]),
    ("Close-Grip_Barbell_Bench_Press", "Supino fechado", ["supino pegada fechada", "supino fechado com barra"]),
    ("Dumbbell_Flyes", "Crucifixo reto com halteres", ["crucifixo", "crucifixo reto", "crucifixo halter", "crucifixo com halteres"]),
    ("Incline_Dumbbell_Flyes", "Crucifixo inclinado com halteres", ["crucifixo inclinado", "crucifixo inclinado halter"]),
    ("Butterfly", "Voador (peck deck)", ["voador", "peck deck", "pec deck", "crucifixo maquina", "crucifixo na maquina", "fly maquina"]),
    ("Cable_Crossover", "Crossover na polia", ["crossover", "cross over", "crucifixo polia", "crucifixo na polia", "cabo cruzado"]),
    ("Pushups", "Flexão de braço", ["flexao", "flexao de braco", "push up", "pushup", "flexao de bracos"]),
    ("Dips_-_Chest_Version", "Paralelas (foco no peito)", ["paralelas peito", "mergulho peito", "dips peito"]),
    ("Bent-Arm_Dumbbell_Pullover", "Pullover com halter", ["pullover", "pull over", "pullover halter"]),
    # ---------------- Costas ----------------
    ("Wide-Grip_Lat_Pulldown", "Puxada frontal aberta", ["puxada frontal", "puxada na frente", "puxada alta", "pulldown", "puxada aberta", "puxada pela frente", "puxada pegada aberta", "lat pulldown"]),
    ("Close-Grip_Front_Lat_Pulldown", "Puxada frontal fechada", ["puxada fechada", "puxada triangulo", "puxada pegada fechada", "puxada com triangulo"]),
    ("Underhand_Cable_Pulldowns", "Puxada supinada", ["puxada invertida", "puxada pegada supinada", "puxada pegada invertida"]),
    ("Seated_Cable_Rows", "Remada baixa na polia", ["remada baixa", "remada sentada", "remada na polia", "remada polia baixa", "remada baixa triangulo", "remada sentado", "remada sentada na polia"]),
    ("Bent_Over_Barbell_Row", "Remada curvada com barra", ["remada curvada", "remada barra", "remada com barra"]),
    ("One-Arm_Dumbbell_Row", "Remada unilateral com halter", ["serrote", "remada serrote", "remada unilateral", "remada com halter", "remada unilateral halter"]),
    ("T-Bar_Row_with_Handle", "Remada cavalinho", ["remada t", "cavalinho", "remada em t", "t bar row"]),
    ("Pullups", "Barra fixa", ["barra fixa pronada", "pull up", "pullup", "barra fixa aberta"]),
    ("Chin-Up", "Barra fixa supinada", ["chin up", "chinup", "barra supinada"]),
    ("Straight-Arm_Pulldown", "Pulldown com braços estendidos", ["pulldown braco reto", "pullover na polia", "pull down", "pulldown na polia", "pulldown corda"]),
    ("Hyperextensions_Back_Extensions", "Extensão lombar", ["hiperextensao", "banco lombar", "extensao lombar no banco", "lombar no banco", "hyperextension"]),
    ("Barbell_Deadlift", "Levantamento terra", ["terra", "deadlift", "levantamento terra com barra"]),
    ("Romanian_Deadlift", "Levantamento terra romeno", ["terra romeno", "rdl", "romanian deadlift", "levantamento romeno"]),
    ("Stiff-Legged_Barbell_Deadlift", "Stiff com barra", ["stiff", "stiff barra", "levantamento stiff"]),
    ("Barbell_Shrug", "Encolhimento com barra", ["encolhimento", "encolhimento de ombros", "encolhimento barra", "trapezio com barra"]),
    ("Dumbbell_Shrug", "Encolhimento com halteres", ["encolhimento halter", "encolhimento com halter", "trapezio com halteres"]),
    ("Face_Pull", "Face pull", ["facepull", "puxada para o rosto", "face pull na polia", "puxada de rosto"]),
    # ---------------- Ombros ----------------
    ("Barbell_Shoulder_Press", "Desenvolvimento com barra", ["desenvolvimento", "desenvolvimento militar", "desenvolvimento barra", "military press", "shoulder press barra"]),
    ("Dumbbell_Shoulder_Press", "Desenvolvimento com halteres", ["desenvolvimento halter", "desenvolvimento com halter", "shoulder press", "desenvolvimento ombro"]),
    ("Arnold_Dumbbell_Press", "Desenvolvimento Arnold", ["arnold press", "desenvolvimento arnold com halteres", "arnold"]),
    ("Machine_Shoulder_Military_Press", "Desenvolvimento na máquina", ["desenvolvimento maquina", "desenvolvimento articulado", "shoulder press maquina"]),
    ("Side_Lateral_Raise", "Elevação lateral", ["elevacao lateral com halteres", "lateral", "elevacao lateral halter", "elevacao lateral de ombro"]),
    ("Front_Dumbbell_Raise", "Elevação frontal", ["elevacao frontal com halteres", "frontal", "elevacao frontal halter"]),
    ("Reverse_Flyes", "Crucifixo inverso com halteres", ["crucifixo invertido", "posterior de ombro", "crucifixo inverso", "elevacao posterior", "deltoide posterior"]),
    ("Reverse_Machine_Flyes", "Crucifixo inverso na máquina", ["voador invertido", "peck deck invertido", "crucifixo invertido maquina", "voador inverso"]),
    ("Upright_Barbell_Row", "Remada alta", ["remada alta com barra", "remada alta barra", "upright row"]),
    # ---------------- Bíceps ----------------
    ("Barbell_Curl", "Rosca direta com barra", ["rosca direta", "rosca barra", "rosca com barra", "rosca direta barra reta"]),
    ("EZ-Bar_Curl", "Rosca direta com barra W", ["rosca w", "rosca barra w", "rosca com barra w", "rosca barra ez", "rosca ez"]),
    ("Dumbbell_Alternate_Bicep_Curl", "Rosca alternada com halteres", ["rosca alternada", "rosca halter", "rosca com halteres", "rosca alternada halter"]),
    ("Hammer_Curls", "Rosca martelo", ["rosca martelo com halteres", "martelo", "rosca martelo halter"]),
    ("Preacher_Curl", "Rosca Scott", ["scott", "rosca scott barra", "rosca banco scott", "rosca no banco scott"]),
    ("Alternate_Incline_Dumbbell_Curl", "Rosca inclinada com halteres", ["rosca inclinada", "rosca no banco inclinado"]),
    ("Concentration_Curls", "Rosca concentrada", ["rosca concentrada com halter", "concentrada"]),
    ("Standing_Biceps_Cable_Curl", "Rosca na polia", ["rosca polia", "rosca direta na polia", "rosca cabo", "rosca na polia baixa"]),
    # ---------------- Tríceps ----------------
    ("Triceps_Pushdown", "Tríceps pulley (barra)", ["triceps pulley", "triceps na polia", "triceps polia", "triceps barra", "pulley triceps", "triceps pushdown", "triceps polia barra"]),
    ("Triceps_Pushdown_-_Rope_Attachment", "Tríceps corda", ["triceps na corda", "triceps polia corda", "triceps com corda", "pulley corda", "triceps pulley corda"]),
    ("EZ-Bar_Skullcrusher", "Tríceps testa", ["triceps testa com barra", "skull crusher", "skullcrusher", "testa", "triceps testa barra w", "triceps testa com barra w"]),
    ("Seated_Triceps_Press", "Tríceps francês com halter", ["triceps frances", "frances", "triceps frances halter", "triceps frances sentado"]),
    ("Cable_Rope_Overhead_Triceps_Extension", "Tríceps francês na polia", ["triceps frances polia", "triceps acima da cabeca na polia", "triceps overhead", "triceps frances na corda"]),
    ("Bench_Dips", "Tríceps no banco", ["mergulho no banco", "triceps banco", "mergulho banco", "bench dips", "dips no banco"]),
    ("Dips_-_Triceps_Version", "Paralelas (foco no tríceps)", ["paralelas triceps", "mergulho triceps", "dips triceps", "paralelas", "mergulho nas paralelas"]),
    ("Tricep_Dumbbell_Kickback", "Tríceps coice", ["coice", "triceps coice com halter", "kickback", "triceps kickback"]),
    # ---------------- Pernas ----------------
    ("Barbell_Squat", "Agachamento livre com barra", ["agachamento", "agachamento livre", "agachamento com barra", "squat", "agachamento barra"]),
    ("Goblet_Squat", "Agachamento goblet", ["goblet", "agachamento com halter", "agachamento taça", "agachamento taca"]),
    ("Hack_Squat", "Agachamento hack", ["hack", "hack squat", "agachamento na maquina hack", "agachamento no hack"]),
    ("Smith_Machine_Squat", "Agachamento no smith", ["agachamento smith", "smith squat", "agachamento no smith machine", "agachamento guiado"]),
    ("Bodyweight_Squat", "Agachamento com peso do corpo", ["agachamento livre sem peso", "agachamento sem peso", "air squat", "agachamento corporal"]),
    ("Leg_Press", "Leg press 45°", ["leg press", "legpress", "leg 45", "leg press 45", "leg press inclinado"]),
    ("Leg_Extensions", "Cadeira extensora", ["extensora", "extensora de pernas", "leg extension", "extensao de pernas", "extensao de joelhos"]),
    ("Lying_Leg_Curls", "Mesa flexora", ["flexora deitada", "flexora deitado", "leg curl deitado", "mesa flexora de pernas"]),
    ("Seated_Leg_Curl", "Cadeira flexora", ["flexora sentada", "flexora sentado", "leg curl sentado", "flexora"]),
    ("Dumbbell_Lunges", "Avanço com halteres", ["avanco", "afundo", "afundo com halteres", "avanco halter", "lunge", "afundo halter", "avanço"]),
    ("Barbell_Walking_Lunge", "Passada com barra", ["passada", "walking lunge", "avanco caminhando", "passada caminhando", "afundo caminhando"]),
    ("Split_Squat_with_Dumbbells", "Agachamento búlgaro", ["bulgaro", "agachamento bulgaro", "afundo bulgaro", "agachamento bulgaro com halteres", "split squat", "bulgarian split squat", "agachamento unilateral"]),
    ("Dumbbell_Step_Ups", "Step-up com halteres", ["step up", "subida no banco", "subida no step", "step-up", "stepup"]),
    ("Thigh_Abductor", "Cadeira abdutora", ["abdutora", "abdutor", "maquina abdutora", "abducao de quadril na maquina"]),
    ("Thigh_Adductor", "Cadeira adutora", ["adutora", "adutor", "maquina adutora", "aducao de quadril na maquina"]),
    ("Standing_Calf_Raises", "Panturrilha em pé", ["panturrilha", "gemeos", "gemeos em pe", "panturrilha em pe na maquina", "elevacao de panturrilha", "calf raise", "panturrilha no smith"]),
    ("Seated_Calf_Raise", "Panturrilha sentado", ["gemeos sentado", "panturrilha sentada", "panturrilha na maquina sentado", "soleo sentado"]),
    ("Calf_Press_On_The_Leg_Press_Machine", "Panturrilha no leg press", ["panturrilha leg press", "gemeos no leg", "gemeos leg press", "panturrilha no leg"]),
    ("Barbell_Hip_Thrust", "Elevação pélvica", ["hip thrust", "elevacao pelvica com barra", "hipthrust", "ponte com barra", "elevacao de quadril"]),
    ("Barbell_Glute_Bridge", "Ponte de glúteo com barra", ["ponte de gluteo", "glute bridge", "ponte gluteo", "ponte com barra no chao"]),
    ("Glute_Kickback", "Coice de glúteo", ["coice no gluteo", "gluteo quatro apoios", "glute kickback", "coice de gluteo", "coice gluteo"]),
    ("One-Legged_Cable_Kickback", "Coice de glúteo na polia", ["coice na polia", "gluteo na polia", "kickback na polia", "coice polia"]),
    # ---------------- Core ----------------
    ("Crunches", "Abdominal crunch", ["abdominal", "abdominal tradicional", "crunch", "abdominal supra", "abdominal no solo"]),
    ("Cable_Crunch", "Abdominal na polia", ["abdominal polia", "crunch na polia", "abdominal corda", "abdominal na polia alta"]),
    ("Hanging_Leg_Raise", "Elevação de pernas na barra", ["elevacao de pernas suspenso", "elevacao de pernas na barra fixa", "hanging leg raise", "abdominal na barra", "elevacao de pernas pendurado"]),
    ("Flat_Bench_Lying_Leg_Raise", "Elevação de pernas deitado", ["elevacao de pernas", "abdominal infra", "infra", "elevacao de pernas no banco"]),
    ("Plank", "Prancha", ["prancha abdominal", "plank", "prancha isometrica", "prancha frontal"]),
    ("Side_Bridge", "Prancha lateral", ["side plank", "prancha de lado", "prancha lateral isometrica"]),
    ("Russian_Twist", "Rotação russa", ["russian twist", "abdominal rotacao", "abdominal obliquo", "giro russo", "rotacao russa com peso"]),
    ("Mountain_Climbers", "Escalador", ["mountain climber", "mountain climbers", "escaladores", "escalador no solo"]),
    ("Ab_Crunch_Machine", "Abdominal na máquina", ["abdominal maquina", "maquina de abdominal", "abdominal no aparelho"]),
]

MUSCLES_PT = {
    "abdominals": "Abdômen", "abductors": "Abdutores", "adductors": "Adutores",
    "biceps": "Bíceps", "calves": "Panturrilhas", "chest": "Peito",
    "forearms": "Antebraços", "glutes": "Glúteos", "hamstrings": "Posterior de coxa",
    "lats": "Dorsais", "lower back": "Lombar", "middle back": "Costas (meio)",
    "neck": "Pescoço", "quadriceps": "Quadríceps", "shoulders": "Ombros",
    "traps": "Trapézio", "triceps": "Tríceps",
}
EQUIPMENT_PT = {
    "barbell": "Barra", "dumbbell": "Halteres", "cable": "Polia", "machine": "Máquina",
    "body only": "Peso do corpo", "e-z curl bar": "Barra W", "kettlebells": "Kettlebell",
    "bands": "Elástico", "other": "Outro", "exercise ball": "Bola", "medicine ball": "Medicine ball",
    "foam roll": "Rolo", None: "Outro",
}


def _download_image(client: httpx.Client, exercise_id: str, index: int) -> Image.Image | None:
    resp = client.get(f"{IMAGE_BASE}/{exercise_id}/{index}.jpg")
    if resp.status_code != 200:
        return None
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def main() -> int:
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        dataset = {x["id"]: x for x in client.get(DATASET_URL).raise_for_status().json()}

        missing = [c[0] for c in CURATED if c[0] not in dataset]
        if missing:
            print("IDs que não existem no dataset:", *missing, sep="\n  - ")
            return 1

        catalog = []
        for exercise_id, name_pt, aliases in CURATED:
            src = dataset[exercise_id]
            saved = []
            for i in range(len(src.get("images", []))):
                img = _download_image(client, exercise_id, i)
                if img is None:
                    continue
                if img.width > MAX_WIDTH:
                    img = img.resize((MAX_WIDTH, round(img.height * MAX_WIDTH / img.width)), Image.LANCZOS)
                target = OUT_IMAGES / exercise_id / f"{i}.webp"
                target.parent.mkdir(parents=True, exist_ok=True)
                img.save(target, "WEBP", quality=WEBP_QUALITY, method=6)
                saved.append(i)
            if not saved:
                print(f"AVISO: sem imagens para {exercise_id}, ignorado")
                continue

            primary = [MUSCLES_PT.get(m, m.title()) for m in src.get("primaryMuscles", [])]
            secondary = [MUSCLES_PT.get(m, m.title()) for m in src.get("secondaryMuscles", [])]
            catalog.append({
                "id": exercise_id,
                "name": name_pt,
                "aliases": aliases,
                "primary_muscles": primary,
                "secondary_muscles": secondary,
                "equipment": EQUIPMENT_PT.get(src.get("equipment"), "Outro"),
                "image_count": len(saved),
            })
            print(f"ok  {exercise_id:50s} {len(saved)} img  ->  {name_pt}")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n{len(catalog)} exercícios no catálogo -> {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
