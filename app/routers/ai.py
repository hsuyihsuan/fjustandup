from fastapi import Request, Depends, HTTPException, Header, Form
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from sqlalchemy.orm import Session

import sqlalchemy as sa
import pandas as pd
import shap
import crud, function, schemas
from datetime import date
from database import SessionLocal, engine

# 作業系統修改thread, 以及plt_close可以關掉緩衝檔避免重疊圖
import matplotlib.pyplot as plt
plt.switch_backend('agg')

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import KFold
from sklearn.linear_model import LogisticRegression


# Functions for evaluation
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import confusion_matrix
# from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.metrics import RocCurveDisplay
import pickle

import os



# 為能前後端分離, 將前端介面存在templates資料夾裡供使用, jinja2是知名樣板(template)處理器
templates = Jinja2Templates(directory="templates")

router = APIRouter()


def get_db():  # 給予資料庫session啟用
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#因難以從function.py連接而特別獨立的function
today = date.today()
def calculate_age_while_today_is_sure(born, today=today):
    try:
        birthday = born.replace(year=today.year)
        # raised when birth date is February 29 and the current year is not a leap year
    except ValueError:
         birthday = born.replace(year=today.year,
                                    month=born.month + 1, day=1)

    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year


@router.get("/aiControl", response_class=HTMLResponse, tags=["ai"])
async def ai_control_page(
    request: Request,
):
    session_now = request.session.get("user_role", None)
    if session_now == "doctor":
        return templates.TemplateResponse("/ai/aiControl.html", {"request": request})
    else:
        return HTMLResponse(status_code=403)


@router.get("/aiManage", response_class=HTMLResponse, tags=["ai"])
async def ai_manage_page(
    request: Request,
    success: Optional[int] = None,
    db: Session = Depends(get_db)
):
    account_id = request.session['account_id']
    rebuild_data_count = crud.get_all_rebuild_data_count(db)
    ml_model = crud.get_all_ml_model(db)
    active_model = crud.get_active_model_if_exist(db, request.session['account_id'])
    return templates.TemplateResponse("/ai/aiManage.html", {"request": request, "ml_model": list(zip(ml_model, rebuild_data_count)), "active_model": active_model, "account_id": account_id, "success": success})


@router.get("/watchRebuildData/{pk_create_time}", response_class=HTMLResponse, tags=["ai"])
async def watch_rebuild_data(
    request: Request,
    pk_create_time: str,
    db: Session = Depends(get_db)
):
    rebuild_data = crud.get_rebuild_data_by_pk_create_time(db, pk_create_time)

    all_patient_sex = [0, 0]
    all_mgfa = [0]*8
    all_symptom = ['現有症狀']+[0]*6
    all_medicine = ['用藥頻率']+[0]*2
    all_disease_duraion_month = []
    all_age_at_onset = []
    all_in_hospital_count = []
    all_ct_and_hospitalizaion = ['重要指標']+[0]*3

    for i in rebuild_data:
        if i.PatientSex:
            all_patient_sex[0] += 1
        else:
            all_patient_sex[1] += 1
        
        all_mgfa[i.MGFA_Classification] += 1

        if i.Ptosis:
            all_symptom[1] += 1
        if i.Diplopia:
            all_symptom[2] += 1
        if i.Dysphasia:
            all_symptom[3] += 1
        if i.Dysarthria:
            all_symptom[4] += 1
        if i.Dyspnea:
            all_symptom[5] += 1
        if i.LimbWeakness:
            all_symptom[6] += 1

        if i.Pyridostigmine:
            all_medicine[1] += 1
        if i.Compesolone:
            all_medicine[2] += 1

        all_disease_duraion_month.append(i.DiseaseDurationMonths)
        all_age_at_onset.append(i.AgeAtOnset)
        all_in_hospital_count.append(i.InHospitalCount)

        if i.Hyperplasia:
            all_ct_and_hospitalizaion[1] += 1
        if i.Thymoma:
            all_ct_and_hospitalizaion[2] += 1
        if i.Hospitalization:
            all_ct_and_hospitalizaion[3] += 1






    return templates.TemplateResponse("/ai/oneRebuildData.html", {"request": request, 
                                                                  "rebuild_data": rebuild_data, 
                                                                  "all_patient_sex": all_patient_sex, 
                                                                  "all_mgfa": all_mgfa, 
                                                                  "all_symptom": all_symptom,
                                                                  "all_medicine": all_medicine,
                                                                  "all_disease_duration_months": all_disease_duraion_month, 
                                                                  "all_age_at_onset": all_age_at_onset,
                                                                  "all_in_hospital_count": all_in_hospital_count,
                                                                  "all_ct_and_hospitalizaion": all_ct_and_hospitalizaion,
                                                                  "create_time": pk_create_time
                                                                  })


