from sqlalchemy.orm import Session
import models, schemas, function
from sqlalchemy import func
from datetime import datetime

#二進制查詢
import binascii
# from sqlalchemy import update

#Create

def create_patient(db: Session, patient: schemas.PatientCreate):  
    # if patient.InOtherHospitalDate == None: 
    key = function.gernerate_crypt_key()
    patient.PatientName = function.encrypt_data(patient.PatientName, key[1])
    patient.AttackDate = "0001-01-01"
    patient.BeginSymptom = -1
    patient.InOtherHospitalDate = "0001-01-01" #若沒有輸入外院日期則以0001-01-01記入Patient這個table的欄位InAnotherHospitalDate
    patient.InOtherHospitalCount = 0
    patient.PatientKey = key[1]

    db_patient = models.Patient(**patient.dict()) #取得models.Patient的instance(object)並用**patient.dict()一次將form收集的值賦予instance的atttribue
    db.add(db_patient) #將db_patient這個instance(存入database的session期間)
    db.commit() #確定用sesssion加入此instance的所有attribue

    return 

def create_alert(db: Session, fk_patient_id: str, fk_account_id: int):
    db_alert = models.AlertPatient(FK_PatientID = fk_patient_id, FK_AccountID = fk_account_id)
    db.add(db_alert)
    db.commit()
    return


def create_visit(db: Session, visit: schemas.VisitCreate):        
    
    if visit.Sbp == None: 
        visit.Sbp = -1 #沒有輸入收縮壓則以-1記入Visit這個table的欄位Sbp)
    if visit.Dbp == None:
        visit.Dbp = -1 #沒有輸入舒張壓則以-1記入Visit這個table的欄位Dbp
    if visit.Note == None:
        visit.Note = 'na'

    db_visit = models.Visit(**visit.dict())
    db.add(db_visit)
    db.commit()

    return 

def create_other_disease(db: Session, other_disease):
    for i in other_disease: #可能有多項其他疾病, 以list的方式遍歷
        fk = get_newest_visit_id(db).PK_VisitID #需要取得對應foreignkey
        if i:
            db_other_disease = models.OtherDisease(OtherDiseaseName=i, FK_VisitID=fk)
            db.add(db_other_disease)
            db.commit()
    return

def create_other_medicine(db: Session, other_medicine_name, other_medicine_count):
    for i, j in zip(other_medicine_name, other_medicine_count):
        fk = get_newest_visit_id(db).PK_VisitID #需要取得對應foreignkey
        if i:
            db_other_medicine = models.OtherMedicine(OtherMedicineName=i, OtherMedicineCount=j, FK_VisitID=fk)
            db.add(db_other_medicine)
            db.commit()
    return

def create_thymus(db: Session, thymus: schemas.ThymusCreate, patient_id):
    # thymus.FK_PatientID = get_patient_id(db, patient_id=patient_id).PK_PatientID
    # 若未能實現機器學習則恢復以下註解一對一表示法
    # if thymus.CtDate == None:
    #     thymus.CtDate = "0001-01-01"

    if thymus.CtDate:
        if thymus.ThymusDescription == None:
            thymus.ThymusDescription = "na"

        db_thymus = models.Thymus(**thymus.dict()) #取得models.Patient的instance(object)並用**patient.dict()一次將form收集的值賦予instance的atttribue
        db.add(db_thymus) #將db_patient這個instance(存入database的session期間)
        db.commit() #確定用sesssion加入此instance的所有attribue
        return
    return

def create_blood_test(db: Session, blood_test: schemas.BloodTestCreate, patient_id):
    # blood_test.FK_PatientID = get_patient_id(db, patient_id=patient_id).PK_PatientID

    if blood_test.BloodTestDate: #若要改回一對一則額外設0001-01-01設值
        if blood_test.AchR == None and blood_test.TSH == None and blood_test.TSH == None and blood_test.FreeThyroxine == None and blood_test.ANA == None and blood_test.UricAcid == None:
            return
        if blood_test.AchR == None:
            blood_test.AchR = -1
        if blood_test.TSH == None:
            blood_test.TSH = -1
        if blood_test.FreeThyroxine == None:
            blood_test.FreeThyroxine = -1
        if blood_test.ANA == None:
            blood_test.ANA = -1
        if blood_test.UricAcid == None:
            blood_test.UricAcid = -1

        db_thymus = models.BloodTest(**blood_test.dict()) #取得models.Patient的instance(object)並用**patient.dict()一次將form收集的值賦予instance的atttribue
        db.add(db_thymus) #將db_patient這個instance(存入database的session期間)
        db.commit() #確定用sesssion加入此instance的所有attribue
    return

