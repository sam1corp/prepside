from __future__ import annotations
import json
import os
import uuid
import random
import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Cookie, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

DATABASE_URL = "sqlite:///./exam.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# SQLite may return DateTime(timezone=True) values as naive datetimes.
# Keep stored values in UTC and explicitly attach UTC before comparisons/responses.
def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def as_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


CHAPTERS = {
    "Mathematics": [
        {"id":"M1-1","name":"১. প্রথম অধ্যায়: ম্যাট্রিক্স ও নির্ণায়ক"}, {"id":"M1-2","name":"২. দ্বিতীয় অধ্যায়: ভেক্টর"}, {"id":"M1-3","name":"৩. তৃতীয় অধ্যায়: সরলরেখা"}, {"id":"M1-4","name":"৪. চতুর্থ অধ্যায়: বৃত্ত"}, {"id":"M1-5","name":"৫. পঞ্চম অধ্যায়: বিন্যাস ও সমাবেশ"}, {"id":"M1-6","name":"৬. ষষ্ঠ অধ্যায়: ত্রিকোণমিতিক অনুপাত"}, {"id":"M1-7","name":"৭. সপ্তম অধ্যায়: সংযুক্ত কোণের ত্রিকোণমিতিক অনুপাত"}, {"id":"M1-8","name":"৮. অষ্টম অধ্যায়: ফাংশন ও ফাংশনের লেখচিত্র"}, {"id":"M1-9","name":"৯. নবম অধ্যায়: অন্তরীকরণ"}, {"id":"M1-10","name":"১০. দশম অধ্যায়: যোগজীকরণ"},
        {"id":"M2-1","name":"১. প্রথম অধ্যায়: বাস্তব সংখ্যা ও অসমতা"}, {"id":"M2-2","name":"২. দ্বিতীয় অধ্যায়: যোগাশ্রয়ী প্রোগ্রাম"}, {"id":"M2-3","name":"৩. তৃতীয় অধ্যায়: অবাস্তব সংখ্যা"}, {"id":"M2-4","name":"৪. চতুর্থ অধ্যায়: বহুপদী ও বহুপদী সমীকরণ"}, {"id":"M2-5","name":"৫. পঞ্চম অধ্যায়: দ্বিপদী বিস্তৃতি"}, {"id":"M2-6","name":"৬. ষষ্ঠ অধ্যায়: কনিক"}, {"id":"M2-7","name":"৭. সপ্তম অধ্যায়: বিপরীত ত্রিকোণমিতিক ফাংশন ও ত্রিকোণমিতিক সমীকরণ"}, {"id":"M2-8","name":"৮. অষ্টম অধ্যায়: স্থিতিবিদ্যা"}, {"id":"M2-9","name":"৯. নবম অধ্যায়: সমতলে বস্তুকণার গতি"}, {"id":"M2-10","name":"১০. দশম অধ্যায়: বিস্তার পরিমাপ ও সম্ভাবনা"}
    ],
    "Physics": [
        {"id":"P1-1","name":"1. ভৌত জগত ও পরিমাপ"}, {"id":"P1-2","name":"2. ভেক্টর"}, {"id":"P1-3","name":"3. গতিবিদ্যা"}, {"id":"P1-4","name":"4. নিউটনিয় বলবিদ্যা"}, {"id":"P1-5","name":"5. কাজ, শক্তি, ক্ষমতা"}, {"id":"P1-6","name":"6. মহাকর্ষ ও অভিকর্ষ"}, {"id":"P1-7","name":"7. পদার্থের গাঠনিক ধর্ম"}, {"id":"P1-8","name":"8. পর্যায়বৃত্ত গতি"}, {"id":"P1-9","name":"9. তরঙ্গ"}, {"id":"P1-10","name":"10. আদর্শ গ্যাস ও গ্যাসের গতিতত্ব"},
        {"id":"P2-1","name":"1. তাপগতিবিদ্যা"}, {"id":"P2-2","name":"2. স্থির তড়িৎ"}, {"id":"P2-3","name":"3. চল তড়িৎ"}, {"id":"P2-4","name":"4. তড়িৎ প্রবাহের চুম্বক ক্রিয়া ও চুম্বকত্ব"}, {"id":"P2-5","name":"5. তড়িৎ চুম্বক আবেশ ও পরিবর্তী প্রবাহ"}, {"id":"P2-6","name":"6. জ্যামিতিক আলোকবিজ্ঞান"}, {"id":"P2-7","name":"7. ভৌত আলোকবিজ্ঞান"}, {"id":"P2-8","name":"8. আধুনিক পদার্থবিজ্ঞান"}, {"id":"P2-9","name":"9. পরমাণু মডেল এবং নিউক্লিও পদার্থ"}, {"id":"P2-10","name":"10. সেমিকন্ডাক্টর ও ইলেকট্রনিক্স"}, {"id":"P2-11","name":"11. জ্যোতির্বিদ্যা"}
    ],
    "Chemistry": [
        {"id":"C1-1","name":"1. ল্যাবরেটরির নিরাপদ ব্যবহার"}, {"id":"C1-2","name":"2. গুণগত রসায়ন"}, {"id":"C1-3","name":"3. মৌলের পরজায়ব্রিত্ত ধর্ম"}, {"id":"C1-4","name":"4. রাসায়নিক পরিবর্তন"}, {"id":"C1-5","name":"5. কর্মমুখী রসায়ন"},
        {"id":"C2-1","name":"1. পরিবেশ রসায়ন"}, {"id":"C2-2","name":"2. জৈব যৌগ"}, {"id":"C2-3","name":"3. পরিমাণগত রসায়ন"}, {"id":"C2-4","name":"4. তড়িৎ রসায়ন"}, {"id":"C2-5","name":"5. অর্থনীতিক রসায়ন"}
    ]
}
PAPER_NAMES = {
    "Mathematics": [("M1", "Higher Math 1st Paper", "M1-"), ("M2", "Higher Math 2nd Paper", "M2-")],
    "Physics": [("P1", "Physics 1st Paper", "P1-"), ("P2", "Physics 2nd Paper", "P2-")],
    "Chemistry": [("C1", "Chemistry 1st Paper", "C1-"), ("C2", "Chemistry 2nd Paper", "C2-")]
}

def chapter_id_for_question(subject: str, number: int, stored: Optional[str] = None) -> str:
    valid={x["id"] for x in CHAPTERS[subject]}
    if stored in valid:
        return stored
    ids=[x["id"] for x in CHAPTERS[subject]]
    return ids[(number-1) % len(ids)]

app = FastAPI(title="BUET AI Exam Engine", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

class Base(DeclarativeBase): pass
class Exam(Base):
    __tablename__ = "exams"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))

class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column(String(50))
    number: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text())
    marks: Mapped[int] = mapped_column(Integer, default=10)
    difficulty: Mapped[str] = mapped_column(String(30), default='Medium-Hard')
    topic: Mapped[str] = mapped_column(String(120))
    paper_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    chapter_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="published")
    source_file: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_exam: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    source_year: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    source_session: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    source_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    answer_text: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    solution_text: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    rubric_json: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    content_json: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    original_language: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

class ImportedResource(Base):
    __tablename__ = "imported_resources"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(120))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), default="uploaded")
    page_count: Mapped[int] = mapped_column(Integer, default=1)