@router.get("/watchChart/{pk_create_time}", response_class=HTMLResponse, tags=["ai"])
async def watch_rebuild_data_picture(
    request: Request,
    pk_create_time: str,
):
    cm_url = "ai/img/"+pk_create_time+"-confusion_matrix.png"
    roc_url = "ai/img/"+pk_create_time+"-roc.png"
    return templates.TemplateResponse("/ai/oneEvaluationChart.html", {"request": request, "cm_url": cm_url, "roc_url": roc_url})


@router.get("/changeModel/{pk_create_time}", response_class=HTMLResponse, tags=["ai"])
async def change_model(
    request: Request,
    pk_create_time: str,
    db: Session = Depends(get_db)
):
    account_id = request.session['account_id']
    if crud.get_active_model_if_exist(db, account_id):
        crud.delete_active_model_for_account(db)
        crud.create_active_model_for_account(db, pk_create_time, account_id)
    else:
        crud.create_active_model_for_account(db, pk_create_time, account_id)
    
    # crud.update_all_ml_model_to_off(db)
    # crud.update_ml_model_by_choose(db, pk_create_time)

    return

@router.get("/deleteModel/{pk_create_time}", response_class=HTMLResponse, tags=["ai"])
async def delete_model(
    request: Request,
    pk_create_time: str,
    db: Session = Depends(get_db)
):
    
    modeL_url = "C:/Users/careaboutyou/Desktop/standup_develop/ai/model/"+pk_create_time+".model"
    cm_url = "C:/Users/careaboutyou/Desktop/standup_develop/ai/img/" + \
        pk_create_time+"-confusion_matrix.png"
    roc_url = "C:/Users/careaboutyou/Desktop/standup_develop/ai/img/"+pk_create_time+"-roc.png"
    os.remove(modeL_url)
    os.remove(cm_url)
    os.remove(roc_url)
    crud.delete_model_by_choose(db, pk_create_time)
    
    # crud.update_all_ml_model_to_off(db)
    # crud.update_ml_model_by_choose(db, pk_create_time)
    return