def create_qol(db: Session, qol: schemas.QOLCreate, patient_id):
    #get_patient_id(db, patient_id).PK_PatientID

    if qol.QOL_Date:
        qol.FK_PatientID =  patient_id
        db_qol = models.QOLTable(**qol.dict())
        db.add(db_qol)
        db.commit()
    
    return

def create_qmg(db: Session, qmg: schemas.QMGCreate, patient_id):
    # qmg.FK_PatientID = get_patient_id(db, patient_id=patient_id).PK_PatientID

    if qmg.QMG_Date:
        qmg.FK_PatientID =  patient_id
        db_qmg = models.QMGTable(**qmg.dict())
        db.add(db_qmg)
        db.commit()

    return

def create_mg_composite(db: Session, mg_composite: schemas.MGCompositeCreate, patient_id):
    # mg_composite.FK_PatientID = get_patient_id(db, patient_id=patient_id).PK_PatientID

    if mg_composite.MGComposite_Date:
        mg_composite.FK_PatientID = patient_id
        db_mg_composite = models.MGCompositeTable(**mg_composite.dict())
        db.add(db_mg_composite)
        db.commit()

    return

def create_adl(db: Session, adl: schemas.ADLCreate, patient_id):
    # adl.FK_PatientID = get_patient_id(db, patient_id=patient_id).PK_PatientID

    if adl.ADL_Date:
        adl.FK_PatientID = patient_id
        db_adl = models.ADLTable(**adl.dict())
        db.add(db_adl)
        db.commit()

    return




def create_account(db: Session, user_name: list, user_email: schemas.EmailSchema, user_job: str):


    for i, j in zip(user_name, user_email):
        account_id = get_newest_account_id(db).PK_AccountID
        account_name= user_job+str(account_id)

        db_account = models.Account(AccountName=account_name, 
                                    Password=function.create_password(), 
                                    Email=j, 
                                    Job=user_job, 
                                    UserName=i, 
                                    CreateTime=datetime.now(), 
                                    UserRole="uncheck", 
                                    RandomURL = str(function.generate_random_url(20)),
                                   
                                    )
        db.add(db_account)
        db.commit()
    return
    
    
def create_ml_model(db: Session, create_time, acc, f1_score, precision, sen, spe, auc, algorithm, fk_account_id):
    db_ml_model = models.MLModel(PK_CreateTime=create_time, Accuracy=acc, F1Score=f1_score, Precision=precision, Sensitivity=sen, Specificity=spe, AUC=auc, Algorithm=algorithm, FK_AccountID=fk_account_id)
    db.add(db_ml_model)
    db.commit()


def create_active_model_for_account(db: Session, fk_create_time: str, fk_account_id: int):
    db_active_model_for_account = models.ActiveMLModel(FK_CreateTime=fk_create_time, FK_AccountID=fk_account_id)
    db.add(db_active_model_for_account)
    db.commit()


def create_active_record(db: Session, record_type: str, patient_id: str, visit_date: str, reason: str, fk_account_id: int, content: str = "None"):
    if record_type == "下載":
        content = "該欄僅屬修改專有" #(patient_id+"_"+visit_date)
    db_active_record = models.ActiveRecord(RecordType=record_type, 
                                           TargetDate = visit_date,
                                           RecordTime=datetime.now(), 
                                           TargetContent=content, 
                                           Reason=reason,
                                           FK_PatientID=patient_id,
                                           FK_AccountID=fk_account_id
                                           )
    db.add(db_active_record)
    db.commit()
    return


#Read
def get_patient_id(db: Session, patient_id: str): #輸入病歷號碼判定初診、複診

    return db.query(models.Patient.PK_PatientID).filter(models.Patient.PK_PatientID == patient_id).first() #SELECT PK_PatientID FROM Patient WHERE PK_PatientID = patient_id
    # patient_id_bytes = function.encrypt_data(patient_id, get_account_key(db, account_id)) #binascii.unhexlify(patient_id.encode())

def get_patient(db: Session, patient_id: str): #確認為複診, 從資料庫叫病歷資料呈現於複診頁面
    return db.query(models.Patient).filter(models.Patient.PK_PatientID == patient_id).first()
    #原定patient_id加密取消
    # patient_id_bytes = function.encrypt_data(patient_id, get_account_key(db, account_id).AccountKey) AES只有解密可用同樣key, 加密每次都不同需要全部調閱比對
    # for i in get_all_patient_id(db):
    #     if function.decrypt_data(i.PK_PatientID, get_account_key(db, account_id)) == patient_id:
    #         return db.query(models.Patient).filter(models.Patient.PK_PatientID == i.PK_PatientID).first() #SELECT * FROM Patient WHERE PK_PatientID = patient_id

