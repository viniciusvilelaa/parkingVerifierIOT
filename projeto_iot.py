import cv2
import numpy as np
import easyocr
import sqlite3
from datetime import datetime

# Conexão com o banco
conn = sqlite3.connect("estacionamento.db")
cursor = conn.cursor()

# Criação das tabelas, se não existirem
cursor.execute("""
CREATE TABLE IF NOT EXISTS vagas (
    id INTEGER PRIMARY KEY,
    ocupada BOOLEAN,
    placa TEXT,
    horario DATETIME
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT,
    vaga INTEGER,
    entrada DATETIME,
    saida DATETIME
)
""")

# Carregar imagem do estacionamento
img = cv2.imread("estacionamento_exemplo.jpg")

# Defina manualmente as coordenadas das vagas (x, y, largura, altura)
# Exemplo com 2 vagas (adicione mais conforme necessário)
vagas = [
    (30, 60, 120, 100),   # Vaga 1
    (140, 60, 230, 100)  # Vaga 2
]

# Inicializa o leitor OCR
ocr = easyocr.Reader(['pt', 'en'])

for i, (x, y, w, h) in enumerate(vagas, start=1):
    vaga_img = img[y:y+h, x:x+w]
    gray = cv2.cvtColor(vaga_img, cv2.COLOR_BGR2GRAY)
    media = np.mean(gray)

    if media < 120:  # parâmetro simples para detectar vaga ocupada
        vaga_ocupada = True
        resultado = ocr.readtext(vaga_img)
        placa = resultado[0][1] if resultado else "desconhecida"
        horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"[VAGA {i}] OCUPADA - Placa: {placa}")

        cursor.execute("REPLACE INTO vagas (id, ocupada, placa, horario) VALUES (?, ?, ?, ?)",
                       (i, True, placa, horario))

        cursor.execute("INSERT INTO historico (placa, vaga, entrada) VALUES (?, ?, ?)",
                       (placa, i, horario))
    else:
        print(f"[VAGA {i}] LIVRE")
        cursor.execute("REPLACE INTO vagas (id, ocupada, placa, horario) VALUES (?, ?, ?, ?)",
                       (i, False, None, None))

    # Mostrar retângulo visual
    cor = (0, 0, 255) if media < 120 else (0, 255, 0)
    cv2.rectangle(img, (x, y), (x + w, y + h), cor, 2)

# Finalizar
conn.commit()
conn.close()

cv2.imshow("Resultado", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
