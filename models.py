from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mssql import CHAR, VARCHAR, BIT, DATE, SMALLINT, TINYINT, INTEGER, DATETIME2, REAL, BINARY, VARBINARY
from database import Base
from sqlalchemy.orm import relationship


class Patient(Base):
    __tablename__ = "Patient"

    # 病歷號碼作為PK, index=True代表可用來查詢(加速用)
    PK_PatientID = Column(CHAR(10), primary_key=True, index=True)
    # 病歷姓名, nullable=False代表不可為空值
    PatientName = Column(BINARY(140), nullable=False)
    PatientSex = Column(BIT, nullable=False)  # 性別, 0=女性、1=男性
    PatientBirth = Column(DATE, nullable=False)  # 生日
    AttackDate = Column(DATE, nullable=False)  # 肌無力發生日
    BeginSymptom = Column(SMALLINT, nullable=False)  # 初始症狀
    InOtherHospitalDate = Column(DATE, nullable=False)  # 最近外院住院日期
    InOtherHospitalCount = Column(SMALLINT, nullable=False)  # 外院住院總次數
    PatientKey = Column(VARBINARY(64), nullable=False)  # 二進制密鑰, 可用來加解密病歷資料

    # Alert = Column(BIT, nullable=False) #是否將病歷加入關注名單

    visit = relationship("Visit", back_populates="patient")
    thymus = relationship("Thymus", back_populates="patient")
    blood_test = relationship("BloodTest", back_populates="patient")
    qol_table = relationship("QOLTable", back_populates="patient")
    qmg_table = relationship("QMGTable", back_populates="patient")
    active_record = relationship("ActiveRecord", back_populates="patient")
    mg_composite_table = relationship(
        "MGCompositeTable", back_populates="patient")
    adl_table = relationship("ADLTable", back_populates="patient")

    FK_AccountID = Column(INTEGER, ForeignKey(
        "Account.PK_AccountID"), nullable=False)
    account = relationship("Account", back_populates="patient")

    alert_patient = relationship("AlertPatient", back_populates="patient")


class Visit(Base):
    __tablename__ = "Visit"

    PK_VisitID = Column(INTEGER, primary_key=True,
                        autoincrement=True, index=True)  # 就診流水號
    VisitDate = Column(DATE, nullable=False)  # 就診日期(存儲時間是為方便排序, 一天可能有許多病歷輸入)
    Treat = Column(TINYINT, nullable=False)  # 住院治療方式

    Height = Column(REAL, nullable=False)  # 身高
    Weight = Column(REAL, nullable=False)  # 體重
    Sbp = Column(SMALLINT, nullable=False)  # 收縮壓
    Dbp = Column(SMALLINT, nullable=False)  # 舒張壓

    Ptosis = Column(BIT, nullable=False)  # 是否眼瞼下垂
    Diplopia = Column(BIT, nullable=False)  # 是否複視
    Dysphasia = Column(BIT, nullable=False)  # 是否吞嚥困難
    Dysarthria = Column(BIT, nullable=False)  # 是否講話不清
    Dyspnea = Column(BIT, nullable=False)  # 是否呼吸困難
    LimbWeakness = Column(BIT, nullable=False)  # 是否手腳無力

    MGFA_Classification = Column(TINYINT, nullable=False)  # MGFA協會對該疾病分類

    Pyridostigmine = Column(TINYINT, nullable=False)  # 大力丸用藥量
    Compesolone = Column(TINYINT, nullable=False)  # 類固醇用藥量
    Cellcept = Column(TINYINT, nullable=False)  # 山喜多用藥量
    Imuran = Column(TINYINT, nullable=False)  # 移護寧用藥量
    Prograf = Column(TINYINT, nullable=False)  # 普洛可富用藥量

    SelfAssessment = Column(TINYINT, nullable=False)  # 自覺嚴重程度 0=輕度 1=中度 2=重度
    Note = Column(VARCHAR(100), nullable=False)  # 附註

    FK_PatientID = Column(CHAR(10), ForeignKey("Patient.PK_PatientID"), nullable=False)
    FK_AccountID = Column(INTEGER, ForeignKey("Account.PK_AccountID"), nullable=False)

    patient = relationship("Patient", back_populates="visit")
    account = relationship("Account", back_populates="visit")

    other_disease = relationship("OtherDisease", back_populates="visit")
    other_medicine = relationship("OtherMedicine", back_populates="visit")

    # 若需一對一才取消註解
    # thymus = relationship("Thymus", back_populates="visit")
    # blood_test = relationship("BloodTest", back_populates="visit")