def get_all_patient_id(db: Session):
    return db.query(models.Patient.PK_PatientID).all()

def get_patient_newest_patient_id(db: Session):
    return db.query(models.Patient.PK_PatientID).order_by(models.Patient.PK_PatientID.desc()).first()

def get_patient_other_disease_by_visit_date(db: Session, patient_id: str, visit_date: str):
    visit_id = get_patient_visit_id_by_visit_date(db, patient_id, visit_date).PK_VisitID
    return db.query(models.OtherDisease.OtherDiseaseName).filter(models.OtherDisease.FK_VisitID == visit_id).all()

def get_patient_other_medicine_by_visit_date(db: Session, patient_id: str, visit_date: str):
    visit_id = get_patient_visit_id_by_visit_date(db, patient_id, visit_date).PK_VisitID
    return db.query(models.OtherMedicine.OtherMedicineName, models.OtherMedicine.OtherMedicineCount).filter(models.OtherMedicine.FK_VisitID == visit_id).all()


def get_other_disease(db: Session, patient_id: str): #取得上次就診其他疾病
    visit_id = get_newest_visit_id_from_patient_id(db, patient_id).PK_VisitID #先取得該病歷的就診號
    return db.query(models.OtherDisease.PK_OtherDiseaseID, models.OtherDisease.OtherDiseaseName).filter(models.OtherDisease.FK_VisitID == visit_id).all()

def get_other_medicine(db: Session, patient_id: str): #取得上次就診其他用藥
    visit_id = get_newest_visit_id_from_patient_id(db, patient_id).PK_VisitID #先取得該病歷的就診號
    return db.query(models.OtherMedicine.PK_OtherMedicineID, models.OtherMedicine.OtherMedicineName, models.OtherMedicine.OtherMedicineCount).filter(models.OtherMedicine.FK_VisitID == visit_id).all()

def get_newest_in_hospital_date_by_patient_id(db: Session, patient_id:str):
    return db.query(models.Visit.VisitDate).filter((models.Visit.FK_PatientID == patient_id) & (models.Visit.Treat != 0)).order_by(models.Visit.VisitDate.desc()).first()

def get_in_hospital_count(db: Session, patient_id:str):
    return db.query(models.Visit.Treat).filter((models.Visit.FK_PatientID == patient_id) & (models.Visit.Treat != 0)).count()

def get_visit(db: Session, patient_id: str):
    return db.query(models.Visit).filter(models.Visit.FK_PatientID == patient_id).all()

def get_patient_all_thymus(db: Session, patient_id: str):
    return db.query(models.Thymus).filter(models.Thymus.FK_PatientID == patient_id).all()


def get_patient_first_time_thymus_atrophy(db: Session, patient_id: str): #首次胸腺萎縮
    return db.query(models.Thymus.CtDate).filter((models.Thymus.ThymusStatus == 1) & (models.Thymus.FK_PatientID == patient_id)).order_by(models.Thymus.CtDate).first()

def get_patient_first_time_thymus_hyperplasia(db: Session, patient_id: str): #首次胸腺增生
    return db.query(models.Thymus.CtDate).filter((models.Thymus.ThymusStatus == 2) & (models.Thymus.FK_PatientID == patient_id)).order_by(models.Thymus.CtDate).first()

def get_patient_first_time_thymus_thymoma(db: Session, patient_id: str): #首次胸腺瘤
    return db.query(models.Thymus.CtDate).filter((models.Thymus.ThymusStatus == 3) & (models.Thymus.FK_PatientID == patient_id)).order_by(models.Thymus.CtDate).first()

def get_patient_newest_thymus(db: Session, patient_id: str):
    return db.query(models.Thymus).filter(models.Thymus.FK_PatientID == patient_id).order_by(models.Thymus.CtDate.desc()).first()

def get_patient_newest_blood_test(db: Session, patient_id: str):
    return db.query(models.BloodTest).filter(models.BloodTest.FK_PatientID == patient_id).order_by(models.BloodTest.BloodTestDate.desc()).first()

def get_patient_thymus_by_date(db: Session, patient_id: str, ct_date: str):
    return db.query(models.Thymus).filter((models.Thymus.FK_PatientID == patient_id) & (models.Thymus.CtDate == ct_date)).first()

