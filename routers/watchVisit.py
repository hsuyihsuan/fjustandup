from fastapi import Request, Depends, HTTPException, Header, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pickle
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


#神秘原因會造成物件NoneType因此必需再轉get法才能啟用htmx
@router.post("/watchVisit/{patient_id}", tags=["watch"]) #承接自@app.post("/addNew")
async def watch_visit(
    
    patient_id: str,
    db: Session = Depends(get_db)
):
    visit_date = crud.get_patient_newest_visit_date(db, patient_id=patient_id).VisitDate

    # patient = crud.get_patient(db, patient_id=patient_id)
    # visit = crud.get_patient_newest_visit(db, patient_id=patient_id)
    # patient_age = function.calculate_age(born=patient.PatientBirth, today=today)
    # visit = crud.get_patient_newest_visit(db=db, patient_id=patient_id)
    url = "/watchVisit/"+patient_id+"/"+str(visit_date)
    return RedirectResponse(url, status_code=303)
    

@router.get("/watchVisit", response_class=RedirectResponse, tags=["watch"], status_code=307)
async def redirect_by_visit_date(
     patient_id: str,
     visit_date: date,
):
     url = "/watchVisit/"+patient_id+"/"+str(visit_date)

     return RedirectResponse(url, status_code=307)

#查看病歷頁面
@router.get("/watchVisit/{patient_id}/{visit_date}", response_class=HTMLResponse, tags=["watch"])
async def watch_page(
   request: Request, 
   patient_id: str,
   visit_date: date, 
   db: Session = Depends(get_db)
): 
    if request.session.get("user_role", None) == "doctor":
        
        today = date.today()

        patient = crud.get_patient(db, patient_id)
        account_id = request.session['account_id']
        alert = crud.get_alert_if_exist(db, patient_id, account_id)
        patient.PatientName = function.decrypt_data(patient.PatientName, crud.get_patient_key(db, patient_id))
        patient_age = function.calculate_age(patient.PatientBirth, today)
        visit = crud.get_patient_visit_by_date(db, patient_id, visit_date)
        input_user_name = crud.get_account_by_id(db, visit.FK_AccountID).UserName #crud.get_visit_input_account(db, visit.PK_VisitID, visit.FK_AccountID).UserName

        all_visit_date = []
        for i in reversed(crud.get_all_visit_date_by_patient_id(db, patient_id)):
                 all_visit_date.append(str(i.VisitDate))

        days_of_onset = function.days_of_onset(patient.AttackDate, today)
        age_of_onset = function.calculate_age(patient.PatientBirth, patient.AttackDate)
        bmi = function.bmi(visit.Height, visit.Weight)

        if in_hospital_date := crud.get_newest_in_hospital_date_by_patient_id(db, patient_id):
            in_hospital_date = in_hospital_date.VisitDate
        
        in_hospital_count = crud.get_in_hospital_count(db, patient_id)

        other_disease = crud.get_patient_other_disease_by_visit_date(db, patient_id, visit_date)
        other_medicine = crud.get_patient_other_medicine_by_visit_date(db, patient_id, visit_date)

        if first_time_thymus_atrophy := crud.get_patient_first_time_thymus_atrophy(db, patient_id):
            first_time_thymus_atrophy = first_time_thymus_atrophy.CtDate
        if first_time_thymus_hyperplasia := crud.get_patient_first_time_thymus_hyperplasia(db, patient_id):
            first_time_thymus_hyperplasia = first_time_thymus_hyperplasia.CtDate
        if first_time_thymus_thymoma := crud.get_patient_first_time_thymus_thymoma(db, patient_id):
            first_time_thymus_thymoma = first_time_thymus_thymoma.CtDate

        all_thymus_dates = []
        one_thymus = None
        thymus_date = None
        if thymus := crud.get_patient_all_thymus(db, patient_id):
            for i in thymus:
                all_thymus_dates.append(str(i.CtDate))
            one_thymus = crud.get_patient_newest_thymus(db, patient_id)
            thymus_date = one_thymus.CtDate
            

            

        all_blood_test_dates = []
        one_blood_test = None
        blood_test_date = None
        AchR = []
        TSH = []
        ANA = []
        if blood_test := crud.get_patient_all_blood_test(db, patient_id):
            for i in blood_test:
                all_blood_test_dates.append(str(i.BloodTestDate))
                if i.AchR != -1:
                    AchR.append(round(i.AchR, 2))
                else:
                    AchR.append('None')
                if i.TSH != -1:
                    TSH.append(round(i.TSH, 1))
                else:
                    TSH.append('None')
                if i.ANA != -1:
                     ANA.append(i.ANA)
                else:
                     ANA.append('None')
                
          
               
            
            one_blood_test = crud.get_patient_newest_blood_test(db, patient_id)
            blood_test_date = one_blood_test.BloodTestDate

        qol = None
        qol_date = None
        if qol_field_data := crud.get_patient_newest_qol(db, patient_id):
            qol_date = qol_field_data.QOL_Date
            qol = function.CreateTableFields()
            qol = qol.create_table_fields(qol.qol, qol_field_data)

        #從這開始改
        qmg = None
        qmg_date = None
        if qmg_field_data := crud.get_patient_newest_qmg(db, patient_id):
            qmg_date = qmg_field_data.QMG_Date
            qmg = function.CreateTableFields()
            qmg = qmg.create_table_fields(qmg.qmg, qmg_field_data)

        mg_composite = None
        mg_composite_date = None
        if mg_composite_field_data := crud.get_patient_newest_mg_composite(db, patient_id):
            mg_composite_date = mg_composite_field_data.MGComposite_Date
            mg_composite = function.CreateTableFields()
            mg_composite = mg_composite.create_table_fields(mg_composite.mg_composite, mg_composite_field_data)

        adl = None
        adl_date = None
        if adl_field_data := crud.get_patient_newest_adl(db, patient_id):
            adl_date = adl_field_data.ADL_Date
            adl = function.CreateTableFields()
            adl = adl.create_table_fields(adl.adl, adl_field_data)

            # if mg_composite_field_data:
            #     mg_composite_date = mg_composite_field_data.MGComposite_Date
            # else:
            #     mg_composite_date = None
        # crud.get_patient_all_qol_date(db, patient_id)
        all_qmg_dates = crud.get_patient_all_qmg_date(db, patient_id)
        all_mg_composite_dates = crud.get_patient_all_mg_composite_date(db, patient_id)
        all_adl_dates = crud.get_patient_all_adl_date(db, patient_id)
               
        all_visit = crud.get_patient_all_visit(db, patient_id)
        
        height = []
        weight = []
        sbp = []
        dbp = []
        pyridostigmine = []
        compesolone = []
        cellcept = []
        imuran = []
        prograf = []
        

        for i in all_visit:
            height.append(round(i.Height, 1))
            weight.append(round(i.Weight, 1))
            sbp.append(i.Sbp)
            dbp.append(i.Dbp)
            pyridostigmine.append(i.Pyridostigmine)
            compesolone.append(i.Compesolone)
            cellcept.append(i.Cellcept)
            imuran.append(i.Imuran)
            prograf.append(i.Prograf)

        all_qol = crud.get_patient_all_qol(db, patient_id)
        all_qol_dates = []
        qol_sum = []
        for i in all_qol:
             all_qol_dates.append(str(i.QOL_Date))
             qol_sum.append(i.QOL_Sum)

        

        all_qmg = crud.get_patient_all_qmg(db, patient_id)
        all_qmg_dates = []
        qmg_sum = []
        for i in all_qmg:
            all_qmg_dates.append(str(i.QMG_Date))
            qmg_sum.append(i.QMG_Sum)

        all_mg_composite = crud.get_patient_all_mg_composite(db, patient_id)
        all_mg_composite_dates = []
        mg_composite_sum = []
        for i in all_mg_composite:
            all_mg_composite_dates.append(str(i.MGComposite_Date))
            mg_composite_sum.append(i.MGComposite_Sum)

        all_adl = crud.get_patient_all_adl(db, patient_id)
        all_adl_dates = []
        adl_sum = []
        for i in all_adl:
            all_adl_dates.append(str(i.ADL_Date))
            adl_sum.append(i.ADL_Sum)

        
        try:
            # model_url = crud.get_model_which_is_activate(db).PK_CreateTime
            model_url = crud.get_active_model_if_exist(db, account_id)
        except:
            model_url = None


        return templates.TemplateResponse("watchVisit.html", {"request": request, 
                                                              "patient": patient, 
                                                              "alert": alert,
                                                              "account_id": account_id,
                                                              "patient_id": patient_id, 
                                                              "patient_age": patient_age, 
                                                              "visit": visit, 
                                                              "all_visit_date": all_visit_date, 
                                                              "all_visit_date_asc": list(reversed(all_visit_date)), 
                                                              "days_of_onset": days_of_onset, 
                                                              "age_of_onset": age_of_onset,
                                                              "bmi": bmi,
                                                              "in_hospital_date": in_hospital_date,
                                                              "in_hospital_count": in_hospital_count,
                                                              "other_disease": other_disease,
                                                              "other_medicine": other_medicine,
                                                              "thymus": thymus, 
                                                              "all_thymus_dates": all_thymus_dates, 
                                                              "one_thymus": one_thymus,
                                                              "thymus_date": thymus_date,
                                                              "first_time_thymus_atrophy": first_time_thymus_atrophy, 
                                                              "first_time_thymus_hyperplasia": first_time_thymus_hyperplasia, 
                                                              "first_time_thymus_thymoma": first_time_thymus_thymoma,
                                                              "blood_test": blood_test, 
                                                              "all_blood_test_dates": all_blood_test_dates, 
                                                            #   "all_blood_test_dates_asc": list(reversed(all_blood_test_dates)), 
                                                              "one_blood_test": one_blood_test,
                                                            #   "blood_test_date": blood_test_date,
                                                              "AchR": AchR,
                                                              "TSH": TSH,
                                                              "ANA": ANA,

                                                              "all_qol_dates": all_qol_dates,
                                                              "qol": qol,
                                                              "qol_sum": qol_sum,
                                                              "qol_date": qol_date,

                                                              "all_qmg_dates": all_qmg_dates,
                                                              "qmg": qmg,
                                                              "qmg_sum": qmg_sum,
                                                              "qmg_date": qmg_date,

                                                              "all_mg_composite_dates": all_mg_composite_dates,
                                                              "mg_composite": mg_composite, 
                                                              "mg_composite_sum": mg_composite_sum,
                                                              "mg_composite_date": mg_composite_date,
                                                              
                                                              "all_adl_dates": all_adl_dates,
                                                              "adl": adl,
                                                              "adl_sum": adl_sum,
                                                              "adl_date": adl_date,

                                                              "watch": 1,
                                                              "basic": "height_and_weight",
                                                            #   "height": height,
                                                            #   "weight": weight, 
                                                            #   "sbp": sbp,
                                                            #   "dbp": dbp,
                                                              "pyridostigmine": pyridostigmine,
                                                              "compesolone": compesolone,
                                                              "cellcept": cellcept, 
                                                              "imuran": imuran, 
                                                              "prograf": prograf, 
                                                          
                                                              "model_url": model_url,
                                                              "input_user_name": input_user_name,
                                                              "session_account_id": request.session['account_id']

                                                              })
    else:
         return HTMLResponse(status_code=403)


