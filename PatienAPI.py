from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field 
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(...,description='ID of the patient',examples=['P001'])]
    name: Annotated[str, Field(...,description='Name of the patient')]
    city: Annotated[str, Field(...,description='City where the patient is living')]
    age: Annotated[int, Field(...,gt=0,lt=150,description='Age of the patient')]
    gender: Annotated[Literal['male','female','others'], Field(...,description='Gender of the patient')]
    height: Annotated[float, Field(...,gt=0,description='Height of the patient')]
    weight: Annotated[float, Field(...,gt=0,description='Weight of the patient')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5 : return 'Underweight'
        elif self.bmi > 18.5 and self.bmi < 30: return 'Normal'
        else: return 'Obese'
    
class UpdatePatient(BaseModel):
    
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(gt=0,lt=150,default=None)]
    gender: Annotated[Optional[Literal['male','female','others']], Field(default=None)]
    height: Annotated[Optional[float], Field(gt=0,default=None)]
    weight: Annotated[Optional[float], Field(gt=0,default=None)]


# function to load data from json file

def load_data():
    with open("patients.json", "r") as file:
        data = json.load(file)
    return data

def save_data(data):
    with open('patients.json','w') as file:
        json.dump(data,file)


@app.get("/")
def welcome():
    return {"message": "Welcome"}
#shows data of all patients

@app.get("/view")
def view():
    data = load_data()
    return data
#end-point to display data of patient using its patient-id

@app.get("/patient/{patient_id}") # path parameter
def view_patient(patient_id: str = Path(..., description="The ID of the patient to view",examples=['P001'])):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    else : raise HTTPException(status_code=404, detail="Patient not found")
#end-point to display sorted data of patient. eg: sort-by -> height,weight,bmi and also order -> asc,desc

@app.get("/sort") # query parameter
def sort_patients(sort_by: str = Query(...,description='sort data by height,weight,bmi'),order:str = Query('asc',description='asc or dec')):
    value_fields = ['height','weight','bmi']
    if sort_by not in value_fields:
        raise HTTPException(status_code=400,detail='error, not found')
    
    if order not in ['asc','dec']:
        raise HTTPException(status_code=400,detail='error, invalid input')
    
    data = load_data()
    sort_order = True if order=='dec' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by,0),reverse=sort_order)
    return sorted_data

@app.post('/create')
def create_new_patient(patient:Patient):
    
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=409,detail='Patient alreay exist')
    
    data[patient.id] = patient.model_dump(exclude={'id'})

    save_data(data)

    return JSONResponse(status_code=201,content={'meassage': 'Patient created successfully'})

@app.put('/edit/{patient_id}')
def update_patient_details(patient_id:str,updatePatient:UpdatePatient):
    
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = updatePatient.model_dump(exclude_unset=True)

    for key,value in updated_patient_info.items():
        existing_patient_info[key] = value
        
    existing_patient_info['id'] = patient_id  # Ensure the ID remains the same
    patient_pydantic_object = Patient(**existing_patient_info)
    existing_patient_info = patient_pydantic_object.model_dump(exclude={'id'})

    data[patient_id] = existing_patient_info

    save_data(data)

    return JSONResponse(status_code=200,content={'message': 'Patient details updated successfully'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200,content={'message': 'Patient deleted successfully'})


#