def get_patient_blood_test_by_date(db: Session, patient_id: str, blood_test_date: str):
    return db.query(models.BloodTest).filter((models.BloodTest.FK_PatientID == patient_id) & (models.BloodTest.BloodTestDate == blood_test_date)).first()



def get_patient_all_blood_test(db: Session, patient_id: str):
    return db.query(models.BloodTest).filter(models.BloodTest.FK_PatientID == patient_id).all()

def get_patient_newest_qol(db: Session, patient_id: str):
    return db.query(models.QOLTable).filter(models.QOLTable.FK_PatientID == patient_id).order_by(models.QOLTable.QOL_Date.desc()).first()

def get_patient_newest_qmg(db: Session, patient_id: str):
    return db.query(models.QMGTable).filter(models.QMGTable.FK_PatientID == patient_id).order_by(models.QMGTable.QMG_Date.desc()).first()

def get_patient_newest_adl(db: Session, patient_id: str):
    return db.query(models.ADLTable).filter(models.ADLTable.FK_PatientID == patient_id).order_by(models.ADLTable.ADL_Date.desc()).first()


def get_patient_all_qol_date(db: Session, patient_id: str):
    return db.query(models.QOLTable.QOL_Date).filter(models.QOLTable.FK_PatientID == patient_id).order_by(models.QOLTable.QOL_Date.desc()).all()

def get_patient_all_qmg_date(db: Session, patient_id: str):
    return db.query(models.QMGTable.QMG_Date).filter(models.QMGTable.FK_PatientID == patient_id).order_by(models.QMGTable.QMG_Date.desc()).all()

def get_patient_all_mg_composite_date(db: Session, patient_id: str):
    return db.query(models.MGCompositeTable.MGComposite_Date).filter(models.MGCompositeTable.FK_PatientID == patient_id).order_by(models.MGCompositeTable.MGComposite_Date.desc()).all()

def get_patient_all_adl_date(db: Session, patient_id: str):
    return db.query(models.ADLTable.ADL_Date).filter(models.ADLTable.FK_PatientID == patient_id).order_by(models.ADLTable.ADL_Date.desc()).all()

def get_patient_newest_mg_composite(db: Session, patient_id: str):
    return db.query(models.MGCompositeTable).filter(models.MGCompositeTable.FK_PatientID == patient_id).order_by(models.MGCompositeTable.MGComposite_Date.desc()).first()

def get_patient_qol_by_date(db: Session, patient_id: str, qol_date: str):
    return db.query(models.QOLTable).filter((models.QOLTable.FK_PatientID == patient_id) & (models.QOLTable.QOL_Date == qol_date)).first()

def get_patient_qmg_by_date(db: Session, patient_id: str, qmg_date: str):
    return db.query(models.QMGTable).filter((models.QMGTable.FK_PatientID == patient_id) & (models.QMGTable.QMG_Date == qmg_date)).first()

def get_patient_mg_composite_by_date(db: Session, patient_id: str, mg_composite_date: str):
    return db.query(models.MGCompositeTable).filter((models.MGCompositeTable.FK_PatientID == patient_id) & (models.MGCompositeTable.MGComposite_Date == mg_composite_date)).first()

def get_patient_adl_by_date(db: Session, patient_id: str, adl_date: str):
    return db.query(models.ADLTable).filter((models.ADLTable.FK_PatientID == patient_id) & (models.ADLTable.ADL_Date == adl_date)).first()

def get_patient_newest_adl(db: Session, patient_id: str):
    return db.query(models.ADLTable).filter(models.ADLTable.FK_PatientID == patient_id).order_by(models.ADLTable.ADL_Date.desc()).first()


def get_visit_count(db: Session, patient_id: str):
    return db.query(models.Visit.PK_VisitID).filter(models.Visit.FK_PatientID == patient_id).count()

def get_patient_newest_visit(db: Session, patient_id: str):  #確認為複診, 從資料庫叫就診資料呈現於複診頁面
    return db.query(models.Visit).order_by(models.Visit.VisitDate.desc()).filter(models.Visit.FK_PatientID == patient_id).first() #SELECT * FROM Visit WHERE FK_PatientID = patient_id ORDER BY PK_VisitID DESC

def get_newest_visit_id(db: Session):
    return db.query(models.Visit.PK_VisitID).order_by(models.Visit.PK_VisitID.desc()).first()

