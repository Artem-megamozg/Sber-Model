import requests
import json
import tkinter as tk
from tkinter import messagebox, simpledialog

# URL GraphQL server
url = "https://smapi.pv-api.sbc.space/ds-7429590172239724545/graphql"

def graphql_query(query, variables=None):
    # Function to execute GraphQL queries
    try:
        json_data = {
            'query': query,
            'variables': variables or {}
        }

        response = requests.post(url, json=json_data)

        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                print(f"GraphQL Errors: {result['errors']}")
                return None
            return result.get('data')
        else:
            print(f"HTTP Error {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None

def load_data():
    # Load data from JSON file
    with open('results.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def create_appointment(clinic_id, clinic_doctor_id, begin_date, end_date, clinic_office_id, customer_id):
    mutation = """
    mutation createClinicTable(
      $clinicId: ID!,
      $clinicDoctorId: ID!,
      $beginDate: _DateTime!,
      $endDate: _DateTime!,
      $clinicOfficeId: ID!,
      $customerId: String!
    ) {
      packet {
        createClinicTable(input: {
          clinic: $clinicId,
          clinicDoctor: $clinicDoctorId,
          clinicOffice: $clinicOfficeId,
          customer: { entityId: $customerId },
          beginDate: $beginDate,
          endDate: $endDate
        }) {
          id
        }
      }
    }
    """

    variables = {
        "clinicId": clinic_id,
        "clinicDoctorId": clinic_doctor_id,
        "beginDate": begin_date,
        "endDate": end_date,
        "clinicOfficeId": clinic_office_id,
        "customerId": customer_id
    }

    result = graphql_query(mutation, variables)

    if result and 'packet' in result and 'createClinicTable' in result['packet']:
        print("Appointment created successfully")
        return result['packet']['createClinicTable']
    else:
        print("Failed to create appointment")
        return None

def start():
    data = load_data()
    clinics = data['clinics']
    clinic_offices = data['clinic_offices']
    clinic_doctors = data['clinic_doctors']
    customers = data['customers']

    # Create a mapping of clinic numbers to IDs
    clinic_mapping = {str(i + 1): clinic['id'] for i, clinic in enumerate(clinics)}
    customer_mapping = {customer['insurancePolicyNumber']: customer['id'] for customer in customers}

    # Input clinic number instead of ID
    clinic_number = simpledialog.askstring("Выбор клиники",
                                           "Введите номер клиники (например, 1 для Клиника N1):\n" + "\n".join(
                                               [f"{i + 1}: {clinic['name']}" for i, clinic in enumerate(clinics)]))

    # Validate input and get the corresponding clinic ID
    clinic_id = clinic_mapping.get(clinic_number)
    if not clinic_id:
        messagebox.showerror("Ошибка", "Некорректный номер клиники.")
        return

    # Proceed with selecting office
    offices = clinic_offices.get(clinic_id, [])
    if not offices:
        messagebox.showerror("Ошибка", "Нет доступных кабинетов в выбранной клинике.")
        return

    # Create a mapping of office numbers to IDs
    office_mapping = {office['officeNumber']: office['id'] for office in offices}

    # Input office number instead of ID
    office_number = simpledialog.askstring("Выбор кабинета", "Введите номер кабинета:\n" + "\n".join(
        [f"{office['officeNumber']}" for office in offices]))

    # Validate input and get the corresponding office ID
    office_id = office_mapping.get(office_number)
    if not office_id:
        messagebox.showerror("Ошибка", "Некорректный номер кабинета.")
        return

    # Selecting doctor by specialty
    specialties = list(set(doctor['doctor']['entity']['doctorType']['name'] for doctor in clinic_doctors.get(clinic_id, [])))
    specialty_selection = simpledialog.askstring("Выбор специальности", "Выберите специальность врача по номеру:\n" + "\n".join(
        [f"{i + 1}: {specialty}" for i, specialty in enumerate(specialties)]))

    # Validate the specialty selection
    if specialty_selection.isdigit() and 1 <= int(specialty_selection) <= len(specialties):
        specialty = specialties[int(specialty_selection) - 1]
    else:
        messagebox.showerror("Ошибка", "Некорректный выбор специальности.")
        return

    # Find matching doctors by specialty
    doctors = [doctor for doctor in clinic_doctors.get(clinic_id, []) if
               doctor['doctor']['entity']['doctorType']['name'] == specialty]

    if not doctors:
        messagebox.showerror("Ошибка", "Нет доступных врачей с указанной специальностью.")
        return

    # Display matching doctors
    doctor_selection = simpledialog.askstring("Выбор врача", "Выберите врача по номеру:\n" + "\n".join(
        [
            f"{i + 1}: {doctor['doctor']['entity']['person']['entity']['firstName']} {doctor['doctor']['entity']['person']['entity']['lastName']}"
            for i, doctor in enumerate(doctors)]))

    # Validate the doctor's selection
    if doctor_selection.isdigit() and 1 <= int(doctor_selection) <= len(doctors):
        doctor_id = doctors[int(doctor_selection) - 1]['id']  # Получаем ID врача
    else:
        messagebox.showerror("Ошибка", "Некорректный выбор врача.")
        return

    # Input date and time
    begin_date = simpledialog.askstring("Дата и время начала приема",
                                        "Введите дату и время начала приема в формате YYYY-MM-DDTHH:MM:SS")
    end_date = simpledialog.askstring("Дата и время окончания приема",
                                      "Введите дату и время окончания приема в формате YYYY-MM-DDTHH:MM:SS")
    insurance_policy_number = simpledialog.askstring("Медицинский полис", "Введите номер медицинского полиса:")

    # Проверяем, существует ли клиент с таким номером полиса
    customer_id = customer_mapping.get(insurance_policy_number)
    if not customer_id:
        messagebox.showerror("Ошибка", "Некорректный номер медицинского полиса.")
        return

    # Create appointment
    appointment_result = create_appointment(clinic_id, doctor_id, begin_date, end_date, office_id, customer_id)

    if appointment_result:
        messagebox.showinfo("Успешно", "Запись создана успешно!")
    else:
        messagebox.showerror("Ошибка", "Не удалось создать запись.")

if __name__ == "__main__":
    start()