class DraftQuestion(Base):
    __tablename__ = "draft_questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("imported_resources.id"))
    page_number: Mapped[int] = mapped_column(Integer)
    subject: Mapped[str] = mapped_column(String(50))
    paper_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    chapter_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    question_text: Mapped[str] = mapped_column(Text())
    content_json: Mapped[str] = mapped_column(Text(), default="[]")
    answer_text: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    solution_text: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    difficulty: Mapped[str] = mapped_column(String(30), default="Medium")
    rubric_json: Mapped[str] = mapped_column(Text(), default="[]")
    source_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bbox_json: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="review")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class AuthSession(Base):
    __tablename__ = "auth_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Problem(Base):
    __tablename__ = "problems"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Attempt(Base):
    __tablename__ = "attempts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    student_name: Mapped[str] = mapped_column(String(120))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted: Mapped[bool] = mapped_column(Boolean, default=False)
    config_json: Mapped[str] = mapped_column(Text(), default="[]")

class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("attempts.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    answer_text: Mapped[str] = mapped_column(Text(), default="")
    handwriting_data: Mapped[str] = mapped_column(Text(), default="[]")
    answer_mode: Mapped[str] = mapped_column(String(20), default="typing")
    image_urls: Mapped[str] = mapped_column(Text(), default="[]")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    score: Mapped[Optional[float]] = mapped_column(nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

def migrate_questions_table():
    cols = {row[1] for row in engine.connect().exec_driver_sql("PRAGMA table_info(questions)").fetchall()}
    additions = {
        "paper_id": "VARCHAR(20)", "chapter_id": "VARCHAR(30)", "status": "VARCHAR(20) DEFAULT 'published'", "difficulty": "VARCHAR(30) DEFAULT 'Medium-Hard'",
        "source_file": "VARCHAR(255)", "source_page": "INTEGER", "source_exam": "VARCHAR(30)", "source_year": "VARCHAR(30)", "source_session": "VARCHAR(60)", "source_image_url": "VARCHAR(500)",
        "answer_text": "TEXT", "solution_text": "TEXT", "rubric_json": "TEXT", "content_json": "TEXT", "original_language": "VARCHAR(20)"
    }
    with engine.begin() as conn:
        for name, sql in additions.items():
            if name not in cols:
                conn.exec_driver_sql(f"ALTER TABLE questions ADD COLUMN {name} {sql}")

Base.metadata.create_all(engine)
migrate_questions_table()

def migrate_answers_table():
    cols = {row[1] for row in engine.connect().exec_driver_sql("PRAGMA table_info(answers)").fetchall()}
    additions = {"handwriting_data": "TEXT DEFAULT '[]'", "answer_mode": "VARCHAR(20) DEFAULT 'typing'"}
    with engine.begin() as conn:
        for name, sql in additions.items():
            if name not in cols:
                conn.exec_driver_sql(f"ALTER TABLE answers ADD COLUMN {name} {sql}")

migrate_answers_table()

def _curated_path():
    p = Path(__file__).resolve().parents[2] / 'data' / 'curated_questions.json'
    if not p.exists():
        p = Path(__file__).resolve().parents[1] / 'data' / 'curated_questions.json'
    return p

def _copy_curated_assets():
    assets_dir = _curated_path().parent / 'assets'
    if assets_dir.exists():
        for src in assets_dir.iterdir():
            if src.is_file():
                dest = UPLOAD_DIR / src.name
                if not dest.exists():
                    dest.write_bytes(src.read_bytes())
    # legacy page images used by the older curated bank
    for fname in ['circle_practice_page2.png', 'vector_practice_page1.png']:
        src = _curated_path().parent / fname
        if src.exists() and not (UPLOAD_DIR / fname).exists():
            (UPLOAD_DIR / fname).write_bytes(src.read_bytes())

def _item_key(item):
    # Prefer stable source identity; fall back to text for hand-added questions.
    return (
        item.get('subject',''), item.get('source_file',''), item.get('source_page'),
        item.get('source_exam',''), item.get('source_year',''), item.get('question_no'),
        item.get('question_text','').strip()
    )

def seed():
    """Seed/refresh the curated written-question bank without generative AI."""
    curated_path = _curated_path()
    curated = json.loads(curated_path.read_text(encoding='utf-8')) if curated_path.exists() else []
    _copy_curated_assets()
    with Session(engine) as db:
        # Old sample/demo questions are never eligible for exams.
        db.query(Question).filter(Question.source_file.is_(None)).update({Question.status:'archived'})

        existing = db.scalars(select(Question)).all()
        by_key = {}
        for q in existing:
            by_key[(_safe(q.subject), _safe(q.source_file), q.source_page, _safe(q.source_exam), _safe(q.source_year), q.number, _safe(q.text))] = q

        # Determine the next display number per subject.
        next_num = {}
        for subj in CHAPTERS:
            nums = [q.number for q in existing if q.subject == subj]
            next_num[subj] = (max(nums) if nums else 0) + 1

        for item in curated:
            blocks=[]
            for b in item.get('content_blocks', []):
                bb=dict(b)
                if bb.get('type')=='image' and bb.get('content'):
                    bb['content']='/uploads/' + Path(str(bb['content'])).name
                blocks.append(bb)
            text=item.get('question_text','').strip()
            # Find an exact existing row by immutable source coordinates + text.
            qmatch = next((q for q in existing if (
                q.subject == item.get('subject') and q.source_file == item.get('source_file') and
                q.source_page == item.get('source_page') and q.source_exam == item.get('source_exam') and
                q.source_year == item.get('source_year') and q.text.strip() == text
            )), None)
            if qmatch is None:
                qmatch=Question(subject=item['subject'], number=next_num[item['subject']]); next_num[item['subject']]+=1; db.add(qmatch); existing.append(qmatch)
            qmatch.text=text
            qmatch.marks=10
            qmatch.difficulty=item.get('difficulty','Medium-Hard')
            qmatch.topic=item.get('chapter_id','')
            qmatch.paper_id=item.get('paper_id')
            qmatch.chapter_id=item.get('chapter_id')
            qmatch.status='published'
            qmatch.source_file=item.get('source_file')
            qmatch.source_page=item.get('source_page')
            qmatch.source_exam=item.get('source_exam')
            qmatch.source_year=item.get('source_year')
            qmatch.source_session=item.get('source_session')
            qmatch.source_image_url=item.get('original_image') or (('/uploads/'+Path(item['content_blocks'][0]['content']).name) if item.get('content_blocks') and item['content_blocks'][0].get('type')=='image' else None)
            qmatch.answer_text=item.get('answer_text')
            qmatch.solution_text=item.get('solution_text')
            qmatch.rubric_json=item.get('rubric_json','[]')
            qmatch.content_json=json.dumps(blocks,ensure_ascii=False)
            qmatch.original_language=item.get('original_language') or 'bn'
        db.commit()

def _safe(v):
    return '' if v is None else str(v)

Base.metadata.create_all(engine)

# Lightweight SQLite migration for existing installations.
def migrate_auth_tables():
    with engine.begin() as conn:
        cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(attempts)").fetchall()}
        if "user_id" not in cols:
            conn.exec_driver_sql("ALTER TABLE attempts ADD COLUMN user_id INTEGER")

migrate_auth_tables()

seed()

def sync_curated_question_metadata():
    """Keep the bundled database aligned with curated question JSON, including original-language crops."""
    curated_path = Path(__file__).resolve().parents[2] / 'data' / 'curated_questions.json'
    if not curated_path.exists():
        curated_path = Path(__file__).resolve().parents[1] / 'data' / 'curated_questions.json'
    if not curated_path.exists():
        return
    curated = json.loads(curated_path.read_text(encoding='utf-8'))
    with Session(engine) as db:
        by_subject = {}
        for item in curated:
            by_subject.setdefault(item['subject'], []).append(item)
        changed = False
        for subject, items in by_subject.items():
            qs = db.scalars(select(Question).where(Question.subject == subject, Question.status == 'published').order_by(Question.number)).all()
            for idx, item in enumerate(items):
                if idx >= len(qs):
                    break
                q = qs[idx]
                new_image = item.get('original_image')
                new_page = item.get('source_page')
                if new_image and q.source_image_url != new_image:
                    q.source_image_url = new_image; changed = True
                if new_page and q.source_page != new_page:
                    q.source_page = new_page; changed = True
                if q.text != item.get('question_text', q.text):
                    q.text = item.get('question_text', q.text); changed = True
                if q.answer_text != item.get('answer_text', q.answer_text):
                    q.answer_text = item.get('answer_text', q.answer_text); changed = True
        if changed:
            db.commit()

sync_curated_question_metadata()

def repair_question_latex():
    # Repair only known malformed control characters from the older seed data.
    changed = False
    with Session(engine) as db:
        questions = db.scalars(select(Question)).all()
        for q in questions:
            text = q.text.replace("\x0c", "\\f")
            text = text.replace("A\tan B", "A\\tan B") if "A\tan B" in text else text
            if text != q.text:
                q.text = text
                changed = True
        if changed:
            db.commit()

repair_question_latex()

class SignupIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=8, max_length=20)
    password: str = Field(min_length=8, max_length=128)

class LoginIn(BaseModel):
    phone: str = Field(min_length=8, max_length=20)
    password: str = Field(min_length=8, max_length=128)

def normalize_bd_phone(phone: str) -> str:
    p = ''.join(ch for ch in phone.strip() if ch.isdigit() or ch == '+')
    if p.startswith('00880'): p = '+880' + p[5:]
    elif p.startswith('880'): p = '+' + p
    elif p.startswith('01'): p = '+88' + p
    if not (len(p) == 14 and p.startswith('+8801') and p[5] in '3456789'):
        raise HTTPException(400, 'Enter a valid Bangladeshi mobile number, e.g. 01712345678')
    return p

def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310_000)
    return 'pbkdf2_sha256$310000$' + base64.urlsafe_b64encode(salt).decode() + '$' + base64.urlsafe_b64encode(dk).decode()

