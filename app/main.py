import secrets
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from tortoise.contrib.fastapi import register_tortoise

from app.api.v1.router import router as api_v1_router
# Импортируем TORTOISE_ORM, в котором уже зашит URL базы
from app.core.config import TORTOISE_ORM

# Импорты моделей (теперь они подхватятся автоматически через папку, 
# но оставляем для использования в коде ниже)
from app.models.user import User
from app.models.family import Family
from app.models.transfusion import Transfusion
from app.models.password_reset import PasswordResetToken
from app.models.analysis_template import AnalysisTemplate

from app.core.mail import send_reset_email
from passlib.hash import bcrypt 

templates = Jinja2Templates(directory="app/templates")
security = HTTPBasic()

app = FastAPI(
    title="HemoDay API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(f"422 Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

# --- ФУНКЦИЯ ПРОВЕРКИ ПАРОЛЯ ДЛЯ АДМИНКИ ---
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

# --- КАСТОМНЫЙ SWAGGER С МЕТРИКОЙ ---
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_ui_template_str=f"""
        <html>
        <head>
        <script type="text/javascript">
           (function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
           m[i].l=1*new Date();
           for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
           k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
           }})(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=106264847', 'ym');
           ym(106264847, 'init', {{ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", accurateTrackBounce:true, trackLinks:true}});
        </script>
        </head>
        <body>
        <div id="swagger-ui"></div>
        </body>
        </html>
        """
    )

@app.get("/")
async def root():
    return {"status": "ok", "service": "HemoDay API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# --- СБРОС ПАРОЛЯ ---

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
        return templates.TemplateResponse(
            request=request,
            name="reset_password_error.html",
            context={"error_message": "Ссылка устарела или неверна."},
            status_code=400
        )

    return templates.TemplateResponse(
        request=request, 
        name="reset_password.html", 
        context={"token": token}
    )

@app.post("/reset-password-action", include_in_schema=False)
async def reset_password_action(request: Request, token: str = Form(...), password: str = Form(...)):
    reset_token = await PasswordResetToken.get_or_none(token=token, used=False).prefetch_related("user")
    
    if not reset_token or reset_token.is_expired():
        return templates.TemplateResponse(
            request=request,
            name="reset_password_error.html",
            context={"error_message": "Ссылка устарела."},
            status_code=400
        )

    user = reset_token.user
    user.password_hash = bcrypt.hash(password)
    await user.save()

    reset_token.used = True
    await reset_token.save()

    return templates.TemplateResponse(
        request=request,
        name="reset_password_success.html"
    )

# --- РЕГИСТРАЦИЯ TORTOISE ---
# Используем TORTOISE_ORM напрямую, чтобы не путаться в именах переменных
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,
    add_exception_handlers=True,
)