#胸腺或抗體抽血
@router.get("/getThymusOrBloodTest", response_class=HTMLResponse , tags=['watch'])
async def watch_page_thymus_or_blood_test(
    request: Request,
    patient_id: str,
    thymus_date: Optional[date] = None, 
    blood_test_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    
   
    if thymus_date:
        
        one_thymus = crud.get_patient_thymus_by_date(db, patient_id, thymus_date)
        
        all_thymus_dates = []
        if thymus := crud.get_patient_all_thymus(db, patient_id):
            for i in thymus:
                all_thymus_dates.append(str(i.CtDate))
            
        return templates.TemplateResponse("partials/watchVisit/thymus.html", {"request": request, "one_thymus": one_thymus, "thymus_date": str(thymus_date), "all_thymus_dates": all_thymus_dates, "session_account_id": request.session['account_id']})

    elif blood_test_date:
        one_blood_test = crud.get_patient_blood_test_by_date(db, patient_id, blood_test_date)
        
        all_blood_test_dates = []
        if blood_test := crud.get_patient_all_blood_test(db, patient_id):
            for i in blood_test:
                all_blood_test_dates.append(str(i.BloodTestDate))
            
        return templates.TemplateResponse("partials/watchVisit/bloodTest.html", {"request": request, "one_blood_test": one_blood_test, "blood_test_date": str(blood_test_date), "all_blood_test_dates": all_blood_test_dates})
         
     
   



#量表讀取資料
@router.get("/getSurvey", response_class=HTMLResponse, tags=["watch"])
async def watch_page_survey(
    request: Request,
    patient_id: str,
    qol_date: Optional[date] = None,
    qmg_date: Optional[date] = None,
    mg_composite_date: Optional[date] = None,
    adl_date: Optional[date] = None,
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
    
    elif qmg_date:

        all_qmg = crud.get_patient_all_qmg(db, patient_id)
        all_qmg_dates = []
 
        for i in all_qmg:
             all_qmg_dates.append(str(i.QMG_Date))

        qmg_field_data = crud.get_patient_qmg_by_date(db, patient_id, qmg_date)
        qmg = function.CreateTableFields()
        qmg = qmg.create_table_fields(qmg.qmg, qmg_field_data)
        return templates.TemplateResponse("partials/survey/qmg.html", {"request": request, "qmg": qmg, "all_qmg_dates":all_qmg_dates, "qmg_date": str(qmg_date), "patient_id": patient_id,  "watch": 1})
   
    elif mg_composite_date:

        all_mg_composite = crud.get_patient_all_mg_composite(db, patient_id)
        all_mg_composite_dates = []
 
        for i in all_mg_composite:
            all_mg_composite_dates.append(str(i.MGComposite_Date))

        mg_composite_field_data = crud.get_patient_mg_composite_by_date(db, patient_id, mg_composite_date)
        mg_composite = function.CreateTableFields()
        mg_composite = mg_composite.create_table_fields(mg_composite.mg_composite, mg_composite_field_data)
        return templates.TemplateResponse("partials/survey/mgComposite.html", {"request": request, "mg_composite": mg_composite,  "all_mg_composite_dates":all_mg_composite_dates, "mg_composite_date": str(mg_composite_date), "patient_id": patient_id, "watch": 1})
    
    elif adl_date:

        all_adl = crud.get_patient_all_adl(db, patient_id)
        all_adl_dates = []
 
        for i in all_adl:
            all_adl_dates.append(str(i.ADL_Date))

        adl_field_data = crud.get_patient_adl_by_date(db, patient_id, adl_date)
        adl = function.CreateTableFields()
        adl = adl.create_table_fields(adl.adl, adl_field_data)
        return templates.TemplateResponse("partials/survey/adl.html", {"request": request, "adl": adl, "all_adl_dates":all_adl_dates, "adl_date": str(adl_date), "patient_id": patient_id, "watch": 1})


# @router.get("/test", response_class=HTMLResponse)
# async def test(
#     request: Request
# ):
#     return templates.TemplateResponse("test.html", {"request": request})


@router.get("/basicFig/{patient_id}/{basic}", response_class=HTMLResponse, tags=["watch"])
async def watch_page_basic_fig(
    request: Request,
    patient_id: str,
    basic: Optional[str] = "height_and_weight", 
    db: Session = Depends(get_db)
):
    if basic == "height_and_weight":  
        all_visit_date = []
        for i in reversed(crud.get_all_visit_date_by_patient_id(db, patient_id)):
                    all_visit_date.append(str(i.VisitDate))
        
        # 有時間看要不要優化
        all_visit = crud.get_patient_all_visit(db, patient_id)

        height = []
        weight = []
        for i in all_visit:
            height.append(round(i.Height, 1))
            weight.append(round(i.Weight, 1))


        return templates.TemplateResponse("partials/figure/heightAndWeight.html", {"request": request, "height": height, "weight": weight, "all_visit_date_asc": list(reversed(all_visit_date))})
    
    elif basic == "blood_pressure":
        all_visit_date = []
        for i in reversed(crud.get_all_visit_date_by_patient_id(db, patient_id)):
                    all_visit_date.append(str(i.VisitDate))

        all_visit = crud.get_patient_all_visit(db, patient_id)

        sbp = []
        dbp = []
        for i in all_visit:
            sbp.append(round(i.Sbp, 1))
            dbp.append(round(i.Dbp, 1))
        return templates.TemplateResponse("partials/figure/bloodPressure.html", {"request": request, "sbp": sbp, "dbp": dbp, "all_visit_date_asc": list(reversed(all_visit_date))})


@router.get("/bloodTestFig/{patient_id}/{blood_test_type}", response_class=HTMLResponse, tags=["watch"])
async def watch_page_blood_test_fig(
    request: Request,
    patient_id: str,
    blood_test_type: Optional[str] = "AchR", 
    db: Session = Depends(get_db)
):
    all_blood_test_dates = []

    AchR = []
    TSH = []
    ANA = []
    blood_test = crud.get_patient_all_blood_test(db, patient_id)
    for i in blood_test:
        all_blood_test_dates.append(str(i.BloodTestDate))
            # if i.ANA != -1:
            #      ANA.append(i.ANA)
            # else:
            #      ANA.append('None')

    if blood_test_type == "AchR":  
        AchR = []
        for i in blood_test:
            if i.AchR != -1:
                AchR.append(round(i.AchR, 2))
            else:
                AchR.append('None')
        return templates.TemplateResponse("partials/figure/bloodTest/AchR.html", {"request": request, "AchR": AchR, "all_blood_test_dates": all_blood_test_dates})
    
    elif blood_test_type == "TSH":
        TSH = []
        for i in blood_test:
            if i.TSH != -1:
                TSH.append(round(i.TSH, 1))
            else:
                TSH.append('None')
        return templates.TemplateResponse("partials/figure/bloodTest/TSH.html", {"request": request, "TSH": TSH, "all_blood_test_dates": all_blood_test_dates})

    elif blood_test_type == "fT4":
        fT4 = []
        for i in blood_test:
            if i.FreeThyroxine != -1:
                fT4.append(round(i.FreeThyroxine, 1))
            else:
                fT4.append('None')
        return templates.TemplateResponse("partials/figure/bloodTest/fT4.html", {"request": request, "fT4": fT4, "all_blood_test_dates": all_blood_test_dates})

    elif blood_test_type == "ANA":
        ANA = []
        for i in blood_test:
            if i.ANA != -1:
                ANA.append(i.ANA)
            else:
                ANA.append('None')
        return templates.TemplateResponse("partials/figure/bloodTest/ANA.html", {"request": request, "ANA": ANA, "all_blood_test_dates": all_blood_test_dates})

    elif blood_test_type == "UricAcid":
        UricAcid = []
        for i in blood_test:
            if i.UricAcid != -1:
                UricAcid.append(round(i.UricAcid, 1))
            else:
                UricAcid.append('None')
        return templates.TemplateResponse("partials/figure/bloodTest/UricAcid.html", {"request": request, "UricAcid": UricAcid, "all_blood_test_dates": all_blood_test_dates})
     




# @router.post("/findVisitByDate", response_class=RedirectResponse)
# async def find_visit_by_date(
#     patient_id: str = Form(), 
#     visit_date: str = Form()
# ):
#     visit_data = crud.get_visit_by_date(db, patient_id=patient_id, visit_date=visit_date)