def verify_password(password: str, encoded: str) -> bool:
    try:
        _, rounds, salt_b64, hash_b64 = encoded.split('$', 3)
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(hash_b64.encode())
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, int(rounds))
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def session_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def current_user(db: Session, auth_token: str | None) -> User | None:
    if not auth_token: return None
    row = db.scalar(select(AuthSession).where(AuthSession.token_hash == session_token_hash(auth_token)))
    if not row: return None
    if row.expires_at <= utc_now_naive():
        db.delete(row); db.commit(); return None
    return db.get(User, row.user_id)

def require_user(db: Session, auth_token: str | None) -> User:
    user = current_user(db, auth_token)
    if not user: raise HTTPException(401, 'Please log in first')
    return user

@app.post('/api/auth/signup')
def signup(payload: SignupIn, response: Response):
    phone = normalize_bd_phone(payload.phone)
    with Session(engine) as db:
        if db.scalar(select(User).where(User.phone == phone)):
            raise HTTPException(409, 'An account already exists with this phone number')
        user = User(name=payload.name.strip(), phone=phone, password_hash=hash_password(payload.password), created_at=utc_now_naive())
        db.add(user); db.flush()
        token = secrets.token_urlsafe(48)
        db.add(AuthSession(user_id=user.id, token_hash=session_token_hash(token), created_at=utc_now_naive(), expires_at=utc_now_naive()+timedelta(days=30)))
        db.commit()
        response.set_cookie('buet_session', token, httponly=True, samesite='lax', secure=False, max_age=30*24*3600, path='/')
        return {'id': user.id, 'name': user.name, 'phone': user.phone}

@app.post('/api/auth/login')
def login(payload: LoginIn, response: Response):
    phone = normalize_bd_phone(payload.phone)
    with Session(engine) as db:
        user = db.scalar(select(User).where(User.phone == phone))
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(401, 'Phone number or password is incorrect')
        token = secrets.token_urlsafe(48)
        db.add(AuthSession(user_id=user.id, token_hash=session_token_hash(token), created_at=utc_now_naive(), expires_at=utc_now_naive()+timedelta(days=30)))
        db.commit()
        response.set_cookie('buet_session', token, httponly=True, samesite='lax', secure=False, max_age=30*24*3600, path='/')
        return {'id': user.id, 'name': user.name, 'phone': user.phone}

@app.post('/api/auth/logout')
def logout(response: Response, buet_session: str | None = Cookie(default=None)):
    with Session(engine) as db:
        if buet_session:
            row = db.scalar(select(AuthSession).where(AuthSession.token_hash == session_token_hash(buet_session)))
            if row: db.delete(row); db.commit()
    response.delete_cookie('buet_session', path='/')
    return {'ok': True}

@app.get('/api/auth/me')
def me(buet_session: str | None = Cookie(default=None)):
    with Session(engine) as db:
        user = current_user(db, buet_session)
        if not user: raise HTTPException(401, 'Not logged in')
        return {'id': user.id, 'name': user.name, 'phone': user.phone}

class ProfileUpdateIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)

@app.patch('/api/auth/profile')
def update_profile(payload: ProfileUpdateIn, buet_session: str | None = Cookie(default=None)):
    with Session(engine) as db:
        user = require_user(db, buet_session)
        clean = payload.name.strip()
        if not clean: raise HTTPException(400, 'Name cannot be empty')
        user.name = clean
        db.commit()
        return {'id': user.id, 'name': user.name, 'phone': user.phone}

class StartExamIn(BaseModel):
    student_name: str = Field(min_length=1, max_length=120)
    duration_minutes: int = Field(ge=1, le=600)
    subjects: list[dict]
class SaveAnswerIn(BaseModel):
    answer_text: str = Field(default="", max_length=50000)
    handwriting_data: str = Field(default="[]", max_length=2000000)
    answer_mode: str = Field(default="typing", pattern="^(typing|handwriting)$")
class DeleteImageIn(BaseModel): image_url: str

def ensure_writable(attempt: Attempt):
    if attempt.submitted:
        raise HTTPException(409, "Exam already submitted")
    now = utc_now_naive()
    ends_at = attempt.ends_at.replace(tzinfo=None) if attempt.ends_at else now
    if now >= ends_at:
        attempt.submitted = True
        attempt.submitted_at = ends_at
        raise HTTPException(410, "Exam time has expired")

def get_attempt(db, attempt_id):
    attempt=db.get(Attempt,attempt_id)
    if not attempt: raise HTTPException(404,"Attempt not found")
    return attempt

def get_user_attempt(db: Session, attempt_id: int, auth_token: str | None) -> Attempt:
    user = require_user(db, auth_token)
    attempt = get_attempt(db, attempt_id)
    if attempt.user_id is not None and attempt.user_id != user.id:
        raise HTTPException(403, 'You do not have access to this exam attempt')
    return attempt

def answer_payload(a: Answer):
    return {"text": a.answer_text, "images": json.loads(a.image_urls or "[]"), "handwriting": json.loads(a.handwriting_data or "[]"), "mode": a.answer_mode or "typing"}


# --------------------------- Question bank importer ---------------------------

def chapter_options_payload():
    out = {}
    for subject in ["Mathematics","Physics","Chemistry"]:
        out[subject] = []
        for paper_id, paper_name, prefix in PAPER_NAMES[subject]:
            out[subject].append({
                "paper_id": paper_id,
                "paper_name": paper_name,
                "chapters": [c for c in CHAPTERS[subject] if c["id"].startswith(prefix)]
            })
    return out