@router.get("/rebuild", response_class=HTMLResponse, tags=["ai"])
async def rebuild_page(
    request: Request,
    dataTooLess: Optional[int] = None
):
    with engine.begin() as conn:
        df = pd.read_sql_query(sa.text("SELECT v.VisitDate, t.CtDate, p.PK_PatientID, p.PatientBirth, p.PatientSex, p.AttackDate, v.MGFA_Classification, v.Ptosis, v.Diplopia, v.Dysphasia, v.Dysarthria, v.Dyspnea, v.LimbWeakness, v.Pyridostigmine, v.Compesolone, t.ThymusStatus, p.InOtherHospitalCount, v.Treat FROM Patient p INNER JOIN Visit v ON p.PK_PatientID = v.FK_PatientID INNER JOIN Thymus t ON p.PK_PatientID = t.FK_PatientID"), conn)

    if len(df) > 9:
        def disease_duration(attack_date):
            return (pd.to_datetime('today').to_period('M') - pd.to_datetime(attack_date).to_period('M')).n

      
        df['DiseaseDurationMonths'] = df['AttackDate'].apply(disease_duration)
        
        df['AgeAtOnset'] = df.apply((lambda x: function.calculate_age(x['PatientBirth'], x['AttackDate'])), axis=1)
        df['Age'] = df['PatientBirth'].apply(calculate_age_while_today_is_sure)

        df = df.drop('AttackDate', axis=1)

        df['InHospitalCount'] = df['Treat'].apply(function.in_hospital_count)
        df['InHospitalCount'] = df['InHospitalCount'] + df['InOtherHospitalCount']

        df = df.drop('InOtherHospitalCount', axis=1)
        df = df.sort_values('VisitDate').groupby('PK_PatientID').tail(1)
        df = df.sort_values('CtDate').groupby('PK_PatientID').tail(1)


        df['Hyperplasia'] = df['ThymusStatus'].apply(function.is_hyperplasia)
        df['Thymoma'] = df['ThymusStatus'].apply(function.is_thymoma)

        def whether_stay_hospital(treat):
            if treat > 0:
                return 1
            else:
                return 0

        df['Hospitalization'] = df['Treat'].apply(whether_stay_hospital)

        df = df.drop(['PK_PatientID', 'PatientBirth', 'VisitDate', 'CtDate', 'Treat', 'Age', 'ThymusStatus'], axis=1)

        from datetime import datetime
        now = datetime.today()
        conn.close()

        
        
        if function.count_hospitalized(df, 1) > 1 and function.count_hospitalized(df, 0) > 1:
            return templates.TemplateResponse("/ai/rebuild.html", {"request": request, "df": df, "now":  now, "fk_account_id": request.session['account_id'], "dataTooLess": dataTooLess})
        else:
            return  templates.TemplateResponse("/ai/rebuild.html", {"request": request, "not_enough": 1, "df": None})
    else:
        return  templates.TemplateResponse("/ai/rebuild.html", {"request": request, "not_enough": 1, "df": None})


