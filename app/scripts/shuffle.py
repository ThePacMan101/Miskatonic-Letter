import json
import random

# Caminho do arquivo JSON de entrada
input_file = "../data/posts.json"
# Caminho do arquivo JSON de saída
output_file = "../data/posts.json"

# Lê o JSON
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Embaralha as entradas
random.shuffle(data)

# Salva o JSON embaralhado
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"{len(data)} entradas embaralhadas e salvas em {output_file}.")
