
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import os


app = FastAPI(
    title="Hospital Staff Scheduling API",
    description="ML API for hospital staff scheduling and overload prediction",
    version="1.0"
)



BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)


patient_model = joblib.load(
    os.path.join(
        MODEL_DIR,
        "best_patient_model.joblib"
    )
)

staff_model = joblib.load(
    os.path.join(
        MODEL_DIR,
        "best_staff_model.joblib"
    )
)

schedule_model = joblib.load(
    os.path.join(
        MODEL_DIR,
        "best_schedule_model.joblib"
    )
)



class PatientInput(BaseModel):

    Primary_Diagnosis: str
    Procedure_Performed: str
    Room_Type: str
    Bed_Days: float
    Supplies_Used: str
    Equipment_Used: str



class StaffInput(BaseModel):

    Staff_Type: str
    Current_Assignment: str
    Hours_Worked: float
    Overtime_Hours: float




class ScheduleInput(BaseModel):

    Department: str
    shift_duration_hours: float
    workdays_per_month: float
    years_of_experience: float
    absenteeism_days: float



class DepartmentStaffing(BaseModel):

    department: str
    required_staff: int
    required_staff_type: str


class StaffMember(BaseModel):

    staff_id: str
    staff_type: str
    current_assignment: str
    hours_worked: float
    overtime_hours: float
    rest_hours: float
    shift_end: str



class StaffingPlanInput(BaseModel):

    departments: list[DepartmentStaffing]
    staff: list[StaffMember]



MAX_HOURS = 14
MAX_OVERTIME = 4
MIN_REST_HOURS = 4


def is_staff_eligible(
    staff,
    target_department,
    required_staff_type
):

    # Staff type must match
    if staff.staff_type != required_staff_type:
        return False

    # Staff must not already be in target department
    if staff.current_assignment == target_department:
        return False

    # Maximum working hours
    if staff.hours_worked >= MAX_HOURS:
        return False

    # Maximum overtime
    if staff.overtime_hours >= MAX_OVERTIME:
        return False

    # Minimum rest requirement
    if staff.rest_hours < MIN_REST_HOURS:
        return False

    return True


@app.get("/")
def home():

    return {
        "message": "Hospital Staff Scheduling API",
        "status": "running"
    }



@app.get("/health")
def health():

    return {
        "status": "healthy",
        "models_loaded": True
    }


@app.post("/predict/patient")
def predict_patient(data: PatientInput):

    input_data = pd.DataFrame([{

        "Primary_Diagnosis":
            data.Primary_Diagnosis,

        "Procedure_Performed":
            data.Procedure_Performed,

        "Room_Type":
            data.Room_Type,

        "Bed_Days":
            data.Bed_Days,

        "Supplies_Used":
            data.Supplies_Used,

        "Equipment_Used":
            data.Equipment_Used

    }])

    prediction = patient_model.predict(
        input_data
    )[0]

    return {
        "predicted_staff_needed":
            round(float(prediction))
    }




@app.post("/predict/staff")
def predict_staff(data: StaffInput):

    input_data = pd.DataFrame([{

        "Staff_Type":
            data.Staff_Type,

        "Current_Assignment":
            data.Current_Assignment,

        "Hours_Worked":
            data.Hours_Worked,

        "Overtime_Hours":
            data.Overtime_Hours

    }])

    prediction = staff_model.predict(
        input_data
    )[0]

    return {
        "predicted_patients_assigned":
            round(float(prediction))
    }


@app.post("/predict/schedule")
def predict_schedule(data: ScheduleInput):

    input_data = pd.DataFrame([{

        "Department":
            data.Department,

        "Shift Duration (Hours)":
            data.shift_duration_hours,

        "Workdays per Month":
            data.workdays_per_month,

        "Years of Experience":
            data.years_of_experience,

        "Absenteeism (Days)":
            data.absenteeism_days

    }])

    prediction = schedule_model.predict(
        input_data
    )[0]

    prediction = int(prediction)

    result = {

        "overload_prediction":
            prediction,

        "status":
            "OVERLOAD"
            if prediction == 1
            else "NORMAL"
    }

    # Return probability if model supports it
    if hasattr(schedule_model, "predict_proba"):

        probability = schedule_model.predict_proba(
            input_data
        )[0][1]

        result["overload_probability"] = round(
            float(probability),
            4
        )

    return result



@app.post("/staffing-plan")
def staffing_plan(data: StaffingPlanInput):

    
    department_staff = {}

    for department in data.departments:

        department_staff[
            department.department
        ] = []


   

    for staff in data.staff:

        if staff.current_assignment in department_staff:

            department_staff[
                staff.current_assignment
            ].append(staff)


   

    department_plan = []

    for department in data.departments:

        available_staff = len(
            department_staff[
                department.department
            ]
        )

        required_staff = department.required_staff

        gap = (
            required_staff
            - available_staff
        )

        if gap > 0:

            status = "SHORTAGE"

        elif gap < 0:

            status = "EXCESS"

        else:

            status = "NORMAL"

        department_plan.append({

            "department":
                department.department,

            "required_staff":
                required_staff,

            "available_staff":
                available_staff,

            "staff_gap":
                gap,

            "status":
                status
        })


    

    shortage_departments = []

    for department in data.departments:

        available_staff = len(
            department_staff[
                department.department
            ]
        )

        shortage = (
            department.required_staff
            - available_staff
        )

        if shortage > 0:

            shortage_departments.append({

                "department":
                    department.department,

                "shortage":
                    shortage,

                "required_staff_type":
                    department.required_staff_type
            })


    
    excess_departments = []

    for department in data.departments:

        available_staff = len(
            department_staff[
                department.department
            ]
        )

        excess = (
            available_staff
            - department.required_staff
        )

        if excess > 0:

            excess_departments.append({

                "department":
                    department.department,

                "excess":
                    excess
            })


    

    reallocation_recommendations = []

    for shortage in shortage_departments:

        target_department = (
            shortage["department"]
        )

        required_staff_type = (
            shortage["required_staff_type"]
        )

        remaining_shortage = (
            shortage["shortage"]
        )

        for excess in excess_departments:

            if remaining_shortage <= 0:
                break

            if excess["excess"] <= 0:
                continue

            source_department = (
                excess["department"]
            )


           
            eligible_staff = []

            for staff in data.staff:

                if (
                    staff.current_assignment
                    != source_department
                ):
                    continue

                if is_staff_eligible(
                    staff,
                    target_department,
                    required_staff_type
                ):

                    eligible_staff.append(staff)


           
            for staff in eligible_staff:

                if remaining_shortage <= 0:
                    break

                if excess["excess"] <= 0:
                    break

                reallocation_recommendations.append({

                    "staff_id":
                        staff.staff_id,

                    "staff_type":
                        staff.staff_type,

                    "from_department":
                        source_department,

                    "to_department":
                        target_department,

                    "hours_worked":
                        staff.hours_worked,

                    "overtime_hours":
                        staff.overtime_hours,

                    "rest_hours":
                        staff.rest_hours,

                    "recommendation":
                        "REALLOCATE"
                })

                remaining_shortage -= 1

                excess["excess"] -= 1


    

    return {

        "department_staffing_plan":
            department_plan,

        "reallocation_recommendations":
            reallocation_recommendations

    }