#     selfEffect = Column(TINYINT, nullable=False) #自覺治療成效
#     note = Column(NVARCHAR(30), nullable=False) #註記


# #從這開始處理一對多關係

class OtherDisease(Base):
    __tablename__ = "OtherDisease"

    PK_OtherDiseaseID = Column(
        INTEGER, primary_key=True, autoincrement=True, index=True)
    OtherDiseaseName = Column(VARCHAR(40), nullable=False)

    FK_VisitID = Column(INTEGER, ForeignKey(
        "Visit.PK_VisitID"), nullable=False)
    visit = relationship("Visit", back_populates="other_disease")


class OtherMedicine(Base):
    __tablename__ = "OtherMedicine"

    PK_OtherMedicineID = Column(
        INTEGER, primary_key=True, autoincrement=True, index=True)
    OtherMedicineName = Column(VARCHAR(40))
    OtherMedicineCount = Column(TINYINT, nullable=False)

    FK_VisitID = Column(INTEGER, ForeignKey(
        "Visit.PK_VisitID"), nullable=False)
    visit = relationship("Visit", back_populates="other_medicine")


class Thymus(Base):
    __tablename__ = "Thymus"

    PK_CtID = Column(INTEGER, primary_key=True,
                     autoincrement=True, index=True)  # 胸腺斷層掃描流水號
    CtDate = Column(DATE, nullable=False)  # 胸腺斷層掃描日期
    # 胸腺斷層掃描結果 -1:本次就診未收集 0:正常 1:胸腺萎縮 2:胸腺增生 3:胸腺瘤
    ThymusStatus = Column(TINYINT, nullable=False)
    ThymusDescription = Column(VARCHAR(30), nullable=False)

    FK_PatientID = Column(CHAR(10), ForeignKey(
        "Patient.PK_PatientID"), nullable=False)
    patient = relationship("Patient", back_populates="thymus")

    FK_AccountID = Column(INTEGER, ForeignKey(
        "Account.PK_AccountID"), nullable=False)
    account = relationship("Account", back_populates="thymus")

    # 若需要一對一才開此table連結
    # FK_VisitID = Column(INTEGER, ForeignKey("Visit.PK_VisitID"))
    # visit = relationship("Visit", back_populates="thymus")


class BloodTest(Base):
    __tablename__ = "BloodTest"

    PK_BloodTestID = Column(INTEGER, primary_key=True,
                            autoincrement=True, index=True)  # 抗體抽血流水號
    BloodTestDate = Column(DATE, nullable=False)  # 抗體抽血日期
    AchR = Column(REAL, nullable=False)  # AchR抗體
    TSH = Column(REAL, nullable=False)  # 甲狀腺刺激素
    FreeThyroxine = Column(REAL, nullable=False)  # 游離甲狀腺素
    ANA = Column(SMALLINT, nullable=False)  # 抗核抗體
    UricAcid = Column(REAL, nullable=False)  # 尿酸

    FK_PatientID = Column(CHAR(10), ForeignKey("Patient.PK_PatientID"), nullable=False)
    patient = relationship("Patient", back_populates="blood_test")

    FK_AccountID = Column(INTEGER, ForeignKey("Account.PK_AccountID"), nullable=False)
    account = relationship("Account", back_populates="blood_test")
    
    # 若需要一對一才開此table連結
    # FK_VisitID = Column(INTEGER, ForeignKey("Visit.PK_VisitID"))
    # visit = relationship("Visit", back_populates="blood_test")


