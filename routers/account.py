from fastapi import Request, Depends, Response, Form
from typing import Optional, List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse
from fastapi import APIRouter
import schemas
import crud
import function
from database import SessionLocal
from sqlalchemy.orm import Session
from datetime import date




router = APIRouter()


# 為能前後端分離, 將前端介面存在templates資料夾裡供使用, jinja2是知名樣板(template)處理器
templates = Jinja2Templates(directory="templates")


def get_db():  # 給予資料庫session啟用
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @router.get("/signup", response_class=HTMLResponse, tags=['account'])
# async def signup_page(
#     request: Request
# ):
#     return templates.TemplateResponse("account/signup.html", {"request": request})


# @router.post("/signup", tags=["account"])
# async def signup(
#     account=Depends(schemas.AccountCreate.as_form),
#     db: Session = Depends(get_db)
# ):
#     crud.create_account(db, account)
#     return RedirectResponse("/login", status_code=303)

# 創建醫師帳號並寄驗證信


@router.post("/createAccount", tags=["account"])
async def create_account(
    UserName: List[str] = Form(),
    Email: List[str] = Form(),
    Job: str = Form(),
    db: Session = Depends(get_db)
):
    for i in Email:
        if crud.check_if_email_repeat(db, i):
            return RedirectResponse("/accountManage?emailrepeat=1", status_code=303)

    crud.create_account(db, UserName, Email, Job)

    conf = ConnectionConfig(
        MAIL_USERNAME="admin@standup.tw",
        MAIL_PASSWORD="StandupAdminFJCU",
        MAIL_FROM="admin@standup.tw",
        MAIL_PORT=587,
        MAIL_SERVER="mail.gandi.net",
        MAIL_FROM_NAME="FJCU Hospital IT department",  # 神秘原因無法以中文寄出
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )

    account_data = crud.get_account_name_and_password_and_random_url(
        db, Email[0])
    account_name = account_data.AccountName
    account_password = account_data.Password
    random_url = account_data.RandomURL

    if Job == "doctor":
        job_name = "醫師"
    elif Job == "clerk":
        job_name = "醫院行政"

    html = """<p>親愛的"""+job_name+"""您好，目前您的系統帳號已建置待驗證開通，</p>
    <p>請務必於於<strong>3日內驗證並重新設定密碼</strong>，否則基於資安因素，系統會自動屏蔽帳號。</p>
     <h4>您的固定帳號為「"""+account_name+"」 預設密碼為「"+account_password+"""」</h4><p>請透過連結 <strong><a href="https://standup.tw/verifyAccount/"""+random_url+"""">https://standup.tw/verifyAccount/"""+random_url+"""
    </a></strong> 驗證並正式啟用帳號。</p><p>謝謝您的配合，祝一切順心！</p>"""

    email_list = schemas.EmailSchema(email=Email)

    message = MessageSchema(subject="輔大醫院-肌無力症病歷管理系統帳號驗證",
                            recipients=email_list.dict().get("email"),
                            body=html,
                            subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)

    return RedirectResponse("/accountManage?success=1", status_code=303)


@router.get("/verifyAccount/{random_url}", response_class=HTMLResponse, tags=['account'])
async def verify_account_page(
    request: Request,
    random_url: str,
    notsame: Optional[int] = None,
    db: Session = Depends(get_db)
):
    account = crud.get_account_by_random_url(db, random_url)

    if not account:
        return HTMLResponse(status_code=404)

    if account.UserRole == "uncheck" and function.verify_time(account.CreateTime):            
        return templates.TemplateResponse("/account/verifyAccount.html", {"request": request, "account": account, "notsame": notsame})
    else:
        return HTMLResponse(status_code=404)


@router.post("/verifyAccount/{random_url}", tags=['account'])
async def verify_account(
    random_url: str,
    DefaultPassword: str = Form(),
    PasswordAgain: str = Form(),
    account_verify_update: schemas.AccountUpdateFromVerify = Depends(schemas.AccountUpdateFromVerify.as_form),
    db: Session = Depends(get_db)
):
    account = crud.get_account_by_name(db, account_verify_update.AccountName)

    if account.Password == DefaultPassword:
        if PasswordAgain == account_verify_update.Password:
          

            account_verify_update.Password = function.get_password_hash(account_verify_update.Password)

            crud.update_account_from_verify(db, account_verify_update)
            
            return RedirectResponse("/login?verify=1", status_code=303)
        else:
            url = "/verifyAccount/"+random_url+"?notsame=1"
            return RedirectResponse(url, status_code=303)
    else:
        return HTMLResponse(status_code=403)