def chapter_reference_text(selected_ids, subject_hint):
    subjects = [subject_hint] if subject_hint in {"Mathematics","Physics","Chemistry"} else ["Mathematics","Physics","Chemistry"]
    lines = []
    for subject in subjects:
        for paper_id, paper_name, prefix in PAPER_NAMES[subject]:
            for c in CHAPTERS[subject]:
                if c["id"].startswith(prefix) and (not selected_ids or c["id"] in selected_ids):
                    lines.append(f"{subject} | {paper_id} | {c['id']} | {c['name']}")
    return "\n".join(lines)

@app.get('/api/admin/question-bank')
def question_bank_list(subject: Optional[str]=None, chapter_id: Optional[str]=None, difficulty: Optional[str]=None):
    with Session(engine) as db:
        qs=db.scalars(select(Question).where(Question.status=='published').order_by(Question.subject, Question.chapter_id, Question.number)).all()
        out=[]
        for q in qs:
            if subject and q.subject!=subject: continue
            if chapter_id and q.chapter_id!=chapter_id: continue
            if difficulty and q.topic!=difficulty and q.source_file is None: pass
            out.append({
                'id':q.id,'subject':q.subject,'paper_id':q.paper_id,'chapter_id':q.chapter_id,'number':q.number,
                'text':q.text,'marks':q.marks,'difficulty':q.difficulty,'source_file':q.source_file,'source_page':q.source_page,'source_exam':q.source_exam,'source_year':q.source_year,'source_session':q.source_session,
                'answer_text':q.answer_text,'solution_text':q.solution_text,'rubric':json.loads(q.rubric_json or '[]'),'original_language':q.original_language,'content_blocks':json.loads(q.content_json or '[]')
            })
        return {'questions':out, 'count':len(out)}

@app.get('/api/admin/question-bank/config')
def question_bank_config():
    with Session(engine) as db:
        published_count = len(db.scalars(select(Question).where(Question.status == 'published')).all())
        draft_count = len(db.scalars(select(DraftQuestion).where(DraftQuestion.status == 'review')).all())
    return {"subjects": ["Mathematics","Physics","Chemistry"], "chapters": chapter_options_payload(), "published_count": published_count, "draft_count": draft_count}

class AdminQuestionIn(BaseModel):
    subject: str
    paper_id: str
    chapter_id: str
    text: str = Field(min_length=1, max_length=50000)
    marks: int = Field(default=10, ge=1, le=100)
    answer_text: str = ''
    solution_text: str = ''
    difficulty: str = 'Medium-Hard'
    source_file: Optional[str] = None
    source_page: Optional[int] = None
    source_exam: Optional[str] = None
    source_year: Optional[str] = None
    source_session: Optional[str] = None
    original_language: str = 'source'
    content_blocks: list[dict] = []
    rubric: list[dict] = []

@app.post('/api/admin/question-bank/questions')
def create_question(payload: AdminQuestionIn):
    if payload.subject not in CHAPTERS:
        raise HTTPException(400, 'Invalid subject')
    valid_chapters = {c['id'] for c in CHAPTERS[payload.subject]}
    if payload.chapter_id not in valid_chapters:
        raise HTTPException(400, 'Invalid chapter for subject')
    valid_papers = {p[0] for p in PAPER_NAMES[payload.subject]}
    if payload.paper_id not in valid_papers:
        raise HTTPException(400, 'Invalid paper for subject')
    with Session(engine) as db:
        max_num = db.scalar(select(Question.number).where(Question.subject == payload.subject, Question.status == 'published').order_by(Question.number.desc()).limit(1)) or 0
        q = Question(subject=payload.subject, number=max_num+1, text=payload.text, marks=payload.marks,
            topic=payload.chapter_id, paper_id=payload.paper_id, chapter_id=payload.chapter_id,
            status='published', source_file=payload.source_file, source_page=payload.source_page, source_exam=payload.source_exam, source_year=payload.source_year, source_session=payload.source_session,
            answer_text=payload.answer_text, solution_text=payload.solution_text,
            difficulty=payload.difficulty, rubric_json=json.dumps(payload.rubric, ensure_ascii=False),
            content_json=json.dumps(payload.content_blocks, ensure_ascii=False), original_language=payload.original_language)
        db.add(q); db.commit(); db.refresh(q)
        return {'created': True, 'question_id': q.id}

@app.put('/api/admin/question-bank/questions/{question_id}')
def update_question(question_id: int, payload: AdminQuestionIn):
    with Session(engine) as db:
        q = db.get(Question, question_id)
        if not q: raise HTTPException(404, 'Question not found')
        q.subject=payload.subject; q.paper_id=payload.paper_id; q.chapter_id=payload.chapter_id; q.topic=payload.chapter_id
        q.text=payload.text; q.marks=payload.marks; q.answer_text=payload.answer_text; q.solution_text=payload.solution_text
        q.difficulty=payload.difficulty; q.source_file=payload.source_file; q.source_page=payload.source_page; q.source_exam=payload.source_exam; q.source_year=payload.source_year; q.source_session=payload.source_session
        q.rubric_json=json.dumps(payload.rubric, ensure_ascii=False); q.content_json=json.dumps(payload.content_blocks, ensure_ascii=False)
        q.original_language=payload.original_language
        db.commit(); return {'saved': True}

@app.delete('/api/admin/question-bank/questions/{question_id}')
def archive_question(question_id: int):
    with Session(engine) as db:
        q = db.get(Question, question_id)
        if not q: raise HTTPException(404, 'Question not found')
        q.status='archived'; db.commit(); return {'archived': True}

@app.post('/api/admin/question-bank/question-images')
async def upload_question_image(file: UploadFile = File(...)):
    ext=Path(file.filename or '').suffix.lower()
    if ext not in {'.png','.jpg','.jpeg','.webp'}:
        raise HTTPException(415, 'Only PNG, JPG, JPEG and WEBP are supported')
    data=await file.read()
    if len(data)>15*1024*1024: raise HTTPException(413,'Image is larger than 15 MB')
    safe=f"question_asset_{uuid.uuid4().hex}{ext}"; (UPLOAD_DIR/safe).write_bytes(data)
    return {'image_url': f'/uploads/{safe}'}

@app.post('/api/admin/question-bank/resources')
async def upload_resource(file: UploadFile = File(...)):
    ext = Path(file.filename or '').suffix.lower()
    if ext not in {'.pdf','.png','.jpg','.jpeg','.webp'}:
        raise HTTPException(415, 'Only PDF, PNG, JPG, JPEG and WEBP are supported')
    data = await file.read()
    if len(data) > 80 * 1024 * 1024:
        raise HTTPException(413, 'Resource is larger than 80 MB')
    safe = f"resource_{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / safe
    path.write_bytes(data)
    page_count = 1
    if ext == '.pdf':
        try:
            import fitz
            with fitz.open(path) as doc:
                page_count = max(1, len(doc))
        except Exception:
            page_count = 1
    with Session(engine) as db:
        r = ImportedResource(filename=file.filename or safe, stored_path=safe, content_type=file.content_type or '', uploaded_at=utc_now_naive(), page_count=page_count)
        db.add(r); db.commit(); db.refresh(r)
        return {"resource_id": r.id, "filename": r.filename, "page_count": r.page_count, "status": r.status}

class ProcessResourceIn(BaseModel):
    subject_hint: Optional[str] = None
    selected_chapter_ids: list[str] = []
    written_only: bool = True
    medium_hard_only: bool = True