def get_patient_visit_id_by_visit_date(db: Session, patient_id: str, visit_date: str):
    return db.query(models.Visit.PK_VisitID).join(models.Patient).filter((models.Patient.PK_PatientID == patient_id) & (models.Visit.VisitDate == visit_date)).first()
# def get_newest_blood_test(db: Session, patient_id: str): #現無需求, 暫時註解以備不時之需
#     return db.query(models.BloodTest).order_by(models.Visit.PK_VisitID.desc()).filter((models.Visit.FK_PatientID == patient_id) & (models.BloodTest.FK_VisitID == models.Visit.PK_VisitID)).first()

def get_newest_visit_id_from_patient_id(db: Session, patient_id: str):
    return db.query(models.Visit.PK_VisitID).order_by(models.Visit.PK_VisitID.desc()).filter(models.Visit.FK_PatientID == patient_id).first()

def get_patient_newest_visit_date(db: Session, patient_id: str):  #確認為複診, 從資料庫叫就診資料呈現於複診頁面
    return db.query(models.Visit.VisitDate).order_by(models.Visit.PK_VisitID.desc()).filter(models.Visit.FK_PatientID == patient_id).first() #SELECT * FROM Visit WHERE FK_PatientID = patient_id ORDER BY PK_VisitID DESC

def get_patient_visit_by_date(db: Session, patient_id: str, visit_date: str):
    return db.query(models.Visit).order_by(models.Visit.VisitDate.desc()).filter((models.Visit.FK_PatientID == patient_id) & (models.Visit.VisitDate == visit_date)).first()


def get_all_visit_date_by_patient_id(db: Session, patient_id: str):
    return db.query(models.Visit.VisitDate).filter(models.Visit.FK_PatientID == patient_id).order_by(models.Visit.VisitDate).all()

# def get_seven_newest_visit_date_height_weight(db: Session, patient_id:str):
#     return db.query(models.Visit).filter(models.Visit.FK_PatientID == patient_id).order_by(models.Visit.VisitDate.desc()).limit(7).all()

def get_account_id_and_user_role_that_match_login_data(db: Session, login_data: schemas.LoginCheck):
    return db.query(models.Account.PK_AccountID, models.Account.UserRole).filter((models.Account.AccountName == login_data.AccountName) & (models.Account.UserRole != "uncheck")).first()

def get_account_hashed_password(db: Session, account_name: str):
    return db.query(models.Account.Password).filter(models.Account.AccountName == account_name).first()

def get_all_account(db: Session):
    return db.query(models.Account).all()


def get_patient_and_his_visit_for_manage_page(db: Session, account_id: str):
    # subquery = db.query(func.max(models.Visit.VisitDate)).filter((models.Visit.FK_PatientID == models.Patient.PK_PatientID)).group_by(models.Patient.PK_PatientID).all()
    return db.query(models.Patient, func.count(models.Visit.VisitDate), func.max(models.Visit.VisitDate)).filter((models.Visit.FK_PatientID == models.Patient.PK_PatientID) & (models.Visit.FK_AccountID == account_id)).group_by(models.Patient).all() #models.Patient.PatientName, models.Patient.PatientBirth, models.Visit.SelfAssessment,

def get_patient_all_visit(db: Session, patient_id: str):
    return db.query(models.Visit).filter(models.Visit.FK_PatientID == patient_id).order_by(models.Visit.VisitDate).all()

def get_patient_all_qol(db: Session, patient_id: str):
    return db.query(models.QOLTable).filter(models.QOLTable.FK_PatientID == patient_id).order_by(models.QOLTable.QOL_Date).all()

def get_patient_all_qmg(db: Session, patient_id: str):
    return db.query(models.QMGTable).filter(models.QMGTable.FK_PatientID == patient_id).order_by(models.QMGTable.QMG_Date).all()

def get_patient_all_mg_composite(db: Session, patient_id: str):
    return db.query(models.MGCompositeTable).filter(models.MGCompositeTable.FK_PatientID == patient_id).order_by(models.MGCompositeTable.MGComposite_Date).all()

def get_patient_all_adl(db: Session, patient_id: str):
    return db.query(models.ADLTable).filter(models.ADLTable.FK_PatientID == patient_id).order_by(models.ADLTable.ADL_Date).all()

def get_account_by_id(db: Session, account_id: str):
    return db.query(models.Account).filter(models.Account.PK_AccountID == account_id).first()

def get_account_by_name(db: Session, account_name: str):
    return db.query(models.Account).filter(models.Account.AccountName == account_name).first()