class QOLTable(Base):
    __tablename__ = "QOLTable"

    PK_QOLTableID = Column(INTEGER, primary_key=True,
                           autoincrement=True, index=True)
    QOL_Date = Column(DATE, nullable=False)
    QOL_FrustratedByMG = Column(TINYINT, nullable=False)
    QOL_TroubleUsingEyes = Column(TINYINT, nullable=False)
    QOL_TroubleEating = Column(TINYINT, nullable=False)
    QOL_LimitedSocialActivity = Column(TINYINT, nullable=False)
    QOL_LimitedHobbyAndFun = Column(TINYINT, nullable=False)
    QOL_TroubleMeetingFamilyNeeds = Column(TINYINT, nullable=False)
    QOL_NeedToMakePlans = Column(TINYINT, nullable=False)
    QOL_NegativeToJob = Column(TINYINT, nullable=False)
    QOL_DifficultSpeaking = Column(TINYINT, nullable=False)
    QOL_TroubleDriving = Column(TINYINT, nullable=False)
    QOL_DepressedAboutMg = Column(TINYINT, nullable=False)
    QOL_TroubleWalking = Column(TINYINT, nullable=False)
    QOL_TroubleGettingAroundPublic = Column(TINYINT, nullable=False)
    QOL_OverWhelmedByMg = Column(TINYINT, nullable=False)
    QOL_TroubleGrooming = Column(TINYINT, nullable=False)
    QOL_Sum = Column(TINYINT, nullable=False)

    FK_PatientID = Column(CHAR(10), ForeignKey("Patient.PK_PatientID"), nullable=False)
    patient = relationship("Patient", back_populates="qol_table")

    FK_AccountID = Column(INTEGER, ForeignKey("Account.PK_AccountID"), nullable=False)
    account = relationship("Account", back_populates="qol_table")


class QMGTable(Base):
    __tablename__ = "QMGTable"

    PK_QMGTableID = Column(INTEGER, primary_key=True,
                           autoincrement=True, index=True)
    QMG_Date = Column(DATE, nullable=False)
    QMG_DoubleVision = Column(TINYINT, nullable=False)
    QMG_Ptosis = Column(TINYINT, nullable=False)
    QMG_FacialMuscle = Column(TINYINT, nullable=False)
    QMG_Swallowing = Column(TINYINT, nullable=False)
    QMG_Speech = Column(TINYINT, nullable=False)
    QMG_RightArm = Column(TINYINT, nullable=False)
    QMG_LeftArm = Column(TINYINT, nullable=False)
    QMG_VitalCapacity = Column(TINYINT, nullable=False)
    QMG_RightHandGrip = Column(TINYINT, nullable=False)
    QMG_LeftHandGrip = Column(TINYINT, nullable=False)
    QMG_HeadLifted = Column(TINYINT, nullable=False)
    QMG_RightLeg = Column(TINYINT, nullable=False)
    QMG_LeftLeg = Column(TINYINT, nullable=False)
    QMG_Sum = Column(TINYINT, nullable=False)

    FK_PatientID = Column(CHAR(10), ForeignKey("Patient.PK_PatientID"), nullable=False)
    patient = relationship("Patient", back_populates="qmg_table")

    FK_AccountID = Column(INTEGER, ForeignKey("Account.PK_AccountID"), nullable=False)
    account = relationship("Account", back_populates="qmg_table")


