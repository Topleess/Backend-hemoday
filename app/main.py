import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse
from tortoise.contrib.fastapi import RegisterTortoise

from app.api.v1.router import router as api_v1_router
from app.core.config import TORTOISE_ORM

from app.models.user import User
from app.models.family import Family
from app.models.transfusion import Transfusion

from app.core.mail import send_reset_email
from app.models.password_reset import PasswordResetToken
from passlib.hash import bcrypt 
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="app/templates")
security = HTTPBasic()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with RegisterTortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=False,
        add_exception_handlers=True,
    ):
        yield

app = FastAPI(
    title="HemoDay API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)

# --- ФУНКЦИЯ ПРОВЕРКИ ПАРОЛЯ ---
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
# -------------------------------

# ==========================================
# 👇 АДМИНКА ОТКЛЮЧЕНА (Закомментирована)
# ==========================================

# @app.get("/custom-admin", include_in_schema=False, dependencies=[Depends(get_current_username)])
# async def admin_dashboard(request: Request):
#     families = await Family.all().prefetch_related("users").order_by("-created_at")
#     return templates.TemplateResponse(
#         request=request, 
#         name="admin_users.html", 
#         context={"families": families}
#     )

# @app.get("/custom-admin/family/{family_id}", include_in_schema=False, dependencies=[Depends(get_current_username)])
# async def admin_family_detail(request: Request, family_id: str):
#     family = await Family.get(id=family_id).prefetch_related("users", "transfusions")
#     return templates.TemplateResponse(
#         request=request, 
#         name="admin_family_detail.html", 
#         context={"family": family}
#     )

# @app.post("/custom-admin/family/update/{family_id}", include_in_schema=False, dependencies=[Depends(get_current_username)])
# async def update_family(family_id: str, patient_name: str = Form(...), weight: float = Form(...)):
#     family = await Family.get(id=family_id)
#     family.patient_name = patient_name
#     family.patient_current_weight = weight
#     await family.save()
#     return RedirectResponse(url=f"/custom-admin/family/{family_id}", status_code=303)

# @app.get("/custom-admin/transfusion/delete/{t_id}", include_in_schema=False, dependencies=[Depends(get_current_username)])
# async def delete_transfusion(request: Request, t_id: str):
#     transfusion = await Transfusion.get(id=t_id)
#     family_id = transfusion.family_id 
#     await transfusion.delete()
#     return RedirectResponse(url=f"/custom-admin/family/{family_id}", status_code=303)

# ==========================================

@app.get("/")
async def root():
    return {"status": "ok", "service": "HemoDay API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# --- ЭНДПОИНТЫ ДЛЯ СБРОСА ПАРОЛЯ (ОСТАВЛЯЕМ РАБОЧИМИ) ---

@app.post("/api/v1/auth/forgot-password")
async def forgot_password(email: str):
    user = await User.get_or_none(email=email)
    if not user:
        return {"message": "Если такой email есть, мы отправили письмо."}

    reset_token = await PasswordResetToken.create_token(user_id=user.id)
    
    try:
        await send_reset_email(email_to=user.email, token=reset_token.token)
    except Exception as e:
        print(f"Ошибка отправки почты: {e}")
        return {"error": "Не удалось отправить письмо"}

    return {"message": "Письмо отправлено"}

@app.get("/reset-password-page", response_class=HTMLResponse, include_in_schema=False)
async def reset_password_page(request: Request, token: str):
    reset_token = await PasswordResetToken.get_or_none(token=token, used=False)
    
    if not reset_token or reset_token.is_expired():
        return HTMLResponse(content="<h1>Ошибка</h1><p>Ссылка устарела или неверна.</p>", status_code=400)

    return templates.TemplateResponse(
        request=request, 
        name="reset_password.html", 
        context={"token": token}
    )

@app.post("/reset-password-action", include_in_schema=False)
async def reset_password_action(token: str = Form(...), password: str = Form(...)):
    reset_token = await PasswordResetToken.get_or_none(token=token, used=False).prefetch_related("user")
    
    if not reset_token or reset_token.is_expired():
        return HTMLResponse(content="<h1>Ошибка</h1><p>Ссылка устарела.</p>", status_code=400)

    user = reset_token.user
    user.password_hash = bcrypt.hash(password)
    await user.save()

    reset_token.used = True
    await reset_token.save()

    return HTMLResponse(content="<h1>Успешно!</h1><p>Пароль изменен. Теперь вы можете войти в приложение.</p>")