class GenerateResourceIn(BaseModel):
    subject_hint: Optional[str] = None
    selected_chapter_ids: list[str] = []
    count: int = Field(default=10, ge=1, le=60)
    medium_hard_only: bool = True
    preserve_source_images: bool = False

AI_SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {"type": "array", "items": {"type": "object", "properties": {
            "question_text": {"type": "string"},
            "content_blocks": {"type": "array", "items": {"type": "object", "properties": {"type": {"type": "string"}, "content": {"type": "string"}, "bbox": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4}}, "required": ["type", "content", "bbox"], "additionalProperties": False}},
            "subject": {"type": "string"}, "paper_id": {"type": "string"}, "chapter_id": {"type": "string"},
            "difficulty": {"type": "string"}, "answer": {"type": "string"}, "solution": {"type": "string"},
            "rubric": {"type": "array", "items": {"type": "object", "properties": {"criterion": {"type": "string"}, "marks": {"type": "number"}}, "required": ["criterion", "marks"], "additionalProperties": False}},
            "bbox": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4}
        }, "required": ["question_text", "content_blocks", "subject", "paper_id", "chapter_id", "difficulty", "answer", "solution", "rubric", "bbox"], "additionalProperties": False}},
    },
    "required": ["questions"], "additionalProperties": False
}

def render_resource_pages(resource):
    path = UPLOAD_DIR / resource.stored_path
    if path.suffix.lower() == '.pdf':
        import fitz
        doc = fitz.open(path)
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False)
            yield i + 1, pix.tobytes('png')
        doc.close()
    else:
        yield 1, path.read_bytes()

def image_data_url(data):
    return 'data:image/png;base64,' + base64.b64encode(data).decode('ascii')

def ai_extract_page(image_bytes, chapters_text, subject_hint):
    try:
        from openai import OpenAI
    except ImportError as e:
        raise HTTPException(503, 'OpenAI SDK is missing. Run pip install -r requirements.txt') from e
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        raise HTTPException(503, 'OPENAI_API_KEY is not configured on the backend.')
    client = OpenAI(api_key=key)
    prompt = f'''You curate a Bangladesh engineering-admission written question bank. Extract individual WRITTEN/problem-solving questions from this page image. IGNORE ALL MCQs. Prefer unique medium-hard or hard written questions. Previous-year questions are allowed and valuable. Preserve essential diagrams, graphs, tables, geometry figures and chemical structures as image content blocks. Convert math to clean LaTeX. Do not invent missing source content. Assign an exact chapter_id from this list:\n{chapters_text}\nSubject hint: {subject_hint or 'auto-detect'}. A question may include text and image blocks in sequence. Return only questions suitable for a written exam.'''
    model = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')
    resp = client.responses.create(
        model=model,
        input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}, {"type": "input_image", "image_url": image_data_url(image_bytes)}]}],
        text={"format": {"type": "json_schema", "name": "question_page", "schema": AI_SCHEMA, "strict": True}}
    )
    raw = getattr(resp, 'output_text', '')
    try:
        return json.loads(raw).get('questions', [])
    except Exception as e:
        raise HTTPException(502, 'AI returned invalid structured output.') from e


GEN_AI_SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {"type": "array", "items": {"type": "object", "properties": {
            "question_text": {"type": "string"},
            "content_blocks": {"type": "array", "items": {"type": "object", "properties": {
                "type": {"type": "string"}, "content": {"type": "string"}
            }, "required": ["type", "content"], "additionalProperties": False}},
            "subject": {"type": "string"}, "paper_id": {"type": "string"}, "chapter_id": {"type": "string"},
            "difficulty": {"type": "string"}, "answer": {"type": "string"}, "solution": {"type": "string"},
            "rubric": {"type": "array", "items": {"type": "object", "properties": {
                "criterion": {"type": "string"}, "marks": {"type": "number"}
            }, "required": ["criterion", "marks"], "additionalProperties": False}},
            "estimated_minutes": {"type": "number"},
            "concepts": {"type": "array", "items": {"type": "string"}},
            "accepted_methods": {"type": "array", "items": {"type": "string"}}
        }, "required": ["question_text", "content_blocks", "subject", "paper_id", "chapter_id", "difficulty", "answer", "solution", "rubric", "estimated_minutes", "concepts", "accepted_methods"], "additionalProperties": False}}
    },
    "required": ["questions"], "additionalProperties": False
}

def ai_generate_from_page(image_bytes, chapters_text, subject_hint, how_many):
    try:
        from openai import OpenAI
    except ImportError as e:
        raise HTTPException(503, 'OpenAI SDK is missing. Run pip install -r requirements.txt') from e
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        raise HTTPException(503, 'OPENAI_API_KEY is not configured on the backend.')
    client = OpenAI(api_key=key)
    prompt = f"""You are a BUET-style written-exam question designer for Bangladesh engineering admissions.

Use the attached study/question-material page ONLY as inspiration for concepts, methods, difficulty, notation, and context. DO NOT copy or lightly paraphrase any existing question. Create {how_many} genuinely new, unique written questions.

Rules:
- Ignore MCQs entirely.
- Target medium-hard to hard written problems; prefer multi-step reasoning/calculation/proof/derivation.
- Previous-year style may be imitated, but the generated question must be new.
- Use clean canonical LaTeX for all mathematical/scientific notation.
- Prefer questions that can reasonably be answered in a written engineering-admission exam.
- Assign an exact chapter_id from the list below.
- Generate a final answer, detailed solution, a 10-mark rubric, estimated solving time, key concepts, and accepted alternative/shortcut methods.
- Generated questions should normally be text + LaTeX only. Do not require a new diagram unless the attached source already contains a diagram that can be meaningfully reused.
- Do not mention that the question was AI-generated.

Available chapters:
{chapters_text}
Subject hint: {subject_hint or 'auto-detect'}
"""
    model = os.getenv('OPENAI_GENERATION_MODEL', os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'))
    resp = client.responses.create(
        model=model,
        input=[{"role": "user", "content": [
            {"type": "input_text", "text": prompt},
            {"type": "input_image", "image_url": image_data_url(image_bytes)}
        ]}],
        text={"format": {"type": "json_schema", "name": "generated_question_page", "schema": GEN_AI_SCHEMA, "strict": True}}
    )
    try:
        return json.loads(getattr(resp, 'output_text', '')).get('questions', [])
    except Exception as e:
        raise HTTPException(502, 'AI returned invalid generated-question output.') from e

def materialize_question_images(page_bytes, blocks):
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(page_bytes)).convert('RGB')
        w, h = img.size
        out=[]
        for b in blocks or []:
            if b.get('type') != 'image':
                out.append(b); continue
            bbox=b.get('bbox') or [0,0,0,0]
            if len(bbox)!=4 or max(bbox) <= 0:
                out.append(b); continue
            x0=max(0,min(w,int(float(bbox[0])*w))); y0=max(0,min(h,int(float(bbox[1])*h)))
            x1=max(x0+1,min(w,int(float(bbox[2])*w))); y1=max(y0+1,min(h,int(float(bbox[3])*h)))
            crop=img.crop((x0,y0,x1,y1))
            name=f"question_image_{uuid.uuid4().hex}.png"; crop.save(UPLOAD_DIR/name, format='PNG')
            nb=dict(b); nb['content']=f'/uploads/{name}'; nb['alt']=b.get('content','Question image')
            out.append(nb)
        return out
    except Exception:
        return blocks or []