@router.post("/rebuild", response_class=HTMLResponse, tags=["ai"])
async def rebuild(
    algorithm = Form(),
    # check: List[int] = Form(default=None),
    FK_AccountID = Form(),
    db: Session = Depends(get_db)
):
    # if check == None or len(check) < 10:
    #     return RedirectResponse("/rebuild?dataTooLess=1", status_code=303)
    # else:

        with engine.begin() as conn: #使pandas連上sql server
            df = pd.read_sql_query(sa.text("SELECT v.VisitDate, t.CtDate, p.PK_PatientID, p.PatientName, p.PatientBirth, p.PatientSex, p.AttackDate, v.MGFA_Classification, v.Ptosis, v.Diplopia, v.Dysphasia, v.Dysarthria, v.Dyspnea, v.LimbWeakness, v.Pyridostigmine, v.Compesolone, t.ThymusStatus, p.InOtherHospitalCount, v.Treat FROM Patient p INNER JOIN Visit v ON p.PK_PatientID = v.FK_PatientID INNER JOIN Thymus t ON p.PK_PatientID = t.FK_PatientID"), conn)

        # df = df[df.index.isin(check)]

        if len(df) < 10:
              return RedirectResponse("/rebuild?dataTooLess=1", status_code=303)
        
        else:


            today = date.today()

        

            def disease_duration(attack_date):
                return (pd.to_datetime('today').to_period('M') - pd.to_datetime(attack_date).to_period('M')).n

            df['DiseaseDurationMonths'] = df['AttackDate'].apply(disease_duration)
            df['AgeAtOnset'] = df.apply(lambda x: function.calculate_age(
                x['PatientBirth'], x['AttackDate']), axis=1)
            df['Age'] = df['PatientBirth'].apply(calculate_age_while_today_is_sure)

            df = df.drop('AttackDate', axis=1)


            df['InHospitalCount'] = df['Treat'].apply(function.in_hospital_count)
            df['InHospitalCount'] = df['InHospitalCount'] + df['InOtherHospitalCount']

            df = df.drop('InOtherHospitalCount', axis=1)
            df = df.sort_values('VisitDate').groupby('PK_PatientID').tail(1)
            df = df.sort_values('CtDate').groupby('PK_PatientID').tail(1)


            df['Hyperplasia'] = df['ThymusStatus'].apply(function.is_hyperplasia)
            df['Thymoma'] = df['ThymusStatus'].apply(function.is_thymoma)

            def whether_stay_hospital(treat):
                if treat > 0:
                    return 1
                else:
                    return 0

            df['Hospitalization'] = df['Treat'].apply(whether_stay_hospital)

            if function.count_hospitalized(df, 1) < 3 or function.count_hospitalized(df, 0) < 3:
                return RedirectResponse("/rebuild?dataTooLess=1", status_code=303)

            df = df.drop(['PK_PatientID', 'PatientBirth', 'VisitDate', 'CtDate',
                        'PatientName', 'Treat', 'Age', 'ThymusStatus'], axis=1)

            x = df.drop('Hospitalization', axis=1).values

            feature = df.drop('Hospitalization', axis=1).columns
            y = df['Hospitalization'].values

            test = 0
            state = 4
            while test == 0:
                x_train, x_test, y_train, y_test = train_test_split(
                    x, y, test_size=0.2, random_state=state)
                for i in y_test:
                    if i == 1:
                        # test = 1
                        for j in y_test:
                            if j == 0:
                                test = 1
                                break
                    elif test == 1:
                        break
                print(test)
                state += 1

            if algorithm == "CART":
                model = DecisionTreeClassifier(criterion='gini', random_state=4) #0511重新確認
            # elif algorithm == "Logistic":
            #     model = LogisticRegression()  
            

            model.fit(x_train, y_train)
            # CV5F_cart_acc = cross_val_score(
            #     model, x_train, y_train, cv=5, scoring='accuracy')

            testing_prediction = model.predict(x_test)
            testing_acc = round(accuracy_score(y_test, testing_prediction)*100, 2)
            testing_f1s = round(
                f1_score(y_test, testing_prediction, pos_label=1)*100, 2)
            testing_pre = round(precision_score(
                y_test, testing_prediction, pos_label=1)*100, 2)
            testing_sen = round(recall_score(
                y_test, testing_prediction, pos_label=1)*100, 2)
            testing_spe = round(recall_score(
                y_test, testing_prediction, pos_label=0)*100, 2)

            proba = model.predict_proba(x_test)[:, 1]

            try:
                auc_value = roc_auc_score(y_test, proba)
            except:
                pass

            from datetime import datetime

            now = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")

            testing_cm = confusion_matrix(y_test, testing_prediction)
            # disp = ConfusionMatrixDisplay(confusion_matrix=testing_cm, display_labels=model.classes_)
            cm_disp = ConfusionMatrixDisplay.from_estimator(
                model,
                x_test,
                y_test,
                display_labels=model.classes_,
                cmap=plt.cm.Blues,
                #         normalize=normalize,
            )
            url = "C:/Users/careaboutyou/Desktop/standup_develop/ai/img/" + \
                now+"-confusion_matrix.png"

            # test = str(disp.__dict__)
            cm_disp.figure_.savefig(url)
            plt.close()
            # fig = RocCurveDisplay.from_predictions(y_test, testing_prediction)

            roc_disp = RocCurveDisplay.from_estimator(model, x_test, y_test)
            url = "C:/Users/careaboutyou/Desktop/standup_develop/ai/img/"+now+"-roc.png"
            roc_disp.figure_.savefig(url)
            plt.close()

            filename = "C:/Users/careaboutyou/Desktop/standup_develop/ai/model/"+now+".model"

            pickle.dump(model, open(filename, 'wb'))

            crud.create_ml_model(db, now, testing_acc, testing_f1s,
                                testing_pre, testing_sen, testing_spe, auc_value, algorithm, FK_AccountID)

            df['FK_CreateTime'] = now
            df.to_sql('RebuildData', con=engine, if_exists='append', index=False)

            conn.close()
            plt.close()

            return RedirectResponse("/aiManage?success=1", status_code=303)


