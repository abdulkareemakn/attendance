from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from starlette.requests import Request

from app.db.connection import get_db
from app.db.models import User
from app.schemas.token import Token
from app.security import create_access_token, oauth
from app.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token["userinfo"]

    if not userinfo.get("email_verified"):
        raise HTTPException(status_code=400, detail="Google account email not verified")

    email: str = userinfo["email"]

    if not email.endswith("@cuilahore.edu.pk"):
        raise HTTPException(
            status_code=403, detail="Access restricted to CUI Lahore accounts"
        )

    user = db.exec(select(User).where(User.email == email)).first()
    if not user:
        user = User(email=email, full_name=userinfo.get("name", ""))
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return Token(access_token=access_token, token_type="bearer")
