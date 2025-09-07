from sqlalchemy import create_engine, Column, Integer, String, Date,Text,ForeignKey
import sqlalchemy
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./data/database.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = sqlalchemy.orm.declarative_base()

class Posts(Base):
    __tablename__    = "Posts"
    post_id          = Column(Integer,primary_key=True,index=True)
    post_title       = Column(String,nullable=False)
    post_exerpt      = Column(String)
    author_id        = Column(Integer,ForeignKey("Users.user_id"),nullable=False)
    post_date        = Column(Date)
    post_views       = Column(Integer,default=0)
    post_replies     = Column(Integer,default=0)
    post_credibility = Column(Integer,default=0)
    post_content     = Column(Text)
    badge_id         = Column(Integer,ForeignKey("Badges.badge_id"))

class Users(Base):
    __tablename__    = "Users"
    user_id          = Column(Integer,primary_key=True,index=True)
    user_avatar      = Column(String(2))
    user_name        = Column(String)

class Badges(Base):
    __tablename__    = "Badges"
    badge_id         = Column(Integer,primary_key=True)
    badge_title      = Column(String)
    badge_lable      = Column(String)

class PostsTags(Base):
    __tablename__    = "PostsTags"
    post_id          = Column(Integer,ForeignKey("Posts.post_id"),primary_key=True)
    tag_id           = Column(Integer,ForeignKey("Tags.tag_id"  ),primary_key=True)

class Tags(Base):
    __tablename__    = "Tags"
    tag_id           = Column(Integer,primary_key=True,index=True)
    tag_lable        = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def serialize_post_face(post, db):
    author = db.query(Users).filter_by(user_id=post.author_id).first()
    badge = db.query(Badges).filter_by(badge_id=post.badge_id).first()
    tag_ids = db.query(PostsTags).filter_by(post_id=post.post_id).all()
    tags = []
    for pt in tag_ids:
        tag = db.query(Tags).filter_by(tag_id=pt.tag_id).first()
        if tag:
            tags.append(tag.tag_lable)
    return {
        "id": post.post_id,
        "title": post.post_title,
        "exerpt": post.post_exerpt,
        "date": post.post_date,
        "author": {
            "name": author.user_name if author else "",
            "avatar": author.user_avatar if author else "",
        },
        "badge": {
            "label": badge.badge_lable.upper() if badge else "",
            "title": badge.badge_title if badge else "",
        },
        "tags": tags,
        "stats": {
            "views": post.post_views,
            "replies": post.post_replies,
            "credibility": post.post_credibility,
        }
    }

def serialize_post_content(post,db):
    author = db.query(Users).filter_by(user_id=post.author_id).first()
    badge = db.query(Badges).filter_by(badge_id=post.badge_id).first()
    tag_ids = db.query(PostsTags).filter_by(post_id=post.post_id).all()
    tags = []
    for pt in tag_ids:
        tag = db.query(Tags).filter_by(tag_id=pt.tag_id).first()
        if tag:
            tags.append(tag.tag_lable)
    return {
        "id": post.post_id,
        "title": post.post_title,
        "exerpt": post.post_exerpt,
        "content": post.post_content,
        "date": post.post_date,
        "author": {
            "name": author.user_name if author else "",
            "avatar": author.user_avatar if author else "",
        },
        "badge": {
            "label": badge.badge_lable.upper() if badge else "",
            "title": badge.badge_title if badge else "",
        },
        "tags": tags,
        "stats": {
            "views": post.post_views,
            "replies": post.post_replies,
            "credibility": post.post_credibility,
        }
    }