def get_all_ml_model(db: Session):
    return db.query(models.MLModel).all()


def get_rebuild_data_by_pk_create_time(db: Session, pk_create_time: str):
    return db.query(models.RebuildData).filter(models.RebuildData.FK_CreateTime == pk_create_time).all()


def get_all_rebuild_data_count(db: Session):
    return db.query(func.count(models.RebuildData.FK_CreateTime)).group_by(models.RebuildData.FK_CreateTime).all()


def get_all_ml_model_count(db: Session):
    return db.query(models.MLModel).count()

# def get_model_which_is_activate(db: Session):
#     return db.query(models.MLModel.PK_CreateTime).filter(models.MLModel.Activate == 1).first()


def get_all_patient(db: Session):
    return db.query(models.Patient).all()

def get_visit_input_account(db: Session, visit_id: int, account_id: int):
    return db.query(models.Account.UserName).join(models.Visit, models.Account.PK_AccountID == models.Visit.FK_AccountID).filter((models.Visit.PK_VisitID == visit_id) & (models.Visit.FK_AccountID == account_id)).first()


def get_newest_account_id(db: Session):
    return db.query(models.Account.PK_AccountID).order_by(models.Account.PK_AccountID.desc()).first()

def get_account_name_and_password_and_random_url(db: Session, email: str):
    return db.query(models.Account.AccountName, models.Account.Password, models.Account.RandomURL).filter(models.Account.Email == email).first()

def get_account_by_random_url(db: Session, random_url: str):
    return db.query(models.Account).filter(models.Account.RandomURL == random_url).first()


def get_patient_key(db: Session, patient_id: int):
    return db.query(models.Patient.PatientKey).filter(models.Patient.PK_PatientID == patient_id).first().PatientKey

def get_all_account_id_and_username_from_doctor(db: Session):
    return db.query(models.Account.PK_AccountID, models.Account.UserName).filter(models.Account.UserRole == "doctor").all()

def get_account_user_name_by_account_id(db: Session, account_id: int):
    return db.query(models.Account.UserName).filter(models.Account.PK_AccountID == account_id).first()


def check_if_email_repeat(db: Session, email: str):
    return db.query(models.Account.PK_AccountID).filter(models.Account.Email == email).first()

def check_if_patient_first_time(db: Session, patient_id: str):
    return db.query(models.Visit.PK_VisitID).filter(models.Visit.FK_PatientID == patient_id).first()

def check_if_doctor_is_patient_first_time(db: Session, patient_id: str, account_id: str):
    return db.query(models.Patient).filter((models.Patient.PK_PatientID == patient_id) & (models.Patient.FK_AccountID == account_id)).first()

def get_alert_if_exist(db: Session, patient_id: str, account_id: str):
    return db.query(models.AlertPatient).filter((models.AlertPatient.FK_PatientID == patient_id) & (models.AlertPatient.FK_AccountID == account_id)).first()

def get_active_model_if_exist(db: Session, fk_account_id: int):
    return db.query(models.ActiveMLModel).filter((models.ActiveMLModel.FK_AccountID == fk_account_id)).first()

def get_all_activity(db: Session):
    return db.query(models.ActiveRecord, models.Account.UserName).filter(models.ActiveRecord.FK_AccountID == models.Account.PK_AccountID).all()

def get_activity_reason_by_id(db: Session, active_record_id: int):
    return db.query(models.ActiveRecord.Reason).filter(models.ActiveRecord.PK_ActiveRecordID == active_record_id).first()

# 
#  def get_visit_date(db: Session, patient_id: str, visit_date: str):
#       return db.query(models.Visit.VisitDate).order_by(models.Visit.PK_VisitID.desc()).filter(models.Visit.FK_PatientID == patient_id and models.Visit.VisitDate == visit_date).first()
# downloadcsv區域
#病人姓名
def get_patient_name(db: Session, patient_id: str):
    return db.query(models.Patient.PatientName).filter(models.Patient.PK_PatientID == patient_id).first()
#病人身高
def get_height(db: Session, patient_id: str, visit_date: str):
    return db.query(models.Visit.Height).filter((models.Visit.FK_PatientID == patient_id) & (models.Visit.VisitDate == visit_date)).first()
#病人體重
def get_weight(db: Session, patient_id: str, visit_date: str):
    return db.query(models.Visit.Weight).filter((models.Visit.FK_PatientID == patient_id) & (models.Visit.VisitDate == visit_date)).first()
