from pydantic import BaseModel, EmailStr, AnyUrl, Field, field_validator, model_validator, computed_field
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):

    name: Annotated[str,Field(max_length=50, title='Name of the patient',description='-_-_-_-_-_-',examples=['Nitish','Laksh'])]
    email: EmailStr
    url: AnyUrl
    age: int = Field(gt=0,lt=120)
    weight: Annotated[float,Field(gt=0,strict=True)]
    height: Annotated[float,Field(gt=0,strict=True)]
    married: Annotated[bool,Field(default=None,description='-_-_-_-_-')]
    allergies: Annotated[Optional[List[str]],Field(default=None,max_length=5)]
    contact_details: Dict[str,str]

    @field_validator('email')
    @classmethod
    def email_validator(cls,value):
        email_passes =['hdfc.com','icici.com']
        passe = value.split('@')[-1]
        if passe not in email_passes:
            raise ValueError('Not a valid domain')
        else: return value

    @field_validator('name')
    @classmethod
    def uppername(cls,value):
        return value.upper()
    
    @model_validator(mode='after')
    def validate_emergency_no(cls,model):
        if model.age > 60 and 'emergency' not in model.contact_details:
            raise ValueError('')
        return model
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height**2),2)
        return bmi
    
    
def insert_patient(patient: Patient):
    print(patient.name)
    print(patient.age)
    print(patient.email)
    print(patient.url)
    print(patient.weight)
    print(patient.married)
    print(patient.allergies)

patient_info = {'name':'exampleName','age': 20,'email':'example@icici.com','url':'https://www.example.com/', 'weight': 60.5, 'married': False, 'allergies': ['pollen', 'nuts']}
p1 = Patient(**patient_info)
insert_patient(p1)
