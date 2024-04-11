from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from database import SessionLocal
import schemas, crud, function

router = APIRouter()

templates = Jinja2Templates(directory="./templates") # 為能前後端分離, 將前端介面存在templates資料夾裡供使用, jinja2是知名樣板(template)處理器

def get_db(): #給予資料庫session啟用
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#登入介面
@router.get("/login", response_class=HTMLResponse, tags=['control'])
async def login_page(
    request: Request,
    wrong: Optional[int] = None, #若錯誤回傳訊息
    verify: Optional[int] = None, #驗證成功與否
):
    return templates.TemplateResponse("login.html", {"request": request, "wrong": wrong, "verify": verify}) 

#登入後端驗證
@router.post("/login" ,tags=["control"])
async def login_check(
    request: Request,
    login_data: schemas.LoginCheck = Depends(schemas.LoginCheck.as_form),
    db: Session = Depends(get_db)
):
    try:
        if function.verify_password(login_data.Password, crud.get_account_hashed_password(db, login_data.AccountName).Password):
            if account_session := crud.get_account_id_and_user_role_that_match_login_data(db, login_data):
                request.session["user_role"] = account_session.UserRole
                request.session["account_id"] = account_session.PK_AccountID
                return RedirectResponse("/control", status_code=303)
        else:
            return RedirectResponse("/login?wrong=1", status_code=303) 
    except:
        return RedirectResponse("/login?wrong=1", status_code=303) #可以從post導向get, 參考自https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#redirection_messages


#登入後首頁(控制頁面, 連結各功能)
@router.get("/control", response_class=HTMLResponse, tags=["control"]) 
async def control_page(
  request: Request, 

):
    session_now = request.session.get("user_role", None)
    if session_now in ['clerk', 'doctor']:
        return templates.TemplateResponse("control.html", {"request": request, "session_now": session_now }) 
    else:
        return HTMLResponse(status_code=403)

#登出轉址
@router.get("/logout", response_class=HTMLResponse, tags=["control"]) 
async def logout(
  request: Request, 
):
    session_now = request.session.get("user_role", None)
    if session_now in ['clerk', 'doctor']:
        request.session["user_role"] = None
        return RedirectResponse("/login")
    else:
        return HTMLResponse(status_code=403)
       
@router.get("/manage", response_class=HTMLResponse, tags=["control"])
async def manage_page(
    request: Request, 
    db: Session = Depends(get_db)
):
    session_now = request.session.get("user_role", None)
    if session_now in ['doctor']:
        account_id = request.session['account_id']
        today = date.today()
        manage = crud.get_patient_and_his_visit_for_manage_page(db, request.session['account_id'])
        patients_age = []
        patient_alert = []
        for i in manage:
            i[0].PatientName = function.decrypt_data(i[0].PatientName, crud.get_patient_key(db, i[0].PK_PatientID))
            patients_age.append(function.calculate_age(i[0].PatientBirth, today))
            if crud.get_alert_if_exist(db, i[0].PK_PatientID, account_id):
                patient_alert.append(1)
            else:
                patient_alert.append(0)
        return templates.TemplateResponse("manage.html", {"request": request, "manage": zip(manage, patients_age, patient_alert), "account_id": account_id})
    else:
        return HTMLResponse(status_code=403)

       
@router.get("/activity", response_class=HTMLResponse, tags=["control"])
async def activity_page(
    request: Request, 
    db: Session = Depends(get_db)
):
    session_now = request.session.get("user_role", None)
    if session_now in ['clerk']:
        account_id = request.session['account_id']
        today = date.today()
        activity = crud.get_all_activity(db)
        return templates.TemplateResponse("/activityRecord/activity.html", {"request": request, "activity": activity})
    else:
        return HTMLResponse(status_code=403)

@router.get("/watchReasonFromControl_{active_record_id}")
async def watch_reason(
    request: Request,
    active_record_id: int,
    db: Session = Depends(get_db)
):
    session_now = request.session.get("user_role", None)
    if session_now in ['clerk']:
        reason = crud.get_activity_reason_by_id(db, active_record_id)
        return templates.TemplateResponse("/activityRecord/oneRecordReason.html", {"request": request, "reason": reason})
    else:
        return HTMLResponse(status_code=403)
    
# @router.get("/patientControl/{patient_id}")
# async def control_patient(
#     request: Request,
#     patient_id: str,
#     db: Session = Depends(get_db)
# ):
    
#     return templates.TemplateResponse("/patientControl/patientControlBefroeVisit.html", {"request": request})
