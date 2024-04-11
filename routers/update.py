from fastapi import Request, Depends, HTTPException, Header, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
import crud, function, schemas
from database import SessionLocal
from sqlalchemy.orm import Session
from datetime import date
from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter()

templates = Jinja2Templates(directory="templates") # 為能前後端分離, 將前端介面存在templates資料夾裡供使用, jinja2是知名樣板(template)處理器

def get_db(): #給予資料庫session啟用
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.put("/updateAlert/{patient_id}/{account_id}", tags=["update"])
async def alert_update(
    patient_id: str,
    account_id: int,
    db: Session = Depends(get_db)
):
    
    if crud.get_alert_if_exist(db, patient_id, account_id):
        crud.delete_alert(db, patient_id, account_id)
    else:
        crud.create_alert(db, patient_id, account_id)
    # crud.update_patient_alert(db, patient_id)
    
    return



@router.get("/updatePatient/{patient_id}", response_class=HTMLResponse, tags=["update"])
async def update_page(
    request: Request, 
    patient_id: str,
    db: Session = Depends(get_db)
):
    today = date.today()
    patient = crud.get_patient(db, patient_id)
    patient.PatientName = function.decrypt_data(patient.PatientName, crud.get_account_key(db, request.session['account_id']))
    return templates.TemplateResponse("partials/update/patient.html", {"request": request, "today": today, "patient": patient})

@router.put("/updatePatient/{patient_id}", tags=["update"])
async def visit_update(
    # request: Request,
    patient_id: str,
    patient_update_fields = Depends(schemas.PatientUpdate.as_form),
    db: Session = Depends(get_db)
):
    crud.update_patient(db, patient_update_fields)
    url = "/returnWatchVisitPatient/"+patient_id
    return RedirectResponse(url, status_code=303)

@router.get("/returnWatchVisitPatient/{patient_id}", tags=["update"])
async def return_back_watch_visit_patient(
    request: Request,
    patient_id: str,
    db: Session = Depends(get_db)
):
    today = date.today()
    patient = crud.get_patient(db, patient_id)
    patient.PatientName = function.decrypt_data(patient.PatientName, crud.get_account_key(db, request.session['account_id']))
    patient_age = function.calculate_age(patient.PatientBirth, today)
    if in_hospital_date := crud.get_newest_in_hospital_date_by_patient_id(db, patient_id):
            in_hospital_date = in_hospital_date.VisitDate
        
    in_hospital_count = crud.get_in_hospital_count(db, patient_id)
    days_of_onset = function.days_of_onset(patient.AttackDate, today)
    age_of_onset = function.calculate_age(patient.PatientBirth, patient.AttackDate)
    return templates.TemplateResponse("partials/watchVisit/patient.html", {"request": request, "patient": patient, "patient_age": patient_age, "days_of_onset": days_of_onset, "age_of_onset": age_of_onset, "in_hospital_date": in_hospital_date, "in_hospital_count": in_hospital_count})



@router.get("/updateBasicVisit/{patient_id}/{visit_date}", response_class=HTMLResponse, tags=["update"])
async def update_basic_visi_page(
    request: Request, 
    patient_id: str,
    visit_date: date,
    db: Session = Depends(get_db)
):
    visit = crud.get_patient_visit_by_date(db, patient_id, visit_date)
    return templates.TemplateResponse("partials/update/basicVisit.html", {"request": request, "visit": visit, "patient_id": patient_id})


@router.put("/updateBasicVisit/{patient_id}/{visit_date}", tags=["update"])
async def basic_visit_update(
    request: Request,
    patient_id: str,
    visit_date: date,
    basic_visit_update_fields = Depends(schemas.BasicVisitUpdate.as_form),
    RecordType: str = Form(),
    Content: str = Form(),
    Reason: str = Form(),
    db: Session = Depends(get_db)
):
    crud.update_basic_visit(db, basic_visit_update_fields)
    crud.create_active_record(db, RecordType, patient_id, visit_date, Reason, request.session['account_id'], Content)
    url = "/returnWatchVisitBasicVisit/"+patient_id+"/"+str(visit_date)
    return " " #RedirectResponse(url, status_code=303)


