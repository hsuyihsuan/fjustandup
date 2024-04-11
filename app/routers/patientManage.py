from fastapi import Request, Depends, HTTPException, Header, Form
from fastapi.responses import HTMLResponse
from database import SessionLocal
from typing import Optional, List
import crud
import function
import schemas
import random
from sqlalchemy.orm import Session
from datetime import date
from fastapi.responses import RedirectResponse
from fastapi import APIRouter

from fastapi.templating import Jinja2Templates


# 為能前後端分離, 將前端介面存在templates資料夾裡供使用, jinja2是知名樣板(template)處理器
templates = Jinja2Templates(directory="templates")

router = APIRouter()


def get_db():  # 給予資料庫session啟用
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/patientManage", response_class=HTMLResponse, tags=["patientManage"])
async def manage_page(
    request: Request, 
    create: Optional[str] = None,
    db: Session = Depends(get_db)
):
    session_now = request.session.get("user_role", None)
    if session_now in ['clerk']:
        today = date.today()
        patient = crud.get_all_patient(db)       
        patients_age = []
        for i in patient:
            i.PatientName = function.decrypt_data(i.PatientName, crud.get_patient_key(db, i.PK_PatientID))
            patients_age.append(function.calculate_age(i.PatientBirth, today))

        return templates.TemplateResponse("patientManage.html", {"request": request, 
                                                                 "patient": zip(patient, patients_age), 
                                                                 "doctor": crud.get_all_account_id_and_username_from_doctor(db), 
                                                                 "today": today, 
                                                                 "min_input_date": function.calculate_date_123_years_ago(),
                                                                 "create": create
                                                                 })
    else:
        return HTMLResponse(status_code=403)
       

@router.post("/createPatient", response_class=HTMLResponse, tags=["patientManage"])
async def create_patient(
    patient: schemas.PatientCreate = Depends(schemas.PatientCreate.as_form),
    db: Session = Depends(get_db)
):
    crud.create_patient(db, patient)

    return RedirectResponse("/patientManage?create=1",status_code=303)