@app.post('/api/admin/question-bank/resources/{resource_id}/generate')
def generate_resource(resource_id:int, payload:GenerateResourceIn):
    with Session(engine) as db:
        resource = db.get(ImportedResource, resource_id)
        if not resource: raise HTTPException(404, 'Resource not found')
        pages = list(render_resource_pages(resource))
        if not pages:
            raise HTTPException(400, 'No readable pages found in the resource')
        chapters_text = chapter_reference_text(payload.selected_chapter_ids, payload.subject_hint)
        page_budget = min(len(pages), payload.count)
        pages = pages[:page_budget]
        per_page = max(1, (payload.count + len(pages) - 1) // len(pages))
        created=[]
        remaining=payload.count
        try:
            for page_number, page_bytes in pages:
                if remaining <= 0: break
                how_many=min(per_page, remaining)
                generated=ai_generate_from_page(page_bytes, chapters_text, payload.subject_hint, how_many)
                source_name=f"source_{uuid.uuid4().hex}.png"
                (UPLOAD_DIR / source_name).write_bytes(page_bytes)
                source_url=f"/uploads/{source_name}"
                for item in generated:
                    if remaining <= 0: break
                    difficulty=str(item.get('difficulty','Medium-Hard'))
                    if payload.medium_hard_only and difficulty.lower().startswith('easy'):
                        continue
                    draft=DraftQuestion(
                        resource_id=resource.id, page_number=page_number,
                        subject=item.get('subject') or payload.subject_hint or 'Mathematics',
                        paper_id=item.get('paper_id'), chapter_id=item.get('chapter_id'),
                        question_text=item.get('question_text',''),
                        content_json=json.dumps(item.get('content_blocks',[]), ensure_ascii=False),
                        answer_text=item.get('answer',''), solution_text=item.get('solution',''),
                        difficulty=difficulty, rubric_json=json.dumps({
                            'items': item.get('rubric',[]),
                            'estimated_minutes': item.get('estimated_minutes'),
                            'concepts': item.get('concepts',[]),
                            'accepted_methods': item.get('accepted_methods',[])
                        }, ensure_ascii=False),
                        source_image_url=source_url, bbox_json='[]', status='review', created_at=utc_now_naive()
                    )
                    db.add(draft); db.flush(); created.append(draft.id); remaining -= 1
            db.commit()
        except Exception:
            db.rollback()
            raise
        return {'resource_id': resource.id, 'draft_ids': created, 'draft_count': len(created), 'mode':'generated', 'status':'processed'}

@app.post('/api/admin/question-bank/resources/{resource_id}/process')
def process_resource(resource_id:int, payload:ProcessResourceIn):
    with Session(engine) as db:
        resource = db.get(ImportedResource, resource_id)
        if not resource: raise HTTPException(404, 'Resource not found')
        resource.status = 'processing'; db.commit()
        pages = list(render_resource_pages(resource))
        chapters_text = chapter_reference_text(payload.selected_chapter_ids, payload.subject_hint)
        created = []
        try:
            for page_number, page_bytes in pages:
                extracted = ai_extract_page(page_bytes, chapters_text, payload.subject_hint)
                source_name = f"source_{uuid.uuid4().hex}.png"
                (UPLOAD_DIR / source_name).write_bytes(page_bytes)
                source_url = f"/uploads/{source_name}"
                for item in extracted:
                    if payload.medium_hard_only and str(item.get('difficulty','')).lower().startswith('easy'):
                        continue
                    draft = DraftQuestion(resource_id=resource.id, page_number=page_number, subject=item.get('subject') or payload.subject_hint or 'Mathematics', paper_id=item.get('paper_id'), chapter_id=item.get('chapter_id'), question_text=item.get('question_text',''), content_json=json.dumps(materialize_question_images(page_bytes, item.get('content_blocks',[])), ensure_ascii=False), answer_text=item.get('answer',''), solution_text=item.get('solution',''), difficulty=item.get('difficulty','Medium'), rubric_json=json.dumps(item.get('rubric',[]), ensure_ascii=False), source_image_url=source_url, bbox_json=json.dumps(item.get('bbox',[])), status='review', created_at=utc_now_naive())
                    db.add(draft); db.flush(); created.append(draft.id)
            resource.status = 'processed'; db.commit()
        except Exception:
            resource.status = 'error'; db.commit()
            raise
        return {"resource_id": resource.id, "draft_ids": created, "draft_count": len(created), "status": resource.status}

@app.get('/api/admin/question-bank/drafts')
def list_drafts(status: str='review'):
    with Session(engine) as db:
        rows = db.scalars(select(DraftQuestion).where(DraftQuestion.status == status).order_by(DraftQuestion.created_at.desc())).all()
        return [{"id":r.id,"resource_id":r.resource_id,"page":r.page_number,"subject":r.subject,"paper_id":r.paper_id,"chapter_id":r.chapter_id,"question_text":r.question_text,"content_blocks":json.loads(r.content_json or '[]'),"answer":r.answer_text,"solution":r.solution_text,"difficulty":r.difficulty,"rubric":json.loads(r.rubric_json or '[]'),"source_image_url":r.source_image_url,"status":r.status} for r in rows]

class DraftUpdateIn(BaseModel):
    question_text: str
    subject: str
    paper_id: str
    chapter_id: str
    answer: str = ''
    solution: str = ''
    difficulty: str = 'Medium'
    rubric: list[dict] = []
    content_blocks: list[dict] = []

@app.put('/api/admin/question-bank/drafts/{draft_id}')
def update_draft(draft_id:int, payload:DraftUpdateIn):
    with Session(engine) as db:
        r = db.get(DraftQuestion, draft_id)
        if not r: raise HTTPException(404, 'Draft not found')
        r.question_text=payload.question_text; r.subject=payload.subject; r.paper_id=payload.paper_id; r.chapter_id=payload.chapter_id; r.answer_text=payload.answer; r.solution_text=payload.solution; r.difficulty=payload.difficulty; r.rubric_json=json.dumps(payload.rubric, ensure_ascii=False); r.content_json=json.dumps(payload.content_blocks, ensure_ascii=False); db.commit(); return {"saved": True}

@app.post('/api/admin/question-bank/drafts/{draft_id}/publish')
def publish_draft(draft_id:int):
    with Session(engine) as db:
        draft = db.get(DraftQuestion, draft_id)
        if not draft: raise HTTPException(404, 'Draft not found')
        current = db.scalars(select(Question).where(Question.subject == draft.subject, Question.status == 'published')).all()
        number = max([q.number for q in current] or [0]) + 1
        resource = db.get(ImportedResource, draft.resource_id)
        q = Question(subject=draft.subject, number=number, text=draft.question_text, marks=10, difficulty=draft.difficulty, topic=draft.chapter_id or '', paper_id=draft.paper_id, chapter_id=draft.chapter_id, status='published', source_file=resource.filename if resource else None, source_page=draft.page_number, source_image_url=None, answer_text=draft.answer_text, solution_text=draft.solution_text, rubric_json=draft.rubric_json, content_json=draft.content_json, original_language='source')
        db.add(q); draft.status='published'; db.commit(); db.refresh(q); return {"published": True, "question_id": q.id}

@app.delete('/api/admin/question-bank/drafts/{draft_id}')
def reject_draft(draft_id:int):
    with Session(engine) as db:
        r = db.get(DraftQuestion,draft_id)
        if not r: raise HTTPException(404,'Draft not found')
        r.status='rejected'; db.commit(); return {"rejected":True}

@app.get('/api/questions/catalog')
def catalog():
    with Session(engine) as db:
        qs=db.scalars(select(Question).where(Question.status == "published").order_by(Question.subject,Question.number)).all()
        counts={s:0 for s in ["Mathematics","Physics","Chemistry"]}
        for q in qs:
            if q.subject in counts: counts[q.subject]+=1
        papers={}
        for subject, defs in PAPER_NAMES.items():
            papers[subject]=[]
            for pid,name,prefix in defs:
                papers[subject].append({"id":pid,"name":name,"chapters":[c for c in CHAPTERS[subject] if c["id"].startswith(prefix)]})
        selected_counts={}
        for subject in counts:
            for sid in [x["id"] for x in CHAPTERS[subject]]:
                n=sum(1 for q in qs if q.subject==subject and chapter_id_for_question(subject,q.number,q.chapter_id)==sid)
                selected_counts[f"{subject}:{sid}"]=n
        return {"available_by_subject":counts,"question_bank_size":len(qs),"papers":papers,"chapter_question_counts":selected_counts}

@app.post('/api/exams/start')
def start_exam(payload: StartExamIn, buet_session: str | None = Cookie(default=None)):
    allowed = {"Mathematics", "Physics", "Chemistry"}
    wanted: dict[str, dict] = {}
    for item in payload.subjects:
        subject = str(item.get("subject", ""))
        try:
            count = int(item.get("count", 0))
        except (TypeError, ValueError):
            raise HTTPException(400, f"Invalid question count for {subject or 'subject'}")
        if subject not in allowed: raise HTTPException(400, f"Unsupported subject: {subject}")
        if count < 1 or count > 60: raise HTTPException(400, f"Question count for {subject} must be between 1 and 60")
        if subject in wanted: raise HTTPException(400, f"Duplicate subject: {subject}")
        chapter_ids = item.get("chapter_ids") or ["all"]
        if not isinstance(chapter_ids, list): raise HTTPException(400, "chapter_ids must be a list")
        valid={c["id"] for c in CHAPTERS[subject]}
        if "all" in chapter_ids: chapter_ids=["all"]
        elif not all(x in valid for x in chapter_ids): raise HTTPException(400, f"Invalid chapter selection for {subject}")
        if not chapter_ids: raise HTTPException(400, f"Select at least one chapter for {subject}")
        wanted[subject] = {"count":count,"chapter_ids":chapter_ids}

    total_requested=sum(x["count"] for x in wanted.values())
    if total_requested < 1: raise HTTPException(400, "Select at least one subject with at least 1 question")
    if total_requested > 60: raise HTTPException(400, f"An exam can contain at most 60 questions. You selected {total_requested}.")

    with Session(engine) as db:
        user = require_user(db, buet_session)
        all_qs = db.scalars(select(Question).where(Question.status == "published").order_by(Question.subject, Question.number)).all()
        selected=[]
        chosen_config=[]
        for subject in ["Mathematics","Physics","Chemistry"]:
            if subject not in wanted: continue
            spec=wanted[subject]
            pool=[q for q in all_qs if q.subject==subject and ("all" in spec["chapter_ids"] or chapter_id_for_question(subject,q.number,q.chapter_id) in spec["chapter_ids"])]
            if spec["count"]>len(pool): raise HTTPException(400, f"Not enough {subject} questions in the selected chapters. Available: {len(pool)}")
            # Balance each selected chapter as evenly as possible, then randomize
            # the order while interleaving chapters. For k selected chapters and n
            # requested questions, each chapter receives either floor(n/k) or
            # ceil(n/k) questions whenever the available question counts allow it.
            # If a chapter has fewer questions than its fair share, its deficit is
            # redistributed to the remaining chapters without exceeding capacity.
            buckets={}
            for q in pool:
                buckets.setdefault(chapter_id_for_question(subject,q.number,q.chapter_id), []).append(q)
            for bucket in buckets.values():
                random.shuffle(bucket)

            capacities = {chapter: len(items) for chapter, items in buckets.items() if items}
            remaining = spec["count"]
            allocations = {chapter: 0 for chapter in capacities}

            # Give every chapter the same baseline first. Recompute against
            # remaining capacity when a chapter cannot absorb the baseline.
            while remaining > 0:
                eligible = [c for c in allocations if allocations[c] < capacities[c]]
                if not eligible:
                    break
                min_alloc = min(allocations[c] for c in eligible)
                lowest = [c for c in eligible if allocations[c] == min_alloc]
                chapter = random.choice(lowest)
                allocations[chapter] += 1
                remaining -= 1

            if remaining:
                raise HTTPException(400, f"Not enough {subject} questions in the selected chapters. Available: {len(pool)}")

            # Pull the allocated number from each chapter, then repeatedly pick
            # among chapters that still have allocated questions. This preserves
            # subject grouping but avoids chapter blocks such as A,A,A,B,B,B.
            chapter_pools = {c: buckets[c][:allocations[c]] for c in allocations}
            picked=[]; last_chapter=None
            while len(picked) < spec["count"]:
                choices=[c for c,items in chapter_pools.items() if items and c != last_chapter]
                if not choices:
                    choices=[c for c,items in chapter_pools.items() if items]
                chapter=random.choice(choices)
                picked.append(chapter_pools[chapter].pop())
                last_chapter=chapter
            selected.extend(picked)
            chosen_config.append({"subject":subject,"count":spec["count"],"chapter_ids":spec["chapter_ids"],"question_ids":[q.id for q in picked]})

        now=utc_now_naive()
        attempt=Attempt(user_id=user.id,student_name=user.name,started_at=now,ends_at=now+timedelta(minutes=payload.duration_minutes),config_json=json.dumps(chosen_config,ensure_ascii=False))
        db.add(attempt); db.flush(); db.commit(); db.refresh(attempt)
        return {"attempt_id":attempt.id,"started_at":as_utc(attempt.started_at),"ends_at":as_utc(attempt.ends_at),"submitted":attempt.submitted,"questions":[attempt_question_payload(q,i) for i,q in enumerate(attempt_questions(db,attempt),1)]}

def attempt_questions(db: Session, attempt: Attempt):
    config=json.loads(attempt.config_json or '[]')
    by_id={q.id:q for q in db.scalars(select(Question).where(Question.status == 'published')).all()}
    selected=[]
    for spec in config:
        ids=spec.get('question_ids') or []
        if ids:
            selected.extend([by_id[i] for i in ids if i in by_id])
        else:
            subject=spec['subject']; chapter_ids=spec.get('chapter_ids',['all']); n=int(spec['count'])
            pool=[q for q in by_id.values() if q.subject==subject and ('all' in chapter_ids or chapter_id_for_question(subject,q.number,q.chapter_id) in chapter_ids)]
            selected.extend(pool[:n])
    return selected

def attempt_question_payload(q, i):
    return {"id":q.id,"number":i,"subject":q.subject,"text":q.text,"marks":q.marks,"topic":q.topic,"chapter_id":chapter_id_for_question(q.subject,q.number,q.chapter_id),"paper_id":q.paper_id,"source_exam":q.source_exam,"source_year":q.source_year,"source_session":q.source_session,"source_file":q.source_file,"source_page":q.source_page,"content_blocks":json.loads(q.content_json or '[]')}

@app.get('/api/attempts/{attempt_id}')
def get_attempt_api(attempt_id:int, buet_session: str | None = Cookie(default=None)):
    with Session(engine) as db:
        attempt=get_user_attempt(db,attempt_id,buet_session)
        if not attempt.submitted:
            try: ensure_writable(attempt)
            except HTTPException as e:
                db.commit(); raise e
        answers=db.scalars(select(Answer).where(Answer.attempt_id==attempt_id)).all()
        return {"attempt_id":attempt.id,"student_name":attempt.student_name,"started_at":as_utc(attempt.started_at),"ends_at":as_utc(attempt.ends_at),"submitted":attempt.submitted,"questions":[attempt_question_payload(q,i) for i,q in enumerate(attempt_questions(db,attempt),1)],"answers":{str(a.question_id):answer_payload(a) for a in answers}}

@app.put('/api/attempts/{attempt_id}/answers/{question_id}')
def save_answer(attempt_id:int,question_id:int,payload:SaveAnswerIn, buet_session: str | None = Cookie(default=None)):
    with Session(engine) as db:
        attempt=get_user_attempt(db,attempt_id,buet_session); ensure_writable(attempt)
        q=db.get(Question,question_id)
        if not q: raise HTTPException(404,'Question not found')
        a=db.scalar(select(Answer).where(Answer.attempt_id==attempt_id,Answer.question_id==question_id))
        now=utc_now_naive()
        if a:
            a.answer_text=payload.answer_text
            a.handwriting_data=payload.handwriting_data
            a.answer_mode=payload.answer_mode
            a.updated_at=now
        else:
            db.add(Answer(attempt_id=attempt_id,question_id=question_id,answer_text=payload.answer_text,handwriting_data=payload.handwriting_data,answer_mode=payload.answer_mode,image_urls='[]',updated_at=now))
        db.commit(); return {"saved":True,"saved_at":now}

@app.post('/api/attempts/{attempt_id}/answers/{question_id}/images')
async def upload_image(attempt_id:int,question_id:int,file:UploadFile=File(...), buet_session: str | None = Cookie(default=None)):
    with Session(engine) as db:
        attempt=get_user_attempt(db,attempt_id,buet_session); ensure_writable(attempt)
        q=db.get(Question,question_id)
        if not q: raise HTTPException(404,'Question not found')
        if not (file.content_type or '').startswith('image/'): raise HTTPException(415,'Only image files are allowed')
        ext=Path(file.filename or '').suffix.lower() or '.png'
        filename=f"{uuid.uuid4().hex}{ext}"; path=UPLOAD_DIR/filename
        data=await file.read()
        if len(data)>10*1024*1024: raise HTTPException(413,'Image is larger than 10 MB')
        path.write_bytes(data)
        a=db.scalar(select(Answer).where(Answer.attempt_id==attempt_id,Answer.question_id==question_id))
        now=utc_now_naive(); url=f"/uploads/{filename}"
        if not a:
            a=Answer(attempt_id=attempt_id,question_id=question_id,answer_text='',handwriting_data='[]',answer_mode='typing',image_urls=json.dumps([url]),updated_at=now); db.add(a)
        else:
            imgs=json.loads(a.image_urls or '[]'); imgs.append(url); a.image_urls=json.dumps(imgs); a.updated_at=now
        db.commit(); return {"image_url":url}

@app.delete('/api/attempts/{attempt_id}/answers/{question_id}/images')
def delete_image(attempt_id:int,question_id:int,payload:DeleteImageIn, buet_session: str | None = Cookie(default=None)):
    with Session(engine) as db:
        attempt=get_user_attempt(db,attempt_id,buet_session); ensure_writable(attempt)
        a=db.scalar(select(Answer).where(Answer.attempt_id==attempt_id,Answer.question_id==question_id))
        if a:
            imgs=[x for x in json.loads(a.image_urls or '[]') if x!=payload.image_url]; a.image_urls=json.dumps(imgs); db.commit()
        try:
            Path(payload.image_url.lstrip('/')).unlink(missing_ok=True)
        except Exception: pass
        return {"deleted":True}

@app.get('/api/problems')
def list_problems(buet_session: str | None = Cookie(default=None)):
    with Session(engine) as db:
        user=require_user(db, buet_session)
        rows=db.execute(select(Problem, Question).join(Question, Question.id==Problem.question_id).where(Problem.user_id==user.id).order_by(Problem.created_at.desc())).all()
        return [{"id":p.id,"question_id":q.id,"subject":q.subject,"number":q.number,"text":q.text,"marks":q.marks,"paper_id":q.paper_id,"chapter_id":chapter_id_for_question(q.subject,q.number,q.chapter_id),"source_exam":q.source_exam,"source_year":q.source_year,"source_session":q.source_session,"source_file":q.source_file,"source_page":q.source_page,"content_blocks":json.loads(q.content_json or '[]'),"answer_text":q.answer_text,"solution_text":q.solution_text,"created_at":as_utc(p.created_at)} for p,q in rows]

@app.post('/api/problems/{question_id}')
def add_problem(question_id:int, buet_session: str | None = Cookie(default=None)):
    with Session(engine) as db:
        user=require_user(db, buet_session)
        q=db.get(Question,question_id)
        if not q or q.status!='published': raise HTTPException(404,'Question not found')
        existing=db.scalar(select(Problem).where(Problem.user_id==user.id,Problem.question_id==question_id))
        if not existing:
            db.add(Problem(user_id=user.id,question_id=question_id,created_at=utc_now_naive())); db.commit()
        return {"saved":True}

@app.delete('/api/problems/{question_id}')
def remove_problem(question_id:int, buet_session: str | None = Cookie(default=None)):
    with Session(engine) as db:
        user=require_user(db, buet_session)
        row=db.scalar(select(Problem).where(Problem.user_id==user.id,Problem.question_id==question_id))
        if row: db.delete(row); db.commit()
        return {"saved":False}

@app.post('/api/attempts/{attempt_id}/submit')
def submit(attempt_id:int, buet_session: str | None = Cookie(default=None)):
    with Session(engine) as db:
        attempt=get_user_attempt(db,attempt_id,buet_session)
        if attempt.submitted:return {"submitted":True,"submitted_at":attempt.submitted_at}
        now=utc_now_naive(); ends_at=attempt.ends_at.replace(tzinfo=None); attempt.submitted=True; attempt.submitted_at=min(now, ends_at); db.commit(); return {"submitted":True,"submitted_at":as_utc(attempt.submitted_at)}

@app.get('/api/attempts/{attempt_id}/result')
def result(attempt_id:int, buet_session: str | None = Cookie(default=None)):
    with Session(engine) as db:
        attempt=get_user_attempt(db,attempt_id,buet_session)
        if not attempt.submitted: raise HTTPException(409,'Exam has not been submitted')
        answers=db.scalars(select(Answer).where(Answer.attempt_id==attempt_id)).all(); by={a.question_id:a for a in answers}
        # Use the exact question IDs saved when the attempt was created so randomized
        # exams remain identical in resume/result views.
        selected=attempt_questions(db, attempt)
        max_total=sum(q.marks for q in selected)
        return {"attempt_id":attempt.id,"student_name":attempt.student_name,"total_score":None,"max_score":max_total,"grading_status":"awaiting_ai_grading","questions":[{
            "number":i+1, "question_id":q.id, "subject":q.subject, "paper_id":q.paper_id,
            "chapter_id":chapter_id_for_question(q.subject,q.number,q.chapter_id), "max_score":q.marks,
            "question_text":q.text,
            "reference_answer":q.answer_text, "reference_solution":q.solution_text,
            "content_blocks":json.loads(q.content_json or "[]"),
            "student_answer":(by[q.id].answer_text if q.id in by else ""),
            "student_handwriting":(json.loads(by[q.id].handwriting_data or "[]") if q.id in by else []),
            "answer_mode":(by[q.id].answer_mode if q.id in by else "typing"),
            "student_images":(json.loads(by[q.id].image_urls or "[]") if q.id in by else [])
        } for i,q in enumerate(selected)]}