class MGCompositeTable(Base):
    __tablename__ = "MGCompositeTable"

    PK_MGCompositeTableID = Column(INTEGER, primary_key=True, autoincrement=True, index=True)
    MGComposite_Date = Column(DATE, nullable=False)
    MGComposite_Ptosis = Column(TINYINT, nullable=False)
    MGComposite_DoubleVision = Column(TINYINT, nullable=False)
    MGComposite_EyeClosure = Column(TINYINT, nullable=False)
    MGComposite_Talking = Column(TINYINT, nullable=False)
    MGComposite_Chewing = Column(TINYINT, nullable=False)
    MGComposite_Swallowing = Column(TINYINT, nullable=False)
    MGComposite_Breathing = Column(TINYINT, nullable=False)
    MGComposite_NeckFlexion = Column(TINYINT, nullable=False)
    MGCompostie_ShoulderAbduction = Column(TINYINT, nullable=False)
    MGComposite_HipFlexion = Column(TINYINT, nullable=False)
    MGComposite_Sum = Column(TINYINT, nullable=False)

    FK_PatientID = Column(CHAR(10), ForeignKey("Patient.PK_PatientID"))
    patient = relationship("Patient", back_populates="mg_composite_table")

    FK_AccountID = Column(INTEGER, ForeignKey("Account.PK_AccountID"), nullable=False)
    account = relationship("Account", back_populates="mg_composite_table")


class ADLTable(Base):
    __tablename__ = "ADLTable"

    PK_ADLTableID = Column(INTEGER, primary_key=True,
                           autoincrement=True, index=True)
    ADL_Date = Column(DATE, nullable=False)
    ADL_Talking = Column(TINYINT, nullable=False)
    ADL_Chewing = Column(TINYINT, nullable=False)
    ADL_Swallowing = Column(TINYINT, nullable=False)
    ADL_Breathing = Column(TINYINT, nullable=False)
    ADL_BrushTeethOrCombHair = Column(TINYINT, nullable=False)
    ADL_AriseFromChair = Column(TINYINT, nullable=False)
    ADL_DoubleVision = Column(TINYINT, nullable=False)
    ADL_Eyelid = Column(TINYINT, nullable=False)
    ADL_Sum = Column(TINYINT, nullable=False)

    FK_PatientID = Column(CHAR(10), ForeignKey("Patient.PK_PatientID"))
    patient = relationship("Patient", back_populates="adl_table")

    FK_AccountID = Column(INTEGER, ForeignKey("Account.PK_AccountID"), nullable=False)
    account = relationship("Account", back_populates="adl_table")


# 編撰自妍
class Account(Base):
    __tablename__ = "Account"

    PK_AccountID = Column(INTEGER, primary_key=True,autoincrement=True, index=True)  # 帳號流水號
    AccountName = Column(VARCHAR(30), nullable=False) # 帳號名稱, nullable=False代表不可為空值
    Password = Column(VARCHAR(60), nullable=False)  # 帳號密碼
    Email = Column(VARCHAR(40), nullable=False)  # 使用者電子信箱
    Job = Column(VARCHAR(20), nullable=False)  # 使用者職稱電子信箱
    UserName = Column(VARCHAR(35), nullable=False)  # 使用者姓名
    CreateTime = Column(DATETIME2, nullable=False)  # 帳號創建時間
    UserRole = Column(VARCHAR(7), nullable=False) # 權限設置: clerk=醫院行政, doctor=醫師, uncheck=待審, close=停用
    RandomURL = Column(CHAR(20), nullable=False)  # 驗證url, 亦為修改url

    visit = relationship("Visit", back_populates="account")
    patient = relationship("Patient", back_populates="account")
    thymus = relationship("Thymus", back_populates="account")
    blood_test = relationship("BloodTest", back_populates="account")
    qol_table = relationship("QOLTable", back_populates="account")
    qmg_table = relationship("QMGTable", back_populates="account")
    mg_composite_table = relationship("MGCompositeTable", back_populates="account")
    adl_table = relationship("ADLTable", back_populates="account")
    ml_model = relationship("MLModel", back_populates="account")
    alert_patient = relationship("AlertPatient", back_populates="account")
    active_ml_model = relationship("ActiveMLModel", back_populates="account")
    active_record = relationship("ActiveRecord", back_populates="account")

