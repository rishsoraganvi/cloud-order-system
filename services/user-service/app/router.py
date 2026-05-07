from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import schemas, service
from starlette.status import HTTP_201_CREATED

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_db(request: Request) -> Session:
    SessionLocal = request.app.state.SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", status_code=HTTP_201_CREATED, response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    existing = request.app.state.SessionLocal().query  # quick check to ensure DB present
    created = service.create_user(db, user.email, user.password)
    return created


@router.post("/login")
def login(payload: schemas.UserLogin, request: Request, db: Session = Depends(get_db)):
    user = service.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = service.create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), request: Request = None, db: Session = Depends(get_db)):
    from jose import JWTError, jwt
    from .service import JWT_SECRET, JWT_ALGO

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/me", response_model=schemas.UserResponse)
def me(current_user=Depends(get_current_user)):
    return current_user