@router.get("/returnWatchVisitBasicVisit/{patient_id}/{visit_date}", tags=["update"])
async def return_back_watch_visit_patient(
    request: Request,
    patient_id: str,
    visit_date: date,
    db: Session = Depends(get_db)
):
    visit = crud.get_patient_visit_by_date(db, patient_id, visit_date)
    other_disease = crud.get_patient_other_disease_by_visit_date(db, patient_id, visit_date)
    bmi = function.bmi(visit.Height, visit.Weight)

    return templates.TemplateResponse("partials/watchVisit/basicVisit.html", {"request": request, "visit": visit, "patient_id": patient_id, "bmi": bmi, "other_disease": other_disease})




@router.get("/updateMedicine/{patient_id}/{visit_date}", response_class=HTMLResponse, tags=["update"])
async def update_page(
    request: Request, 
    patient_id: str,
    visit_date: date,
    db: Session = Depends(get_db)
):
    visit = crud.get_patient_visit_by_date(db, patient_id, visit_date)
    return templates.TemplateResponse("partials/update/medicine.html", {"request": request, "visit": visit, "patient_id": patient_id})


@router.put("/updateMedicine/{patient_id}/{visit_date}", tags=["update"])
async def visit_update(
    patient_id: str,
    visit_date: date,
    medicine_update_fields = Depends(schemas.MedicineUpdate.as_form),
    db: Session = Depends(get_db)
):
    crud.update_medicine(db, medicine_update_fields)
    url = "/returnWatchVisitMedicine/"+patient_id+"/"+str(visit_date)
    return RedirectResponse(url, status_code=303)




@router.get("/returnWatchVisitMedicine/{patient_id}/{visit_date}", tags=["update"])
async def return_back_watch_visit_patient(
    request: Request,
    patient_id: str,
    visit_date: date,
    db: Session = Depends(get_db)
):
    visit = crud.get_patient_visit_by_date(db, patient_id, visit_date)

    return templates.TemplateResponse("partials/watchVisit/medicine.html", {"request": request, "visit": visit, "patient_id": patient_id})




@router.get("/updateThymus/{patient_id}/{ct_date}", response_class=HTMLResponse, tags=["update"])
async def update_thymus_page(
    request: Request, 
    patient_id: str,
    ct_date: date,
    db: Session = Depends(get_db)
):
    one_thymus = crud.get_patient_thymus_by_date(db, patient_id, ct_date)
    return templates.TemplateResponse("partials/update/thymus.html", {"request": request, "one_thymus": one_thymus, "patient_id": patient_id})

@router.put("/updateThymus/{patient_id}/{ct_date}", tags=["update"])
async def thymus_update(
    patient_id: str,
    ct_date: date,
    thymus_update_fields = Depends(schemas.ThymusUpdate.as_form),
    db: Session = Depends(get_db)
):
    crud.update_thymus(db, thymus_update_fields)
    url = "/returnWatchVisitThymus/"+patient_id+"/"+str(ct_date)
    return RedirectResponse(url, status_code=303)


@router.get("/returnWatchVisitThymus/{patient_id}/{ct_date}", tags=["update"])
async def return_back_watch_visit_thymus(
    request: Request,
    patient_id: str,
    ct_date: date,
    db: Session = Depends(get_db)
):
    thymus = crud.get_patient_all_thymus(db, patient_id)
    one_thymus = crud.get_patient_thymus_by_date(db, patient_id, ct_date)
    all_thymus_dates = []

    for i in thymus:
         all_thymus_dates.append(str(i.CtDate))

    return templates.TemplateResponse("partials/watchVisit/thymus.html", {"request": request, "one_thymus": one_thymus, "all_thymus_dates": all_thymus_dates, "patient_id": patient_id, "thymus_date": str(ct_date)})


