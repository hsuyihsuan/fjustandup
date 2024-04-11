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





# 介面導引實現動態改變
# 以get(對應PHP的get)方法來進行病歷新增, tags是為方便管理可從/docs查看
@router.get("/add", response_class=HTMLResponse, tags=["add"])
async def add_page(
    request: Request,  # request參數為jinja2規定
    patient_id: Optional[str] = None,
    first_doctor_incorrect: Optional[str] = None,
    not_exist: Optional[str] = None,
    # 為啟用htmx(類似javascript), fastapi會將hx-request辨識為hx_requet, 詳情可參考官網htmx,
    htmxHeader: Optional[str] = Header(None),
    check_if_in_hospital: Optional[bool] = None,
    InOtherHospitalDate: Optional[str] = None,
    OtherDiseaseName: Optional[str] = None,
    OtherMedicineName: Optional[str] = None,
    delete_other_medicine_id: Optional[str] = None,
    CtDate: Optional[str] = None,
    BloodTestDate: Optional[str] = None,
    QOL_Date: Optional[date] = None,
    QMG_Date: Optional[date] = None,
    MGComposite_Date: Optional[date] = None,
    ADL_Date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    if request.session.get("user_role", None) == "doctor":
        if check_if_in_hospital:  # 若有get值則回傳部件html檔
            return templates.TemplateResponse("partials/treat.html", {"request": request})

        elif OtherDiseaseName or OtherDiseaseName == "":
            return templates.TemplateResponse("partials/otherDiseaseInput.html", {"request": request})
        # elif OtherDiseaseName == "":
        #      return templates.TemplateResponse("partials/otherDiseaseInput.html", {"request": request})

        elif OtherMedicineName or OtherMedicineName == "":
                return templates.TemplateResponse("partials/otherMedicineInput.html", {"request": request, "OtherMedicineName": random.randint(1, 1000)})#, "OtherMedicineName": OtherMedicineName

        elif CtDate:
            return templates.TemplateResponse("partials/thymusInput.html", {"request": request})

        elif BloodTestDate:
            return templates.TemplateResponse("partials/bloodTestInput.html", {"request": request})

        elif QOL_Date:
            qol_field_data = crud.get_patient_newest_qol(
                db, patient_id=patient_id)
            qol = function.CreateTableFields()
            qol = qol.create_table_fields(qol.qol, qol_field_data)

            if qol_field_data:
                qol_date = qol_field_data.QOL_Date
            else:
                qol_date = None
            return templates.TemplateResponse("partials/survey/qol.html", {"request": request, "qol": qol, "qol_date": qol_date})

        elif QMG_Date:
            qmg_field_data = crud.get_patient_newest_qmg(
                db, patient_id=patient_id)
            qmg = function.CreateTableFields()
            qmg = qmg.create_table_fields(qmg.qmg, qmg_field_data)

            if qmg_field_data:
                qmg_date = qmg_field_data.QMG_Date
            else:
                qmg_date = None

            return templates.TemplateResponse("partials/survey/qmg.html", {"request": request, "qmg": qmg, "qmg_date": qmg_date})

        elif MGComposite_Date:
            mg_composite_field_data = crud.get_patient_newest_mg_composite(
                db, patient_id=patient_id)
            mg_composite = function.CreateTableFields()
            mg_composite = mg_composite.create_table_fields(
                mg_composite.mg_composite, mg_composite_field_data)

            if mg_composite_field_data:
                mg_composite_date = mg_composite_field_data.MGComposite_Date
            else:
                mg_composite_date = None

            return templates.TemplateResponse("partials/survey/mgComposite.html", {"request": request, "mg_composite": mg_composite, "mg_composite_date": mg_composite_date})
        elif ADL_Date:
            adl_field_data = crud.get_patient_newest_adl(
                db, patient_id=patient_id)
            adl = function.CreateTableFields()
            adl = adl.create_table_fields(adl.adl, adl_field_data)

            if adl_field_data:
                adl_date = adl_field_data.ADL_Date
            else:
                adl_date = None

            return templates.TemplateResponse("partials/survey/adl.html", {"request": request, "adl": adl, "adl_date": adl_date})
        elif InOtherHospitalDate:  # 若有get值初診頁面回傳部件html檔
            # if InOtherHospitalDate:  # 確定選擇日期有值才插入html
                return templates.TemplateResponse("partials/inOtherHospitalCount.html", {"request": request})
        elif InOtherHospitalDate == "":
            return templates.TemplateResponse("partials/inOtherHospitalBlock.html", {"request": request})
        elif htmxHeader == "inOtherHospitalDateHasVisited":  # 若有get值複診頁面回傳部件html檔
            if InOtherHospitalDate:  # 確定選擇日期有值才插入html
                return templates.TemplateResponse("partials/inOtherHospitalCount.html", {"request": request, "inOtherHospitalDateHasVisited": 1})
        elif delete_other_medicine_id:
            return  # 於介面(非資料庫)刪除, 回傳空白製造刪除效果
        elif patient_id == None:
            return templates.TemplateResponse("inputPatientId.html", {"request": request, "not_exist": not_exist, "first_doctor_incorrect": first_doctor_incorrect})
        else:
            return
    else:
        return HTMLResponse(status_code=403)


@router.get("/delete", response_class=HTMLResponse, tags=["add"])
async def add_page_for_delete(
    request: Request,
    OtherDiseaseName: Optional[str] = None,
    OtherMedicineName: Optional[str] = None
):
    if OtherDiseaseName or OtherDiseaseName == "":
        return
    elif OtherMedicineName or OtherMedicineName == "":
        return


# 藉從inputPatientID.html的patient_id導引初診或複診html

@router.post("/add",  response_class=RedirectResponse, tags=["add"])
async def check_patientID_and_redirect(patient_id=Form()):
    url = "/add/patient_id="+patient_id
    return url

# 藉上方check_patinetId_and_redirect回傳介面


@router.post("/add/patient_id={patient_id}", response_class=HTMLResponse, tags=["add"])
async def redirect_page_by_patientID(
    request: Request,  # request參數為jinja2規定
    patient_id,  # 利用patient_id來從資料庫叫資料
    db: Session = Depends(get_db)  # 啟用資料庫Session才可操作
):
    session_account = request.session.get("account_id", None)  # 紀錄輸入就診者
    today = date.today()  # 從後端抓今日日期的值在傳到前端讓input type=date有預設值

    # 初診病歷號碼, == None 代表資料庫沒找到該病歷號碼曾在內
    # if crud.get_patient_id(db, patient_id) == None:
    if crud.check_if_patient_first_time(db, patient_id) == None:
        if patient := crud.check_if_doctor_is_patient_first_time(db, patient_id ,request.session['account_id']):
            patient.PatientName = function.decrypt_data(patient.PatientName, patient.PatientKey)
            patient_age = function.calculate_age(patient.PatientBirth, today)
            return templates.TemplateResponse("addNew.html", {"request": request,
                                                              "patient_id": patient_id,
                                                              "patient": patient,
                                                              "patient_age": patient_age,
                                                              "today": today,
                                                              "min_input_date": function.calculate_date_123_years_ago(),
                                                              "session_account": request.session['account_id']
                                                              })
        elif crud.get_patient_id(db, patient_id) == None:
            return RedirectResponse("/add?not_exist=1", status_code=303)
        else:
            return RedirectResponse("/add?first_doctor_incorrect=1", status_code=303)      
    else:  # 複診病歷號碼
        patient = crud.get_patient(db, patient_id)
        alert = crud.get_alert_if_exist(db, patient_id, request.session['account_id'])
        patient.PatientName = function.decrypt_data(patient.PatientName, patient.PatientKey)
        visit = crud.get_patient_newest_visit(db, patient_id)
        visit_count = crud.get_visit_count(db, patient_id)
        patient_age = function.calculate_age(patient.PatientBirth, today)
        in_other_hospital_date = str(patient.InOtherHospitalDate)
        days_of_onset = function.days_of_onset(patient.AttackDate, today)
        age_of_onset = function.calculate_age(
            patient.PatientBirth, patient.AttackDate)
        other_disease = crud.get_other_disease(db, patient_id)
        if in_hospital_date := crud.get_newest_in_hospital_date_by_patient_id(db, patient_id):
            in_hospital_date = in_hospital_date.VisitDate
        visit_record = crud.get_visit(db, patient_id)
        thymus = crud.get_patient_all_thymus(db, patient_id)
        if first_time_thymus_atrophy := crud.get_patient_first_time_thymus_atrophy(db, patient_id):
            first_time_thymus_atrophy = first_time_thymus_atrophy.CtDate
        if first_time_thymus_hyperplasia := crud.get_patient_first_time_thymus_hyperplasia(db, patient_id):
            first_time_thymus_hyperplasia = first_time_thymus_hyperplasia.CtDate
        if first_time_thymus_thymoma := crud.get_patient_first_time_thymus_thymoma(db, patient_id):
            first_time_thymus_thymoma = first_time_thymus_thymoma.CtDate
        other_medicine = crud.get_other_medicine(db, patient_id)
        blood_test = crud.get_patient_all_blood_test(db, patient_id)
        if qol_date := crud.get_patient_newest_qol(db, patient_id):
            qol_date = qol_date.QOL_Date
        if qmg_date := crud.get_patient_newest_qmg(db, patient_id):
            qmg_date = qmg_date.QMG_Date
        if mg_composite_date := crud.get_patient_newest_mg_composite(db, patient_id):
            mg_composite_date = mg_composite_date.MGComposite_Date
        if adl_date := crud.get_patient_newest_adl(db, patient_id):
            adl_date = adl_date.ADL_Date

        in_hospital_count = crud.get_in_hospital_count(db, patient_id)

        other_disease_list = []
        for i in other_disease:
            other_disease_list.append(
                [i.PK_OtherDiseaseID, i.OtherDiseaseName])

        if in_other_hospital_date == "0001-01-01":
            in_other_hospital_date = None

        return templates.TemplateResponse("addHasVisited.html",
                                          {"request": request,
                                           "patient_id": patient_id,
                                           "alert": alert,
                                           "today": today,
                                           "session_account": session_account,
                                           "patient": patient,
                                           "patient_age": patient_age,
                                           "visit": visit,
                                           "in_other_hospital_date": in_other_hospital_date,
                                           "days_of_onset": days_of_onset,
                                           "age_of_onset": age_of_onset,
                                           "other_disease": other_disease_list,
                                           "in_hospital_date": in_hospital_date,
                                           "in_hospital_count": in_hospital_count,
                                           "visit_count": visit_count,
                                           "visit_record": visit_record,
                                           "other_medicine": other_medicine,
                                           "thymus": thymus,
                                           "first_time_thymus_atrophy": first_time_thymus_atrophy,
                                           "first_time_thymus_hyperplasia": first_time_thymus_hyperplasia,
                                           "first_time_thymus_thymoma": first_time_thymus_thymoma,
                                           "blood_test": blood_test,
                                           "qol_date": qol_date,
                                           "qmg_date": qmg_date,
                                           "mg_composite_date": mg_composite_date,
                                           "adl_date": adl_date, 
                                           "min_input_date": function.calculate_date_123_years_ago(),
                                           "session_account_id": request.session['account_id']
                                           }
                                          )


# 新增初診病歷後端操作
@router.post("/addNew", tags=["add"])  # response_class=RedirectResponse,
async def add_new_data(
        # request: Request,
        patient_id: str = Form(),
        alert: int = Form(default=None),
        patient: schemas.PatientUpdateFromFirst = Depends(schemas.PatientUpdateFromFirst.as_form),
        visit: schemas.VisitCreate = Depends(schemas.VisitCreate.as_form),
        OtherDiseaseName: List[str] = Form(),
        OtherMedicineName: List[str] = Form(),
        OtherMedicineCount: List[int] = Form(),
        thymus: schemas.ThymusCreate = Depends(schemas.ThymusCreate.as_form),
        blood_test: schemas.BloodTestCreate = Depends(
            schemas.BloodTestCreate.as_form),
        qol: schemas.QOLCreate = Depends(schemas.QOLCreate.as_form),
        qmg: schemas.QMGCreate = Depends(schemas.QMGCreate.as_form),
        mg_composite: schemas.MGCompositeCreate = Depends(
            schemas.MGCompositeCreate.as_form),
        adl: schemas.ADLCreate = Depends(schemas.ADLCreate.as_form),
        db: Session = Depends(get_db)
):
    # treat = visit.Treat

    # patient.PatientKey = function.gernerate_crypt_key()[1]
    # patient.PatientName = function.encrypt_data(patient.PatientName, patient.PatientKey)
    crud.update_patient_from_first(db, patient)
    if alert:
        crud.create_alert(db, patient_id, visit.FK_AccountID)
    crud.create_visit(db, visit=visit)
    crud.create_other_disease(db, OtherDiseaseName)
    crud.create_other_medicine(
        db, other_medicine_name=OtherMedicineName, other_medicine_count=OtherMedicineCount)
    crud.create_thymus(db, thymus=thymus, patient_id=patient_id)
    crud.create_blood_test(db, blood_test=blood_test, patient_id=patient_id)
    crud.create_qol(db, qol=qol, patient_id=patient_id)
    crud.create_qmg(db, qmg=qmg, patient_id=patient_id)
    crud.create_mg_composite(
        db, mg_composite=mg_composite, patient_id=patient_id)
    crud.create_adl(db, adl=adl, patient_id=patient_id)

    url = "/watchVisit/"+patient_id

    return RedirectResponse(url)

# 新增複診病歷後端操作


@router.post("/addHasVisited",  tags=["add"])
async def add_visit_and_update_patient(
    request: Request,
    patient_id: str = Form(),
    alert: int = Form(default=None),
    update_field=Depends(schemas.PatientUpdateFromInput.as_form),
    visit=Depends(schemas.VisitCreate.as_form),
    OtherDiseaseName: List[str] = Form(),
    OtherMedicineName: List[str] = Form(),
    OtherMedicineCount: List[int] = Form(),
    thymus: schemas.ThymusCreate = Depends(schemas.ThymusCreate.as_form),
    blood_test: schemas.BloodTestCreate = Depends(
        schemas.BloodTestCreate.as_form),
    qol: schemas.QOLCreate = Depends(schemas.QOLCreate.as_form),
    qmg: schemas.QMGCreate = Depends(schemas.QMGCreate.as_form),
    mg_composite: schemas.MGCompositeCreate = Depends(
        schemas.MGCompositeCreate.as_form),
    adl: schemas.ADLCreate = Depends(schemas.ADLCreate.as_form),
    db: Session = Depends(get_db)
):
    if alert and crud.get_alert_if_exist(db, patient_id, request.session['account_id']) == None:
        crud.create_alert(db, patient_id, request.session['account_id'])
    elif alert == None and crud.get_alert_if_exist(db, patient_id, request.session['account_id']):
        crud.delete_alert(db, patient_id, request.session['account_id'])
    crud.update_patient_from_input(db, update_field)
    crud.create_visit(db, visit=visit)
    crud.create_other_disease(db, OtherDiseaseName)
    crud.create_other_medicine(db, OtherMedicineName, OtherMedicineCount)
    crud.create_thymus(db, thymus, patient_id)
    crud.create_blood_test(db, blood_test, patient_id)
    crud.create_qol(db, qol, patient_id)
    crud.create_qmg(db, qmg, patient_id)
    crud.create_mg_composite(db, mg_composite, patient_id)
    crud.create_adl(db, adl, patient_id)

    url = "/watchVisit/"+patient_id

    return RedirectResponse(url)
