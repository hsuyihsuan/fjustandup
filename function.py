from datetime import datetime, timedelta
import secrets, string

#資安相關
from passlib.context import CryptContext #非對稱
from cryptography.fernet import Fernet #對稱



def calculate_date_123_years_ago():
    import datetime
    today = datetime.date.today()
    delta = datetime.timedelta(days=123 * 365) # 120 years = 120 * 365 days
    date_123_years_ago = today - delta
    return date_123_years_ago


def calculate_age(born, today):
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



def days_of_onset(attack_date, today):
    diff = today - attack_date
    years = diff.days // 365
    days = diff.days - years*365

    if years:
        days_of_onset = f"{years} 年 {days}"
        return days_of_onset
    else:
        days_of_onset = days
        return days_of_onset


class CreateTableFields():
    def __init__(self):
        self.qol = ['QOL_FrustratedByMG',
                    'QOL_TroubleUsingEyes',
                    'QOL_TroubleEating',
                    'QOL_LimitedSocialActivity',
                    'QOL_LimitedHobbyAndFun',
                    'QOL_TroubleMeetingFamilyNeeds',
                    'QOL_NeedToMakePlans',
                    'QOL_NegativeToJob',
                    'QOL_DifficultSpeaking',
                    'QOL_TroubleDriving',
                    'QOL_DepressedAboutMg',
                    'QOL_TroubleWalking',
                    'QOL_TroubleGettingAroundPublic',
                    'QOL_OverWhelmedByMg',
                    'QOL_TroubleGrooming'
                    ]

        self.qmg = ['QMG_DoubleVision',
                    'QMG_Ptosis',
                    'QMG_FacialMuscle',
                    'QMG_Swallowing',
                    'QMG_Speech',
                    'QMG_RightArm',
                    'QMG_LeftArm',
                    'QMG_VitalCapacity',
                    'QMG_RightHandGrip',
                    'QMG_LeftHandGrip',
                    'QMG_HeadLifted',
                    'QMG_RightLeg',
                    "QMG_LeftLeg"
                    ]

        self.mg_composite = ['MGComposite_Ptosis',
                             'MGComposite_DoubleVision',
                             'MGComposite_EyeClosure',
                             'MGComposite_Talking',
                             'MGComposite_Chewing',
                             'MGComposite_Swallowing',
                             'MGComposite_Breathing',
                             'MGComposite_NeckFlexion',
                             'MGCompostie_ShoulderAbduction',
                             'MGComposite_HipFlexion'
                             ]

        self.adl = ['ADL_Talking',
                    'ADL_Chewing',
                    'ADL_Swallowing',
                    'ADL_Breathing',
                    'ADL_BrushTeethOrCombHair',
                    'ADL_AriseFromChair',
                    'ADL_DoubleVision',
                    'ADL_Eyelid']

    def create_table_fields(self, table_field, table_object):
        table = dict()

        if table_object:
            for i in table_field:
                for attr, value in table_object.__dict__.items():
                    if i == attr:
                        table[i] = value
        return table


def bmi(height, weight):
    return round(weight / (height/100)**2, 1)


def disease_duration_months(attack_date, today):
    return ((today - attack_date).days // 30)


# router: ai
def in_hospital_count(treat):
    if treat > 0:
        return 1
    else:
        return 0


def is_hyperplasia(thymus_status):
    if thymus_status == 2:
        return 1
    else:
        return 0


def is_thymoma(thymus_status):
    if thymus_status == 3:
        return 1
    else:
        return 0


def create_password():
    letters = string.ascii_letters
    digits = string.digits
    special_chars = string.punctuation

    alphabet = letters + digits + special_chars

    pwd_length = 8

    pwd = ''
    for i in range(pwd_length):
        pwd += ''.join(secrets.choice(alphabet))

    return pwd


def generate_random_url(length: int) -> str:
    alphabet = string.ascii_letters + string.digits
    url = ''.join(secrets.choice(alphabet) for i in range(length))
    return url

def verify_time(create_time):
    now = datetime.now()
    verification_period = timedelta(days=3)
    elapsed_time = now - create_time

    if elapsed_time > verification_period:
        return False
    else:
        return True
    


def count_hospitalized(df, num):
    return (df['Hospitalization'] == num).sum()
    


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)




#從這開始測試加密進資料庫
def gernerate_crypt_key():
    key = Fernet.generate_key()
    f = Fernet(key)
    return (f, key.decode().encode())

def encrypt_data(data: str, key):
    key = Fernet(key)
    return key.encrypt(data.encode())

def decrypt_data(data: bytes, key):
    key = Fernet(key)
    return key.decrypt(data).decode()