@router.get("/aiSupport/{patient_id}", response_class=HTMLResponse, tags=["ai"])
def displayshap(
    request: Request,
    patient_id: str,
    db: Session = Depends(get_db)
):
    with engine.begin() as conn:
        sql = "SELECT v.VisitDate, t.CtDate, p.PK_PatientID, p.PatientName, p.PatientBirth, p.PatientSex, p.AttackDate, v.MGFA_Classification, v.Ptosis, v.Diplopia, v.Dysphasia, v.Dysarthria, v.Dyspnea, v.LimbWeakness, v.Pyridostigmine, v.Compesolone, t.ThymusStatus, p.InOtherHospitalCount, v.Treat FROM Patient p INNER JOIN Visit v ON p.PK_PatientID = v.FK_PatientID INNER JOIN Thymus t ON p.PK_PatientID = t.FK_PatientID WHERE p.PK_PatientID = '"+patient_id+"'"

        df = pd.read_sql_query(sa.text(sql), conn)


    def disease_duration(attack_date):
        return (pd.to_datetime('today').to_period('M') - pd.to_datetime(attack_date).to_period('M')).n

    df['DurationMonths'] = df['AttackDate'].apply(disease_duration)
    df['AgeAtOnset'] = df.apply(lambda x: function.calculate_age(
        x['PatientBirth'], x['AttackDate']), axis=1)
    df['Age'] = df['PatientBirth'].apply(calculate_age_while_today_is_sure)

    df = df.drop('AttackDate', axis=1)

 
    df['InHospitalCount'] = df['Treat'].apply(function.in_hospital_count)
    df['InHospitalCount'] = df['InHospitalCount'] + df['InOtherHospitalCount']

    df = df.drop('InOtherHospitalCount', axis=1)
    df = df.sort_values('VisitDate').groupby('PK_PatientID').tail(1)
    df = df.sort_values('CtDate').groupby('PK_PatientID').tail(1)


    df['Hyperplasia'] = df['ThymusStatus'].apply(function.is_hyperplasia)
    df['Thymoma'] = df['ThymusStatus'].apply(function.is_thymoma)

    def whether_stay_hospital(treat):
        if treat > 0:
            return 1
        else:
            return 0

    df['Hospitalization'] = df['Treat'].apply(whether_stay_hospital)

    df = df.drop(['PK_PatientID', 'PatientBirth', 'VisitDate', 'CtDate',
                 'PatientName', 'Treat', 'Age', 'ThymusStatus'], axis=1)

    def convert_to_int(col):
        if col == 1:
            return 1
        else:
            return 0

    df['PatientSex'] = df['PatientSex'].apply(convert_to_int)
    df['Ptosis'] = df['Ptosis'].apply(convert_to_int)
    df['Diplopia'] = df['Diplopia'].apply(convert_to_int)
    df['Dysarthria'] = df['Dysarthria'].apply(convert_to_int)
    df['Dyspnea'] = df['Dyspnea'].apply(convert_to_int)
    df['LimbWeakness'] = df['LimbWeakness'].apply(convert_to_int)
    df['Dysphasia'] = df['Dysphasia'].apply(convert_to_int)
    df.rename(columns={'MGFA_Classification': 'MGFA'}, inplace=True)

    x = df.drop('Hospitalization', axis=1).values

    feature = df.drop('Hospitalization', axis=1).columns
    url = crud.get_active_model_if_exist(db, request.session['account_id']).FK_CreateTime

    url = "C:/Users/careaboutyou/Desktop/standup_develop/ai/model/"+url+".model"
   
    model = pickle.load(open(url, 'rb'))


   

    explainer = shap.TreeExplainer(model)
    
    shap_values = explainer.shap_values(x)

    risk = model.predict([x[0]])

    if risk > 0:
        expect = explainer.expected_value[1]
        shap_values = shap_values[1][0]

    else:
        expect = explainer.expected_value[1]
        shap_values = shap_values[1][0]




    fig = shap.waterfall_plot(shap.Explanation(values=shap_values, base_values=expect, data=x[0], feature_names=feature), max_display=7, show=False)

    url = "C:/Users/careaboutyou/Desktop/standup_develop/ai/shap/shap.png"
    fig.set_size_inches(18, 10)
    fig.savefig(url, dpi=300) #dpi=300

    plt.close()

    # get_shap = "/ai/shap/shap.png"
    conn.close()

    # fig.flush()
    # fig.close()

    # print(shap_values[1])
    return templates.TemplateResponse('ai/shap.html', {"request": request, "risk": risk}) #"get_shap": get_shap
