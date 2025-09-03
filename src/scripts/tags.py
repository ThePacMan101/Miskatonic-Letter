import json

# Caminho do arquivo JSON
input_file = "../posts.json"

# Lê o JSON
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Cria um set para armazenar tags únicas
unique_tags = set()

# Percorre todas as entradas e adiciona as tags ao set
for entry in data:
    tags = entry.get("tags", [])
    unique_tags.update(tags)

# Imprime as tags únicas
print("Tags distintas encontradas:")
for tag in sorted(unique_tags):
    print(tag)