#病人性別
def get_patient_sex(db: Session, patient_id: str):
    return db.query(models.Patient.PatientSex).filter(models.Patient.PK_PatientID == patient_id).first()
#大力丸數量
def get_Pyridostigmine(db: Session, patient_id: str, visit_date: str):
    return db.query(models.Visit.Pyridostigmine).filter((models.Visit.FK_PatientID == patient_id) & (models.Visit.VisitDate == visit_date)).first()
#類固醇數量
def get_Compesolone(db: Session, patient_id: str, visit_date: str):
    return db.query(models.Visit.Compesolone).filter((models.Visit.FK_PatientID == patient_id) & (models.Visit.VisitDate == visit_date)).first()
#目前有哪些肌無力症狀
def count_symptoms(db: Session, patient_id: str, visit_date: str):
    symptoms_count=0
    if  db.query(models.Visit.Diplopia).filter((models.Visit.FK_PatientID == patient_id) & (models.Visit.VisitDate == visit_date)).first():
        symptoms_count+=1
    if db.query(models.Visit.Ptosis).filter((models.Visit.FK_PatientID == patient_id) & (models.Visit.VisitDate == visit_date)).first():
        symptoms_count+=1
    if db.query(models.Visit.Dysphasia).filter((models.Visit.FK_PatientID == patient_id) & (models.Visit.VisitDate == visit_date)).first():
        symptoms_count+=1
    if db.query(models.Visit.Dysarthria).filter((models.Visit.FK_PatientID == patient_id) & (models.Visit.VisitDate == visit_date)).first():
        symptoms_count+=1
    if db.query(models.Visit.Dyspnea).filter((models.Visit.FK_PatientID == patient_id) & (models.Visit.VisitDate == visit_date)).first():
        symptoms_count+=1
    return symptoms_count
#曾經發現胸腺異常
def get_patient_thymus_abnormalornot(db: Session, patient_id: str):
    times = db.query(models.Thymus.PK_CtID).filter(models.Thymus.FK_PatientID == patient_id).count()
    status = ""
    if(times > 0):
        status = "有胸腺異常"
    else:
        status = "無胸腺異常"
    return status 
#嘗試用物件導向指定Column, 後來發現容易造成效能問題而以註解保留程式碼
    # multiple_fields = ()

    # def get_multiple_columns(object_data):
    #     for i in list(object_data.__dict__)[3:12]:
    #         field = models.Visit.i
    #         multiple_fields + (models.Visit.field, )
    #     return multiple_fields

    # class GetWantedField():
    #     def parse(cls, data):
    #         for i in list(data.__dict__)[3:12]:
    #             setattr(cls, i, getattr(data, i))

    # def delete_default(self):
    #     for i in self.__dict__:
    #         delattr(self, i)
    #     return

    # wanted_visit = GetWantedField()
    # delete_default(wanted_visit)
    # wanted_visit.parse(models.Visit)


#update

def update_patient_from_input(db: Session, update_field: schemas.PatientUpdateFromInput):
    if update_field.InOtherHospitalDate == None: 
        update_field.InOtherHospitalDate = "0001-01-01" #若沒有輸入外院日期則以0001-01-01記入Patient這個table的欄位InAnotherHospitalDate

    db.merge(models.Patient(**update_field.dict())) #UPDATE Patient SET InAnotherHospitalDate = 'InAnotherHospitalDate', InAnotherHospitalCount = InAnotherHospitalCount WHERE PK_PatientID = 'PK_PatientID'   #merge為高階技術 可參考 https://www.essentialsql.com/difference-merge-update/ 只求效率可看下面註解的update
    db.commit()
    return

def update_patient(db: Session, update_field: schemas.PatientUpdate):
    db.merge(models.Patient(**update_field.dict())) #UPDATE Patient SET InAnotherHospitalDate = 'InAnotherHospitalDate', InAnotherHospitalCount = InAnotherHospitalCount WHERE PK_PatientID = 'PK_PatientID'   #merge為高階技術 可參考 https://www.essentialsql.com/difference-merge-update/ 只求效率可看下面註解的update
    db.commit()
    return

def update_patient_from_first(db: Session, update_field: schemas.PatientUpdate):

    if update_field.InOtherHospitalDate == None:
        update_field.InOtherHospitalDate = "0001-01-01"
        update_field.InOtherHospitalCount = 0

    db.merge(models.Patient(**update_field.dict()))
    return

def update_basic_visit(db: Session, update_field: schemas.BasicVisitUpdate):
    if update_field.Sbp == None:
        update_field.Sbp = -1
    if update_field.Dbp == None:
        update_field.Dbp = -1
    db.merge(models.Visit(**update_field.dict()))
    db.commit()
    return

