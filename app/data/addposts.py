import json
import sqlite3

def insert_posts_from_json(db_path, json_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            posts_data = json.load(f)

        for post in posts_data:
            # Gerenciar a criação de Usuário
            user = post.get('author')
            cursor.execute("SELECT user_id FROM Users WHERE user_name = ?", (user['user_name'],))
            user_id = cursor.fetchone()
            if not user_id:
                cursor.execute("INSERT INTO Users (user_avatar, user_name) VALUES (?, ?)",
                               (user['user_avatar'], user['user_name']))
                user_id = cursor.lastrowid
            else:
                user_id = user_id[0]

            # Gerenciar a criação de Badge
            badge = post.get('badge')
            badge_id = None
            if badge:
                cursor.execute("SELECT badge_id FROM Badges WHERE badge_lable = ?", (badge['badge_lable'],))
                badge_id = cursor.fetchone()
                if not badge_id:
                    cursor.execute("INSERT INTO Badges (badge_title, badge_lable) VALUES (?, ?)",
                                   (badge['badge_title'], badge['badge_lable']))
                    badge_id = cursor.lastrowid
                else:
                    badge_id = badge_id[0]

            # Inserir o Post Principal
            cursor.execute("""
                INSERT INTO Posts (
                    post_title, post_exerpt, author_id, post_date,
                    post_views, post_replies, post_credibility, post_content, badge_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post['post_title'],
                post.get('post_exerpt'),
                user_id,
                post.get('post_date'),
                post.get('post_views', 0),
                post.get('post_replies', 0),
                post.get('post_credibility', 0),
                post.get('post_content'),
                badge_id
            ))
            post_id = cursor.lastrowid

            # Gerenciar a criação e associação de Tags
            tags = post.get('tags', [])
            for tag_label in tags:
                cursor.execute("SELECT tag_id FROM Tags WHERE tag_lable = ?", (tag_label,))
                tag_id = cursor.fetchone()
                if not tag_id:
                    cursor.execute("INSERT INTO Tags (tag_lable) VALUES (?)", (tag_label,))
                    tag_id = cursor.lastrowid
                else:
                    tag_id = tag_id[0]
                
                # Inserir na tabela de junção PostsTags
                cursor.execute("INSERT INTO PostsTags (post_id, tag_id) VALUES (?, ?)", (post_id, tag_id))

        conn.commit()
        print("Dados inseridos com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        conn.rollback()
    finally:
        conn.close()

# Exemplo de uso:
if __name__ == '__main__':
    DB_FILE = 'database.db'
    JSON_FILE = 'newposts.json'
    insert_posts_from_json(DB_FILE, JSON_FILE)