@router.get("/updateQOL/{patient_id}/{qol_date}", response_class=HTMLResponse, tags=['update'])
async def update_qol(
    request: Request,
    patient_id: str,
    qol_date: date, 
    db: Session = Depends(get_db)
):
    qol_field_data = crud.get_patient_qol_by_date(db, patient_id, qol_date)
    qol_id = qol_field_data.PK_QOLTableID
    qol = function.CreateTableFields()
    qol = qol.create_table_fields(qol.qol, qol_field_data)

    return templates.TemplateResponse("partials/watchVisit/survey/qolPartial.html", {"request": request, "patient_id": patient_id, "qol_id": qol_id, "qol": qol, "qol_date": qol_date, "update": 1})


@router.put("/updateQOL/{patient_id}/{qol_date}", tags=["update"])
async def qol_update(
    patient_id: str,
    qol_date: date,
    qol_update_fields = Depends(schemas.QOLTableUpdate.as_form),
    db: Session = Depends(get_db)
):
    crud.update_qol(db, qol_update_fields)
    url = "/returnWatchVisitQOL/"+patient_id+"/"+str(qol_date)
    return RedirectResponse(url, status_code=303)



@router.get("/returnWatchVisitQOL/{patient_id}/{qol_date}", tags=["update"])
async def return_back_watch_visit_qol(
    request: Request,
    patient_id: str,
    qol_date: date,
    db: Session = Depends(get_db)
):
   if qol_date:
        
        all_qol = crud.get_patient_all_qol(db, patient_id)
        all_qol_dates = []
 
        for i in all_qol:
             all_qol_dates.append(str(i.QOL_Date))
          
        qol_field_data = crud.get_patient_qol_by_date(db, patient_id, qol_date)
        qol = function.CreateTableFields()
        qol = qol.create_table_fields(qol.qol, qol_field_data)
        return templates.TemplateResponse("partials/survey/qol.html", {"request": request, "qol": qol, "all_qol_dates":all_qol_dates, "qol_date": str(qol_date), "patient_id": patient_id,  "watch": 1})


@router.put("/updateQMG/{patient_id}/{qmg_date}", tags=["update"])
async def qmg_update(
    patient_id: str,
    qmg_date: date,
    qmg_update_fields = Depends(schemas.QMGTableUpdate.as_form),
    db: Session = Depends(get_db)
):
    crud.update_qmg(db, qmg_update_fields)
    url = "/returnWatchVisitQMG/"+patient_id+"/"+str(qmg_date)
    return RedirectResponse(url, status_code=303)


@router.get("/updateQMG/{patient_id}/{qmg_date}", response_class=HTMLResponse, tags=['update'])
async def update_qmg(
    request: Request,
    patient_id: str,
    qmg_date: date, 
    db: Session = Depends(get_db)
):
    qmg_field_data = crud.get_patient_qmg_by_date(db, patient_id, qmg_date)
    qmg_id = qmg_field_data.PK_QMGTableID
    qmg = function.CreateTableFields()
    qmg = qmg.create_table_fields(qmg.qmg, qmg_field_data)

    return templates.TemplateResponse("partials/watchVisit/survey/qmgPartial.html", {"request": request, "patient_id": patient_id, "qmg_id": qmg_id, "qmg": qmg, "qmg_date": qmg_date, "update": 1})


@router.get("/returnWatchVisitQMG/{patient_id}/{qmg_date}", tags=["update"])
async def return_back_watch_visit_qmg(
    request: Request,
    patient_id: str,
    qmg_date: date,
    db: Session = Depends(get_db)
):
   if qmg_date:
        
        all_qmg = crud.get_patient_all_qmg(db, patient_id)
        all_qmg_dates = []
 
        for i in all_qmg:
             all_qmg_dates.append(str(i.QMG_Date))
          
        qmg_field_data = crud.get_patient_qmg_by_date(db, patient_id, qmg_date)
        qmg = function.CreateTableFields()
        qmg = qmg.create_table_fields(qmg.qmg, qmg_field_data)
        return templates.TemplateResponse("partials/survey/qmg.html", {"request": request, "qmg": qmg, "all_qmg_dates":all_qmg_dates, "qmg_date": str(qmg_date), "patient_id": patient_id,  "watch": 1})




