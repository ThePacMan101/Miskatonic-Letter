# import_posts.py
import json
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Base, Posts, Users, Badges, Tags, PostsTags

# -------------------------------------------------------------------
# Database setup
# -------------------------------------------------------------------
engine = create_engine("sqlite:///../data/database.db", echo=True, future=True)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# -------------------------------------------------------------------
# Helper: get or create
# -------------------------------------------------------------------
def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        params = {**kwargs}
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        session.commit()
        return instance

# -------------------------------------------------------------------
# Import JSON into DB
# -------------------------------------------------------------------
with open("../data/posts.json", "r", encoding="utf-8") as f:
    posts_data = json.load(f)

for post in posts_data:
    # 1. User
    user = get_or_create(
        session,
        Users,
        user_avatar=post["author"]["avatar"],
        user_name=post["author"]["name"],
    )

    # 2. Badge
    badge = get_or_create(
        session,
        Badges,
        badge_title=post["badge"]["title"],
        badge_lable=post["badge"]["label"],
    )

    # 3. Views: handle "4.6k" style
    views = post["stats"]["views"]
    if isinstance(views, str):
        if "k" in views:
            views = int(float(views.replace("k", "")) * 1000)
        else:
            views = int(views)
    else:
        views = int(views)

    # 4. Post
    post_obj = Posts(
        post_title=post["title"],
        post_exerpt=post["excerpt"],
        author_id=user.user_id,
        post_date=datetime.strptime(post["date"], "%Y-%m-%d").date(),
        post_views=views,
        post_replies=post["stats"]["replies"],
        post_credibility=post["stats"]["credibility"],
        post_content="\n\n".join(post["content"]),
        badge_id=badge.badge_id,
    )
    session.add(post_obj)
    session.commit()  # so post_id is available

    # 5. Tags (many-to-many)
    for t in post["tags"]:
        tag = get_or_create(session, Tags, tag_lable=t)
        post_tag = PostsTags(post_id=post_obj.post_id, tag_id=tag.tag_id)
        session.add(post_tag)

    session.commit()

session.close()
print("✅ Database built successfully!")