@router.get("/accountManage", response_class=HTMLResponse, tags=['account'])
async def account_manage(
    request: Request,
    db: Session = Depends(get_db),
    fromUpdate: Optional[str] = None,
    success: Optional[str] = None,
    emailrepeat: Optional[str] = None,
):
    # session_now = request.session.get("user_role", None)
    session_now = "clerk"
    if session_now in ['clerk']:
        if not fromUpdate:
            account = crud.get_all_account(db)

            for i in account:
                if not function.verify_time(i.CreateTime) and i.UserRole == "uncheck":
                    crud.delete_account(db, i.PK_AccountID)

            return templates.TemplateResponse("account/accountManage.html", {"request": request, "account": account, "accountCreateNotify": success, "emailrepeat": emailrepeat, "from_update": fromUpdate})
    else:
        return HTMLResponse(status_code=403)
    # if user_role := crud.get_account_user_role_that_match_login_data(db, login_data):
    #     request.session["user_role"] = user_role.UserRole
    #     return RedirectResponse("/control", status_code=303)
    # else:
    #     return RedirectResponse("/login", status_code=303) #可以從post導向get, 參考自https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#redirection_messages


@router.get("/jobName", tags=['account'])
async def other_job_name(
    request: Request,
    Job: str
):
    return templates.TemplateResponse("account/otherJobName.html", {"request": request, "other_job": Job})


@router.get("/jobNameModify", tags=['account'])
async def other_job_name_modify(
    request: Request,
    Job: str,
    PK_AccountID: str,
    db: Session = Depends(get_db)
):
    if Job != 'doctor' and Job != 'nurse':
        account = crud.get_account_by_id(db, PK_AccountID)
        return templates.TemplateResponse("account/otherJobNameModify.html", {"request": request, "other_job": Job, "account": account})
    else:
        return templates.TemplateResponse("account/none.html", {"request": request})


@router.get("/accountEdit/{account_id}", tags=['account'])
async def account_edit(
    request: Request,
    account_id: int,
    db: Session = Depends(get_db)
):
    account = crud.get_account_by_id(db, account_id)
    return templates.TemplateResponse("account/editOneAccount.html", {"request": request, "account": account})


@router.put("/updateAccount", tags=['account'])
async def account_edit(
    account=Depends(schemas.AccountUpdate.as_form),
    # UserRole = Form(),
    db: Session = Depends(get_db)
):
    crud.update_account(db, account)
    return RedirectResponse("/accountManage?fromUpdate=2", status_code=303)


@router.get("/deleteAccount/{account_id}", tags=['account'])
async def account_delte(
    account_id: str,
    db: Session = Depends(get_db)
):
    crud.delete_account(db, account_id)
    return RedirectResponse("/accountManage?fromUpdate=1")

# @router.get("/control", response_class=HTMLResponse, tags=["control"])
# async def control_page(
#   request: Request,

# ):
#     if request.session.get("user_role", None) == "admin":
#         return templates.TemplateResponse("control.html", {"request": request})
#     else:
#         return HTMLResponse(status_code=403)

# @router.get("/logout", response_class=HTMLResponse, tags=["control"])
# async def control_page(
#   request: Request,

# ):
#     if request.session.get("user_role", None) == "admin":
#         request.session["user_role"] = None
#         return RedirectResponse("/login")
#     else:
#         return HTMLResponse(status_code=403)

# @router.get("/manage", response_class=HTMLResponse, tags=["control"])
# async def manage_page(
#     request: Request,
#     db: Session = Depends(get_db)
# ):
#     if request.session.get("user_role", None) == "admin":
#         today = date.today()
#         manage = crud.get_patient_and_his_visit_for_manage_page(db)
#         patients_age = []
#         for i in manage:
#             patients_age.append(function.calculate_age(i[0].PatientBirth, today))

#         return templates.TemplateResponse("manage.html", {"request": request, "manage": zip(manage, patients_age)})
#     else:
#         return HTMLResponse(status_code=403)
