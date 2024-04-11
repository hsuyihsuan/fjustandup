from fastapi import Request, File, UploadFile, Depends
from typing import Optional
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from fastapi.responses import RedirectResponse
from fastapi import APIRouter
from database import SessionLocal

import crud
import function
from sqlalchemy.orm import Session
from datetime import date
import statistics


router = APIRouter()


# 為能前後端分離, 將前端介面存在templates資料夾裡供使用, jinja2是知名樣板(template)處理器
templates = Jinja2Templates(directory="templates")


def get_db():  # 給予資料庫session啟用
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/analyze", tags=["analyze"])
async def analyze_page(
    request: Request,
    db: Session = Depends(get_db)
):
    session_now = request.session.get("user_role", None)
    if session_now in ['doctor']:
        today = date.today()

        all_patient = crud.get_all_patient(db)

        male, female, sex_count_correct = 0, 0, 0 #至少兩筆男性、兩筆女性才能進行敘述統計
        for i in all_patient:
            if i.PatientSex == 1:
                male += 1
            elif i.PatientSex == 0:
                female += 1

            if male > 1 and female > 1:
                sex_count_correct = 1
                break
        

        if sex_count_correct:
            all_patient_age = [0]*40 # 0~9男,10~19男, ... 90~99男, 0~9女, 10~19女, ..., 90~99女, 總數*10區間,比率*10區間 
            all_patient_age_at_onset = [0]*40

            all_patient_sex = [0, 0, 0, 0]  # 男總數, 女總數, 男比率, 女比率

            all_male_disease_duration_months = [] #男發病時長
            all_female_disease_duration_months = [] #女發病時長

            all_male_in_hospital = [] #男性住院次數
            all_female_in_hospital = [] #女性住院次數

            for i in all_patient:
                if i.PatientSex and str(i.AttackDate) != '0001-01-01': #attackDate是為了確定已初始化
                    all_patient_sex[0] += 1

                    for j in range(10):
                        if (10*j) <= function.calculate_age(i.PatientBirth, today) <= (10*j+9): #0~9, 10~19, 20~29
                            all_patient_age[j] += 1
                        if (10*j) <= function.calculate_age(i.PatientBirth, i.AttackDate) <= (10*j+9):
                            all_patient_age_at_onset[j] += 1
                    all_male_disease_duration_months.append(function.disease_duration_months(i.AttackDate, today))
                    all_male_in_hospital.append(crud.get_in_hospital_count(db, i.PK_PatientID) + i.InOtherHospitalCount)
                elif str(i.AttackDate) != '0001-01-01':
                    all_patient_sex[1] += 1

                    for j in range(10):
                        if (10*j) <=  function.calculate_age(i.PatientBirth, today) <= (10*j+9):
                            all_patient_age[j+10] += 1
                        if (10*j) <= function.calculate_age(i.PatientBirth, i.AttackDate) <= (10*j+9):
                            all_patient_age_at_onset[j+10] += 1
                    all_female_disease_duration_months.append(function.disease_duration_months(i.AttackDate, today))
                    all_female_in_hospital.append(crud.get_in_hospital_count(db, i.PK_PatientID) + i.InOtherHospitalCount)



            all_patient_sex[2] = 100*round(all_patient_sex[0] / (all_patient_sex[0] + all_patient_sex[1]), 2) #男性比率
            all_patient_sex[3] = 100*round(all_patient_sex[1] / (all_patient_sex[0] + all_patient_sex[1]), 2) #女性比率

            for i in range(10):
                all_patient_age[i+20] = all_patient_age[i] + all_patient_age[i+10] #各年齡總數
                all_patient_age_at_onset[i+20] = all_patient_age_at_onset[i] + all_patient_age_at_onset[i+10]

            for i in range(10):
                all_patient_age[i+30] = 100*round(all_patient_age[i+20] / sum(all_patient_age[20:30]), 2)
                all_patient_age_at_onset[i+30] = 100*round(all_patient_age_at_onset[i+20] / sum(all_patient_age_at_onset[20:30]), 2)

            #男性情況, 女性情況計算
            all_male_disease_duration_stat = [0,0,0,0]
            all_male_disease_duration_stat[0] = statistics.mean(all_male_disease_duration_months)
            all_male_disease_duration_stat[1] = statistics.stdev(all_male_disease_duration_months)
            all_male_disease_duration_stat[2] = max(all_male_disease_duration_months)
            all_male_disease_duration_stat[3] = min(all_male_disease_duration_months)

            all_female_disease_duration_stat = [0,0,0,0]
            all_female_disease_duration_stat[0] = statistics.mean(all_female_disease_duration_months)
            all_female_disease_duration_stat[1] = statistics.stdev(all_female_disease_duration_months)
            all_female_disease_duration_stat[2] = max(all_female_disease_duration_months)
            all_female_disease_duration_stat[3] = min(all_female_disease_duration_months)

            all_sex_disease_duration_months = (all_female_disease_duration_months + all_male_disease_duration_months)
            all_sex_desease_duration_distribute = [0]*12
            for i in all_sex_disease_duration_months:
                for j in range(12):
                    if (60*j+1) <=  i <= (60*j+60):
                        all_sex_desease_duration_distribute[j] += 1


            all_sex_disease_duration_stat = [0,0,0,0]
            all_sex_disease_duration_stat[0] = statistics.mean((all_sex_disease_duration_months))
            all_sex_disease_duration_stat[1] = statistics.stdev(all_sex_disease_duration_months)
            all_sex_disease_duration_stat[2] = max(all_sex_disease_duration_months)
            all_sex_disease_duration_stat[3] = min(all_sex_disease_duration_months)

            all_male_in_hospital_stat = [0,0,0,0]
            all_male_in_hospital_stat[0] = round(statistics.mean(all_male_in_hospital), 1)
            all_male_in_hospital_stat[1] = round(statistics.stdev(all_male_in_hospital_stat), 1)
            all_male_in_hospital_stat[2] = round(max(all_male_in_hospital), 1)
            all_male_in_hospital_stat[3] = round(min(all_male_in_hospital), 1)

            all_female_in_hospital_stat = [0,0,0,0]
            all_female_in_hospital_stat[0] = round(statistics.mean(all_female_in_hospital), 1)
            all_female_in_hospital_stat[1] = round(statistics.stdev(all_female_in_hospital_stat), 1)
            all_female_in_hospital_stat[2] = round(max(all_female_in_hospital), 1)
            all_female_in_hospital_stat[3] = round(min(all_female_in_hospital), 1)


            all_sex_in_hospital = (all_male_in_hospital + all_female_in_hospital)
            all_sex_in_hospital_distribute = [0]*10
            for i in all_sex_in_hospital:
                for j in range(10):
                    if (5*j+1) <=  i <= (5*j+5):
                        all_sex_in_hospital_distribute[j] += 1

            all_sex_in_hospital_stat = [0,0,0,0]
            all_sex_in_hospital_stat[0] = round(statistics.mean((all_sex_in_hospital)), 1)
            all_sex_in_hospital_stat[1] = round(statistics.stdev(all_sex_in_hospital), 1)
            all_sex_in_hospital_stat[2] = max(all_sex_in_hospital)
            all_sex_in_hospital_stat[3] = min(all_sex_in_hospital)



            return templates.TemplateResponse("analyze/analyze.html", {"request": request, 
                                                                       "all_patient_sex": all_patient_sex, 
                                                                       "all_patient_age": all_patient_age, 
                                                                       "all_patient_age_at_onset": all_patient_age_at_onset, 
                                                                       "all_male_disease_duration_stat": all_male_disease_duration_stat, 
                                                                       "all_female_disease_duration_stat": all_female_disease_duration_stat, 
                                                                       "all_sex_disease_duration_stat": all_sex_disease_duration_stat, 
                                                                       "all_male_disease_duration_months": all_male_disease_duration_months,
                                                                       "all_female_disease_duration_months": all_female_disease_duration_months,
                                                                       "all_sex_desease_duration_distribute": all_sex_desease_duration_distribute, 
                                                                       "all_male_in_hospital_stat": all_male_in_hospital_stat, 
                                                                       "all_female_in_hospital_stat": all_female_in_hospital_stat,
                                                                       "all_sex_in_hospital_distribute": all_sex_in_hospital_distribute, 
                                                                       "all_sex_in_hospital_stat": all_sex_in_hospital_stat,
                                                                       })
        else:
            return templates.TemplateResponse("analyze/analyze.html", {"request": request})
    else:
        return HTMLResponse(status_code=403)