class RebuildData(Base):
    __tablename__ = "RebuildData"

    PK_RebuildDataID = Column(INTEGER, primary_key=True, autoincrement=True, index=True)
    PatientSex = Column(BIT, nullable=False)  # 性別, 0=女性、1=男性
    MGFA_Classification = Column(TINYINT, nullable=False)  # MGFA協會對該疾病分類
    Ptosis = Column(BIT, nullable=False)  # 是否眼瞼下垂
    Diplopia = Column(BIT, nullable=False)  # 是否複視
    Dysphasia = Column(BIT, nullable=False)  # 是否吞嚥困難
    Dysarthria = Column(BIT, nullable=False)  # 是否講話不清
    Dyspnea = Column(BIT, nullable=False)  # 是否呼吸困難
    LimbWeakness = Column(BIT, nullable=False)  # 是否手腳無力
    Pyridostigmine = Column(TINYINT, nullable=False)  # 大力丸用藥量
    Compesolone = Column(TINYINT, nullable=False)  # 類固醇用藥量
    DiseaseDurationMonths = Column(INTEGER, nullable=False)
    AgeAtOnset = Column(TINYINT, nullable=False)
    InHospitalCount = Column(INTEGER, nullable=False)
    Hyperplasia = Column(BIT, nullable=False)  # 是否胸腺增生
    Thymoma = Column(BIT, nullable=False)  # 是否胸腺瘤
    Hospitalization = Column(BIT, nullable=False)  # 是否因惡化住院

    FK_CreateTime = Column(CHAR(19), ForeignKey("MLModel.PK_CreateTime"), nullable=False)
    ml_model = relationship("MLModel", back_populates="rebuild")


class MLModel(Base):
    __tablename__ = "MLModel"

    PK_CreateTime = Column(CHAR(19), primary_key=True, nullable=False)  # 創建時間

    Accuracy = Column(REAL, nullable=False)
    F1Score = Column(REAL, nullable=False)
    Precision = Column(REAL, nullable=False)
    Sensitivity = Column(REAL, nullable=False)
    Specificity = Column(REAL, nullable=False)
    AUC = Column(REAL, nullable=False)
    Algorithm = Column(VARCHAR(35), nullable=False)  # 建模時選用演算法

    FK_AccountID = Column(INTEGER, ForeignKey("Account.PK_AccountID"), nullable=False)
    account = relationship("Account", back_populates="ml_model")
    rebuild = relationship("RebuildData", back_populates="ml_model")
    active_ml_model = relationship("ActiveMLModel", back_populates="ml_model")


class ActiveMLModel(Base):
    __tablename__ = "ActiveMLModel"

    PK_ActiveMLModelID = Column(INTEGER, primary_key=True, autoincrement=True, index=True)

    FK_CreateTime = Column(CHAR(19), ForeignKey("MLModel.PK_CreateTime"), nullable=False)
    FK_AccountID = Column(INTEGER, ForeignKey("Account.PK_AccountID"), nullable=False)

    ml_model = relationship("MLModel", back_populates="active_ml_model")
    account = relationship("Account", back_populates="active_ml_model")

class AlertPatient(Base):
    __tablename__ = "AlertPatient"

    PK_AlertPatientID = Column(INTEGER, primary_key=True, autoincrement=True, index=True)
    FK_PatientID = Column(CHAR(10), ForeignKey("Patient.PK_PatientID"), nullable=False)
    FK_AccountID = Column(INTEGER, ForeignKey("Account.PK_AccountID"), nullable=False)

    patient = relationship("Patient", back_populates="alert_patient")
    account = relationship("Account", back_populates="alert_patient")

class ActiveRecord(Base):
    __tablename__ = "ActiveRecord"

    PK_ActiveRecordID = Column(INTEGER, primary_key=True, autoincrement=True, index=True)
    RecordTime = Column(DATETIME2, nullable=False) 
    RecordType = Column(VARCHAR(10), nullable=False)
    TargetDate = Column(DATE, nullable=False)
    TargetContent = Column(VARCHAR(35), nullable=False)
    Reason = Column(VARCHAR(60), nullable=False)

    FK_PatientID = Column(CHAR(10), ForeignKey("Patient.PK_PatientID"), nullable=False)
    FK_AccountID = Column(INTEGER, ForeignKey("Account.PK_AccountID"), nullable=False)

    patient = relationship("Patient", back_populates="active_record")
    account = relationship("Account", back_populates="active_record")