@router.get("/updateMGComposite/{patient_id}/{mg_composite_date}", response_class=HTMLResponse, tags=['update'])
async def update_mg_composite(
    request: Request,
    patient_id: str,
    mg_composite_date: date, 
    db: Session = Depends(get_db)
):
    mg_composite_field_data = crud.get_patient_mg_composite_by_date(db, patient_id, mg_composite_date)
    mg_composite_id = mg_composite_field_data.PK_MGCompositeTableID
    mg_composite = function.CreateTableFields()
    mg_composite = mg_composite.create_table_fields(mg_composite.mg_composite, mg_composite_field_data)

    return templates.TemplateResponse("partials/watchVisit/survey/mgCompositePartial.html", {"request": request, "patient_id": patient_id, "mg_composite_id": mg_composite_id, "mg_composite": mg_composite, "mg_composite_date": mg_composite_date, "update": 1})


@router.put("/updateMGComposite/{patient_id}/{mg_composite_date}", tags=["update"])
async def mg_composite_update(
    patient_id: str,
    mg_composite_date: date,
    mg_composite_update_fields = Depends(schemas.MGCompositeTableUpdate.as_form),
    db: Session = Depends(get_db)
):
    crud.update_mg_composite(db, mg_composite_update_fields)
    url = "/returnWatchVisitMGComposite/"+patient_id+"/"+str(mg_composite_date)
    return RedirectResponse(url, status_code=303)



@router.get("/returnWatchVisitMGComposite/{patient_id}/{mg_composite_date}", tags=["update"])
async def return_back_watch_visit_mg_composite(
    request: Request,
    patient_id: str,
    mg_composite_date: date,
    db: Session = Depends(get_db)
):
   if mg_composite_date:
        
        all_mg_composite = crud.get_patient_all_mg_composite(db, patient_id)
        all_mg_composite_dates = []
 
        for i in all_mg_composite:
             all_mg_composite_dates.append(str(i.MGComposite_Date))
          
        mg_composite_field_data = crud.get_patient_mg_composite_by_date(db, patient_id, mg_composite_date)
        mg_composite = function.CreateTableFields()
        mg_composite = mg_composite.create_table_fields(mg_composite.mg_composite, mg_composite_field_data)
        return templates.TemplateResponse("partials/survey/mgComposite.html", {"request": request, "mg_composite": mg_composite, "all_mg_composite_dates":all_mg_composite_dates, "mg_composite_date": str(mg_composite_date), "patient_id": patient_id,  "watch": 1})



@router.get("/updateADL/{patient_id}/{adl_date}", response_class=HTMLResponse, tags=['update'])
async def update_adl(
    request: Request,
    patient_id: str,
    adl_date: date, 
    db: Session = Depends(get_db)
):
    adl_field_data = crud.get_patient_adl_by_date(db, patient_id, adl_date)
    adl_id = adl_field_data.PK_ADLTableID
    adl = function.CreateTableFields()
    adl = adl.create_table_fields(adl.adl, adl_field_data)

    return templates.TemplateResponse("partials/watchVisit/survey/adlPartial.html", {"request": request, "patient_id": patient_id, "adl_id": adl_id, "adl": adl, "adl_date": adl_date, "update": 1})


@router.put("/updateADL/{patient_id}/{adl_date}", tags=["update"])
async def adl_update(
    patient_id: str,
    adl_date: date,
    adl_update_fields = Depends(schemas.ADLTableUpdate.as_form),
    db: Session = Depends(get_db)
):
    crud.update_adl(db, adl_update_fields)
    url = "/returnWatchVisitADL/"+patient_id+"/"+str(adl_date)
    return RedirectResponse(url, status_code=303)