def update_medicine(db: Session, update_field: schemas.MedicineUpdate):
    db.merge(models.Visit(**update_field.dict()))
    db.commit()
    return

def update_thymus(db: Session, update_field: schemas.ThymusUpdate):
    if update_field.ThymusDescription == None:
        update_field.ThymusDescription = "na"
    db.merge(models.Thymus(**update_field.dict()))
    db.commit()
    return

def update_blood_test(db: Session, update_field: schemas.BloodTestUpdate):
    if update_field.AchR == None:
        update_field.AchR = -1
    if update_field.TSH == None:
        update_field.TSH = -1
    if update_field.FreeThyroxine == None:
        update_field.FreeThyroxine = -1
    if update_field.ANA == None:
        update_field.ANA = -1
    if update_field.UricAcid == None:
        update_field.UricAcid = -1

    db.merge(models.BloodTest(**update_field.dict()))
    db.commit()
    return

def update_qol(db: Session, update_field: schemas.QOLTableUpdate):
    db.merge(models.QOLTable(**update_field.dict()))
    db.commit()
    return

def update_qmg(db: Session, update_field: schemas.QMGTableUpdate):
    db.merge(models.QMGTable(**update_field.dict()))
    db.commit()
    return

def update_mg_composite(db: Session, update_field: schemas.MGCompositeTableUpdate):
    db.merge(models.MGCompositeTable(**update_field.dict()))
    db.commit()
    return

def update_adl(db: Session, update_field: schemas.ADLTableUpdate):
    db.merge(models.ADLTable(**update_field.dict()))
    db.commit()
    return


def update_self_assessment(db: Session, update_field: schemas.SelfAssessmentUpdate):
    if update_field.Note == None:
        update_field.Note = "na"

    db.merge(models.Visit(**update_field.dict()))
    db.commit()
    return


def update_account(db: Session, update_field: schemas.AccountUpdate):
    db.merge(models.Account(**update_field.dict()))
    db.commit()
    return


def update_account_from_verify(db: Session, update_field: schemas.AccountUpdateFromVerify):
    db.merge(models.Account(**update_field.dict()))
    db.commit()
    return




def update_all_ml_model_to_off(db: Session):
    all_model = get_all_ml_model(db)
    for i in all_model:
        i.Activate = 0
   
    db.commit()
    return

def update_ml_model_by_choose(db: Session, pk_create_time: str):
   
    target_model = db.query(models.MLModel).filter(models.MLModel.PK_CreateTime == pk_create_time).first()
    target_model.Activate = 1
    db.commit()
    return

def update_patient_alert(db: Session, patient_id: str):
   
    patient = db.query(models.Patient).filter(models.Patient.PK_PatientID == patient_id).first()
    patient.Alert = not patient.Alert
    db.commit()
    return


#原本的update物件作法, 發現用merge更簡潔而暫時保留註解
    # db_patient = db.query(models.Patient).filter(models.Patient.PK_PatientID == patient_id).first()
    # db_patient.InAnotherHospitalDate = update_field.InAnotherHospitalDate
    # db_patient.InAnotherHospitalCount = update_field.InAnotherHospitalCount
    # db.query(models.Patient).filter(models.Patient.PK_PatientID == patient_id).update(**update_field.dict())
    # db.commit()


#Delete

def delete_other_disease_by_id(db: Session, other_disease_id):
    db.query(models.OtherDisease).filter(models.OtherDisease.PK_OtherDiseaseID == other_disease_id).delete()
    db.commit()
    return

def delete_account(db: Session, account_id):
    db.query(models.Account).filter(models.Account.PK_AccountID == account_id).delete()
    db.commit()
    return

def delete_alert(db: Session, fk_patient_id: str, fk_account_id: int):
    db.query(models.AlertPatient).filter((models.AlertPatient.FK_PatientID == fk_patient_id) & (models.AlertPatient.FK_AccountID == fk_account_id)).delete()
    db.commit()
    return


def delete_active_model_for_account(db: Session):
    db.query(models.ActiveMLModel).delete()
    db.commit()
    return

def delete_model_by_choose(db: Session, pk_create_time: str):
    db.query(models.RebuildData).filter(models.RebuildData.FK_CreateTime == pk_create_time).delete()
    db.commit()
    db.query(models.MLModel).filter(models.MLModel.PK_CreateTime == pk_create_time).delete()
    db.commit()
    return