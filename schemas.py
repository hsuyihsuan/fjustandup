import inspect
from typing import Dict, Type, Optional
from typing import List
from fastapi import File, Form
from pydantic import BaseModel, validator, EmailStr
from datetime import date, datetime
import re


def as_form(cls: Type[BaseModel]):
    """
    Adds an as_form class method to decorated models. The as_form class method
    can be used with FastAPI endpoints
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)), #...代表required一定要有的
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls



@as_form
class PatientCreate(BaseModel):
    PK_PatientID: str
    PatientName: str
    PatientSex: bool
    PatientBirth: date 
    AttackDate: Optional[date]
    BeginSymptom: Optional[int]
    InOtherHospitalDate: Optional[date]
    InOtherHospitalCount: Optional[int]
    PatientKey: Optional[bytes]
    FK_AccountID: int

#     @validator('patientId')
#     def patientIdRule(cls, v):
#         regex = '[0-9]{9}[A-Z]{1}'
#         if re.match(regex, v):
#             return v
#         else:
#             raise ValueError('patientID wrongs')
#     @validator('patientName')
#     def patientNameRule(cls, v):
#         regex = '[0-9]{1,}'
#         if len(v) < 21 and (re.match(regex, v) == None):
#             return v
#         else:
#              raise ValueError('patientName wrongs')


@as_form
class VisitCreate(BaseModel):
    VisitDate: date
    Treat: int
    
    
    Height: float
    Weight: float
    Sbp: Optional[int]
    Dbp: Optional[int]

    Ptosis: bool
    Diplopia: bool
    Dysphasia: bool
    Dysarthria: bool
    Dyspnea: bool
    LimbWeakness: bool

    MGFA_Classification: int

    Pyridostigmine: int
    Compesolone: int
    Cellcept: int
    Imuran: int
    Prograf: int

    SelfAssessment: int
    Note: Optional[str]

    FK_PatientID: str
    FK_AccountID: int


#因為 :List[str]有bug改成以手動方式於crud.py設定, 先暫時註解
# @as_form
# class OtherDiseaseCreate(BaseModel):
#     OtherDiseaseName: str = None
#     FK_VisitID: str = None

@as_form
class ThymusCreate(BaseModel):
    CtDate: Optional[date]
    ThymusStatus: Optional[int]
    ThymusDescription: Optional[str]
    FK_PatientID: Optional[str]
    FK_AccountID: Optional[str]

@as_form
class BloodTestCreate(BaseModel):
    BloodTestDate: Optional[date] 
    AchR: Optional[float]
    TSH: Optional[float] 
    FreeThyroxine: Optional[float] 
    ANA: Optional[int]
    UricAcid: Optional[float]
    FK_PatientID: Optional[str]
    FK_AccountID: Optional[str]


@as_form
class QOLCreate(BaseModel):
    QOL_Date: Optional[date]
    QOL_FrustratedByMG: Optional[int]
    QOL_TroubleUsingEyes:  Optional[int]
    QOL_TroubleEating: Optional[int]
    QOL_LimitedSocialActivity: Optional[int]
    QOL_LimitedHobbyAndFun: Optional[int]
    QOL_TroubleMeetingFamilyNeeds: Optional[int]
    QOL_NeedToMakePlans: Optional[int]
    QOL_NegativeToJob: Optional[int]
    QOL_DifficultSpeaking: Optional[int]
    QOL_TroubleDriving: Optional[int]
    QOL_DepressedAboutMg: Optional[int]
    QOL_TroubleWalking: Optional[int]
    QOL_TroubleGettingAroundPublic: Optional[int]
    QOL_OverWhelmedByMg: Optional[int]
    QOL_TroubleGrooming: Optional[int]
    QOL_Sum: Optional[int]
    FK_PatientID: Optional[str]
    FK_AccountID: Optional[str]

@as_form
class QMGCreate(BaseModel):
    QMG_Date: Optional[date]
    QMG_DoubleVision: Optional[int]
    QMG_Ptosis: Optional[int]
    QMG_FacialMuscle: Optional[int]
    QMG_Swallowing: Optional[int]
    QMG_Speech: Optional[int]
    QMG_RightArm: Optional[int]
    QMG_LeftArm: Optional[int]
    QMG_VitalCapacity: Optional[int]
    QMG_RightHandGrip: Optional[int]
    QMG_LeftHandGrip: Optional[int]
    QMG_HeadLifted: Optional[int]
    QMG_RightLeg: Optional[int]
    QMG_LeftLeg: Optional[int]
    QMG_Sum: Optional[int]
    FK_PatientID: Optional[str]
    FK_AccountID: Optional[str]


@as_form
class MGCompositeCreate(BaseModel):
    MGComposite_Date: Optional[date]
    MGComposite_Ptosis: Optional[int]
    MGComposite_DoubleVision: Optional[int]
    MGComposite_EyeClosure: Optional[int]
    MGComposite_Talking: Optional[int] 
    MGComposite_Chewing: Optional[int]
    MGComposite_Swallowing: Optional[int]
    MGComposite_Breathing: Optional[int]
    MGComposite_NeckFlexion: Optional[int]
    MGCompostie_ShoulderAbduction: Optional[int]
    MGComposite_HipFlexion: Optional[int]
    MGComposite_Sum: Optional[int]
    FK_PatientID: Optional[str]
    FK_AccountID: Optional[str]



@as_form
class ADLCreate(BaseModel):
    ADL_Date: Optional[date]
    ADL_Talking: Optional[int]
    ADL_Chewing: Optional[int]
    ADL_Swallowing: Optional[int]
    ADL_Breathing: Optional[int] 
    ADL_BrushTeethOrCombHair: Optional[int]
    ADL_AriseFromChair: Optional[int]
    ADL_DoubleVision: Optional[int]
    ADL_Eyelid: Optional[int]
    ADL_Sum: Optional[int]
    FK_PatientID: Optional[str]
    FK_AccountID: Optional[str]



@as_form
class LoginCheck(BaseModel):
    AccountName: str
    Password: str

@as_form
class AccountCreate(BaseModel):
    AccountName: str
    Password: str
    Email: str
    Job: str
    UserName: str
    CreateTime: Optional[str]
    UserRole: Optional[str]



#Update

@as_form
class PatientUpdateFromInput(BaseModel):
    PK_PatientID: str
    InOtherHospitalDate: Optional[date]
    InOtherHospitalCount: int
    # Alert: bool

@as_form
class PatientUpdate(BaseModel):
    PK_PatientID: str
    PatientName: str
    PatientSex: int
    PatientBirth: date
    AttackDate: date
    BeginSymptom: int


@as_form
class PatientUpdateFromFirst(BaseModel):
    PK_PatientID: str
    AttackDate: date
    BeginSymptom: int
    InOtherHospitalDate: Optional[date]
    InOtherHospitalCount: Optional[int]
   

@as_form
class BasicVisitUpdate(BaseModel):
    PK_VisitID: int
    Treat: int
    MGFA_Classification: int
    Height: float
    Weight: float
    Sbp: Optional[int]
    Dbp: Optional[int]
    Ptosis: bool
    Diplopia: bool
    Dysphasia: bool
    Dysarthria: bool
    Dyspnea: bool
    LimbWeakness: bool
    FK_PatientID: str

@as_form
class MedicineUpdate(BaseModel):
    PK_VisitID: int
    Pyridostigmine: int
    Compesolone: int
    Cellcept: int
    Imuran: int
    Prograf: int
    FK_PatientID: str

@as_form
class ThymusUpdate(BaseModel):
    PK_CtID: int
    ThymusStatus: int
    ThymusDescription: Optional[str]
    FK_PatientID: str
    

@as_form
class BloodTestUpdate(BaseModel):
    PK_BloodTestID: int
    AchR: Optional[float]
    TSH: Optional[float]
    FreeThyroxine: Optional[float]
    ANA: Optional[float]
    UricAcid: Optional[float]
    FK_PatientID: str
    

@as_form
class QOLTableUpdate(BaseModel):
    PK_QOLTableID: int
    QOL_FrustratedByMG: int
    QOL_TroubleUsingEyes: int
    QOL_TroubleEating: int
    QOL_LimitedSocialActivity: int
    QOL_LimitedHobbyAndFun: int
    QOL_TroubleMeetingFamilyNeeds: int
    QOL_NeedToMakePlans: int
    QOL_NegativeToJob: int
    QOL_DifficultSpeaking: int
    QOL_TroubleDriving: int
    QOL_DepressedAboutMg: int
    QOL_TroubleWalking: int
    QOL_TroubleGettingAroundPublic: int
    QOL_OverWhelmedByMg: int
    QOL_TroubleGrooming: int
    QOL_Sum: int
    FK_PatientID: str



@as_form
class QMGTableUpdate(BaseModel):
    PK_QMGTableID: int

    QMG_DoubleVision: int
    QMG_Ptosis: int
    QMG_FacialMuscle: int
    QMG_Swallowing: int
    QMG_Speech: int
    QMG_RightArm: int
    QMG_LeftArm: int
    QMG_VitalCapacity: int
    QMG_RightHandGrip: int
    QMG_LeftHandGrip: int
    QMG_HeadLifted: int
    QMG_RightLeg: int
    QMG_LeftLeg: int
    QMG_Sum: int
    FK_PatientID: str



@as_form
class MGCompositeTableUpdate(BaseModel):
    PK_MGCompositeTableID: int
    MGComposite_Ptosis: int
    MGComposite_DoubleVision: int
    MGComposite_EyeClosure: int
    MGComposite_Talking: int
    MGComposite_Chewing: int
    MGComposite_Swallowing: int
    MGComposite_Breathing: int
    MGComposite_NeckFlexion: int
    MGCompostie_ShoulderAbduction:int
    MGComposite_HipFlexion: int
    MGComposite_Sum: int
    FK_PatientID: str


@as_form
class ADLTableUpdate(BaseModel):
    PK_ADLTableID: int
    ADL_Talking: int
    ADL_Chewing: int
    ADL_Swallowing: int
    ADL_Breathing: int
    ADL_BrushTeethOrCombHair: int
    ADL_AriseFromChair: int
    ADL_DoubleVision: int
    ADL_Eyelid: int
    ADL_Sum: int
    FK_PatientID: str

@as_form
class SelfAssessmentUpdate(BaseModel):
    PK_VisitID: int
    SelfAssessment: int
    Note: Optional[str]
   
    FK_PatientID: str


@as_form
class AccountUpdate(BaseModel):
    PK_AccountID: int
    # AccountName: str
    # Email: str
    # Job: str
    # UserName: str
    UserRole: Optional[str]

@as_form
class AccountUpdateFromVerify(BaseModel):
    PK_AccountID: int
    AccountName: str
    UserName: str
    Password: str
    UserRole: str


class EmailSchema(BaseModel):
    email: List[EmailStr]