@router.get("/returnWatchVisitADL/{patient_id}/{adl_date}", tags=["update"])
async def return_back_watch_visit_adl(
    request: Request,
    patient_id: str,
    adl_date: date,
    db: Session = Depends(get_db)
):
   if adl_date:
        
        all_adl = crud.get_patient_all_adl(db, patient_id)
        all_adl_dates = []
 
        for i in all_adl:
            all_adl_dates.append(str(i.ADL_Date))
          
        adl_field_data = crud.get_patient_adl_by_date(db, patient_id, adl_date)
        adl = function.CreateTableFields()
        adl = adl.create_table_fields(adl.adl, adl_field_data)
        return templates.TemplateResponse("partials/survey/adl.html", {"request": request, "adl": adl, "all_adl_dates":all_adl_dates, "adl_date": str(adl_date), "patient_id": patient_id,  "watch": 1})



@router.get("/updateBloodTest/{patient_id}/{blood_test_date}", response_class=HTMLResponse, tags=["update"])
async def update_page(
    request: Request, 
    patient_id: str,
    blood_test_date: date,
    db: Session = Depends(get_db)
):
    one_blood_test = crud.get_patient_blood_test_by_date(db, patient_id, blood_test_date)
    return templates.TemplateResponse("partials/update/bloodTest.html", {"request": request, "one_blood_test": one_blood_test, "patient_id": patient_id})


@router.put("/updateBloodTest/{patient_id}/{blood_test_date}", tags=["update"])
async def visit_update(
    patient_id: str,
    blood_test_date: date,
    blood_test_update_fields = Depends(schemas.BloodTestUpdate.as_form),
    db: Session = Depends(get_db)
):
    crud.update_blood_test(db, blood_test_update_fields)
    url = "/returnWatchVisitBloodTest/"+patient_id+"/"+str(blood_test_date)
    return RedirectResponse(url, status_code=303)



@router.get("/returnWatchVisitBloodTest/{patient_id}/{blood_test_date}", tags=["update"])
async def return_back_watch_visit_patient(
    request: Request,
    patient_id: str,
    blood_test_date: date,
    db: Session = Depends(get_db)
):
    blood_test = crud.get_patient_all_blood_test(db, patient_id)
    one_blood_test = crud.get_patient_blood_test_by_date(db, patient_id, blood_test_date)
    all_blood_test_dates = []

    for i in blood_test:
         all_blood_test_dates.append(str(i.BloodTestDate))

    return templates.TemplateResponse("partials/watchVisit/bloodTest.html", {"request": request, "one_blood_test": one_blood_test, "all_blood_test_dates": all_blood_test_dates, "patient_id": patient_id, "blood_test_date": str(blood_test_date)})



@router.get("/updateSelfAssessment/{patient_id}/{visit_date}", response_class=HTMLResponse, tags=["update"])
async def update_page(
    request: Request, 
    patient_id: str,
    visit_date: date,
    db: Session = Depends(get_db)
):
    visit = crud.get_patient_visit_by_date(db, patient_id, visit_date)
    return templates.TemplateResponse("partials/update/selfAssessment.html", {"request": request, "visit": visit, "patient_id": patient_id})



@router.put("/updateSelfAssessment/{patient_id}/{visit_date}", tags=["update"])
async def visit_update(
    patient_id: str,
    visit_date: date,
    self_assessment_update_fields = Depends(schemas.SelfAssessmentUpdate.as_form),
    db: Session = Depends(get_db)
):
    crud.update_self_assessment(db, self_assessment_update_fields)
    url = "/returnWatchVisitSelfAssessment/"+patient_id+"/"+str(visit_date)
    return RedirectResponse(url, status_code=303)



@router.get("/returnWatchVisitSelfAssessment/{patient_id}/{visit_date}", tags=["update"])
async def return_back_watch_visit_patient(
    request: Request,
    patient_id: str,
    visit_date: date,
    db: Session = Depends(get_db)
):
    visit = crud.get_patient_visit_by_date(db, patient_id, visit_date)

    return templates.TemplateResponse("partials/watchVisit/selfAssessment.html", {"request": request, "visit": visit, "patient_id": patient_id})

