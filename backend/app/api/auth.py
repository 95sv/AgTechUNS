from fastapi import APIRouter, HTTPException, status
from app.api.deps import DB, hash_password, verify_password, create_access_token
from app.repositories.relational import get_usuario, create_usuario
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserInfo

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DB):
    user = await get_usuario(db, body.email)
    if not user or not verify_password(body.password, user.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    token = create_access_token({"sub": user.email_usuario})
    return TokenResponse(access_token=token)


@router.post("/register", response_model=UserInfo, status_code=201)
async def register(body: RegisterRequest, db: DB):
    existing = await get_usuario(db, body.email)
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = await create_usuario(db, body.email, body.nombre, hash_password(body.password), body.telefono)
    return user


@router.get("/me", response_model=UserInfo)
async def me(db: DB, current_user=None):
    from app.api.deps import get_current_user, oauth2_scheme
    return current_user
