import requests
from datetime import datetime, timedelta
import json
from colorama import init, Fore, Style
from tabulate import tabulate

# Инициализация colorama для работы с цветным выводом
init()

# URL GraphQL сервера
url = "https://smapi.pv-api.sbc.space/ds-7429590172239724545/graphql"

def print_header(text):
    print(f"\n{Fore.BLUE}{'=' * 80}")
    print(f"{text.center(80)}")
    print(f"{'=' * 80}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")

def format_doctor_types(data):
    if not data or 'searchDoctorType' not in data or 'elems' not in data['searchDoctorType']:
        return []

    table_data = []
    for item in data['searchDoctorType']['elems']:
        table_data.append([
            item.get('id', 'N/A'),
            item.get('name', 'N/A'),
            item.get('description', 'N/A')
        ])
    return tabulate(table_data, headers=['ID', 'Name', 'Description'], tablefmt='grid')

def format_doctors(data):
    if not data or 'searchDoctor' not in data or 'elems' not in data['searchDoctor']:
        return []

    table_data = []
    for item in data['searchDoctor']['elems']:
        doctor_type = item.get('doctorType', {})
        person = item.get('person', {}).get('entity', {})
        table_data.append([
            item.get('id', 'N/A'),
            f"{person.get('firstName', '')} {person.get('lastName', '')}",
            doctor_type.get('name', 'N/A')
        ])
    return tabulate(table_data, headers=['ID', 'Name', 'Specialization'], tablefmt='grid')

def format_customers(data):
    if not data or 'searchCustomer' not in data or 'elems' not in data['searchCustomer']:
        return []

    table_data = []
    for item in data['searchCustomer']['elems']:
        person = item.get('person', {}).get('entity', {})
        table_data.append([
            item.get('id', 'N/A'),
            f"{person.get('firstName', '')} {person.get('lastName', '')}",
            item.get('insurancePolicyNumber', 'N/A'),
            item.get('phoneNumber', 'N/A')
        ])
    return tabulate(table_data, headers=['ID', 'Name', 'Insurance Policy', 'Phone'], tablefmt='grid')

def format_clinics(data):
    if not data or 'searchClinic' not in data or 'elems' not in data['searchClinic']:
        return []

    table_data = []
    for item in data['searchClinic']['elems']:
        table_data.append([
            item.get('id', 'N/A'),
            item.get('name', 'N/A')
        ])
    return tabulate(table_data, headers=['ID', 'Name'], tablefmt='grid')

def format_clinic_offices(data):
    if not data or 'searchClinicOffice' not in data or 'elems' not in data['searchClinicOffice']:
        return []

    table_data = []
    for item in data['searchClinicOffice']['elems']:
        table_data.append([
            item.get('id', 'N/A'),
            item.get('clinic', {}).get('name', 'N/A'),
            item.get('officeNumber', 'N/A')
        ])
    return tabulate(table_data, headers=['ID', 'Clinic', 'Office Number'], tablefmt='grid')

def graphql_query(query, variables=None):
    try:
        json_data = {
            'query': query,
            'variables': variables or {}
        }

        print_info("Sending request...")

        response = requests.post(url, json=json_data)

        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                print_error(f"GraphQL Errors: {result['errors']}")
                return None
            return result.get('data')
        else:
            print_error(f"HTTP Error {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return None

def get_all_doctor_types():
    query = """
    query {
      searchDoctorType(cond: "it.isDel == false") {
        elems {
          id
          name
          description
        }
      }
    }
    """
    return graphql_query(query)

def get_all_doctors():
    query = """
    query {
      searchDoctor {
        elems {
          id
          doctorType {
            id
            name
          }
          person {
            entityId
            entity {
              firstName
              lastName
            }
          }
        }
      }
    }
    """
    return graphql_query(query)

def get_all_customers():
    query = """
    query {
      searchCustomer(cond: "1==1") {
        elems {
          id
          insurancePolicyNumber
          phoneNumber
          person {
            entityId
            entity {
              firstName
              lastName
            }
          }
        }
      }
    }
    """
    return graphql_query(query)

def get_all_clinics():
    query = """
    query {
      searchClinic {
        elems {
          id
          name
        }
      }
    }
    """
    return graphql_query(query)

def get_clinic_offices(clinic_id):
    query = f"""
    query {{
      searchClinicOffice(cond: "it.clinic.id == '{clinic_id}'") {{
        elems {{
          id
          clinic {{
            id
            name
          }}
          officeNumber
        }}
      }}
    }}
    """
    return graphql_query(query)




def format_doctor_availability(data):
    if not data or 'searchClinicDoctorAvailability' not in data or 'elems' not in data[
        'searchClinicDoctorAvailability']:
        return []

    table_data = []
    for item in data['searchClinicDoctorAvailability']['elems']:
        table_data.append([
            item.get('id', 'N/A'),
            datetime.fromisoformat(item.get('beginDate')).strftime('%Y-%m-%d %H:%M'),
            datetime.fromisoformat(item.get('endDate')).strftime('%Y-%m-%d %H:%M'),
            item.get('clinicOffice', {}).get('officeNumber', 'N/A')
        ])
    return tabulate(table_data, headers=['ID', 'Begin Date', 'End Date', 'Office Number'], tablefmt='grid')


def get_doctor_availability(clinic_doctor_id, date_from=None, date_to=None):
    if date_from is None:
        date_from = datetime.now()
    if date_to is None:
        date_to = date_from + timedelta(days=7)

    query = """
    query searchClinicDoctorAvailability($clinicDoctorId: String!, $dateFrom: _DateTime!, $dateTo: _DateTime!) {
        searchClinicDoctorAvailability(
            cond: "it.clinicDoctor.id == ${clinicDoctorId} && it.endDate >= ${dateFrom} && it.beginDate <= ${dateTo}"
        ) @strExpr(string:$clinicDoctorId, dateTimes:[$dateFrom, $dateTo]) {
            elems {
                id
                beginDate
                endDate
                clinicOffice {
                    id
                    officeNumber
                }
            }
        }
    }
    """

    variables = {
        "clinicDoctorId": clinic_doctor_id,
        "dateFrom": date_from.isoformat(),
        "dateTo": date_to.isoformat()
    }

    return graphql_query(query, variables)


def get_clinic_doctors(clinic_id):
    query = """
    query {
        searchClinicDoctor(
            cond: "it.clinic.id == '%s'"
        ) {
            elems {
                id
                doctor {
                    entity {
                        person {
                            entity {
                                firstName
                                lastName
                            }
                        }
                        doctorType {
                            name
                        }
                    }
                }
            }
        }
    }
    """ % clinic_id

    return graphql_query(query)


def format_clinic_doctors(data):
    if not data or 'searchClinicDoctor' not in data or 'elems' not in data['searchClinicDoctor']:
        return []

    table_data = []
    for item in data['searchClinicDoctor']['elems']:
        doctor = item.get('doctor', {}).get('entity', {})
        person = doctor.get('person', {}).get('entity', {})
        doctor_type = doctor.get('doctorType', {})

        table_data.append([
            item.get('id', 'N/A'),
            f"{person.get('firstName', '')} {person.get('lastName', '')}",
            doctor_type.get('name', 'N/A')
        ])
    return tabulate(table_data, headers=['ID', 'Doctor Name', 'Specialization'], tablefmt='grid')

def format_clinic_tables(data):
    if not data or 'searchClinicTable' not in data or 'elems' not in data['searchClinicTable']:
        return []

    table_data = []
    for item in data['searchClinicTable']['elems']:
        customer = item.get('customer', {}).get('entity', {}).get('person', {}).get('entity', {})
        doctor = item.get('clinicDoctor', {}).get('doctor', {}).get('entity', {}).get('person', {}).get('entity', {})
        table_data.append([
            item.get('id', 'N/A'),
            f"{doctor.get('firstName', '')} {doctor.get('lastName', '')}",
            f"{customer.get('firstName', '')} {customer.get('lastName', '')}",
            datetime.fromisoformat(item.get('beginDate')).strftime('%Y-%m-%d %H:%M'),
            datetime.fromisoformat(item.get('endDate')).strftime('%Y-%m-%d %H:%M'),
            item.get('clinicOffice', {}).get('officeNumber', 'N/A')
        ])
    return tabulate(table_data, headers=['ID', 'Doctor Name', 'Customer Name', 'Begin Date', 'End Date', 'Office Number'], tablefmt='grid')


def get_clinic_tables(clinic_id):
    query = """
    query {
        searchClinicTable(cond: "it.clinic.id == '%s'") {
            elems {
                id
                beginDate
                endDate
                clinicOffice {
                    id
                    officeNumber
                }
                customer {
                    entity {
                        person {
                            entity {
                                firstName
                                lastName
                            }
                        }
                        insurancePolicyNumber
                        phoneNumber
                    }
                }
                clinicDoctor {
                    id
                    doctor {
                        entity {
                            person {
                                entity {
                                    firstName
                                    lastName
                                }
                            }
                            doctorType {
                                name
                            }
                        }
                    }
                }
            }
        }
    }
    """ % clinic_id

    return graphql_query(query)


def format_clinic_tables(data):
    if not data or 'searchClinicTable' not in data or 'elems' not in data['searchClinicTable']:
        return []

    table_data = []
    for item in data['searchClinicTable']['elems']:
        # Получаем данные о пациенте
        customer = item.get('customer', {}).get('entity', {})
        customer_person = customer.get('person', {}).get('entity', {})
        customer_name = f"{customer_person.get('firstName', '')} {customer_person.get('lastName', '')}"

        # Получаем данные о враче
        clinic_doctor = item.get('clinicDoctor', {}).get('doctor', {}).get('entity', {})
        doctor_person = clinic_doctor.get('person', {}).get('entity', {})
        doctor_name = f"{doctor_person.get('firstName', '')} {doctor_person.get('lastName', '')}"
        doctor_type = clinic_doctor.get('doctorType', {}).get('name', 'N/A')

        # Форматируем время
        begin_date = datetime.fromisoformat(item.get('beginDate')).strftime('%Y-%m-%d %H:%M') if item.get(
            'beginDate') else 'N/A'
        end_date = datetime.fromisoformat(item.get('endDate')).strftime('%Y-%m-%d %H:%M') if item.get(
            'endDate') else 'N/A'

        table_data.append([
            item.get('id', 'N/A'),
            customer_name,
            doctor_name,
            doctor_type,
            begin_date,
            end_date,
            item.get('clinicOffice', {}).get('officeNumber', 'N/A'),
            customer.get('insurancePolicyNumber', 'N/A'),
            customer.get('phoneNumber', 'N/A')
        ])

    headers = [
        'ID',
        'Patient Name',
        'Doctor Name',
        'Specialization',
        'Begin Date',
        'End Date',
        'Office Number',
        'Insurance Policy',
        'Phone Number'
    ]

    return tabulate(table_data, headers=headers, tablefmt='grid')


def save_to_json(data, filename):
    """
    Сохраняет данные в JSON файл
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print_success(f"Data successfully saved to {filename}")
    except Exception as e:
        print_error(f"Error saving data to JSON: {str(e)}")


def collect_all_data():
    """
    Собирает все данные в единую структуру
    """
    data = {
        "doctor_types": [],
        "doctors": [],
        "customers": [],
        "clinics": [],
        "clinic_offices": {},
        "clinic_doctors": {},
        "doctor_schedules": {},
        "appointments": {}
    }

    # Получаем типы врачей
    result = get_all_doctor_types()
    if result and 'searchDoctorType' in result and 'elems' in result['searchDoctorType']:
        data["doctor_types"] = result['searchDoctorType']['elems']

    # Получаем врачей
    result = get_all_doctors()
    if result and 'searchDoctor' in result and 'elems' in result['searchDoctor']:
        data["doctors"] = result['searchDoctor']['elems']

    # Получаем клиентов
    result = get_all_customers()
    if result and 'searchCustomer' in result and 'elems' in result['searchCustomer']:
        data["customers"] = result['searchCustomer']['elems']

    # Получаем клиники и связанные данные
    clinics_result = get_all_clinics()
    if clinics_result and 'searchClinic' in clinics_result and 'elems' in clinics_result['searchClinic']:
        data["clinics"] = clinics_result['searchClinic']['elems']

        # Для каждой клиники получаем дополнительные данные
        for clinic in clinics_result['searchClinic']['elems']:
            clinic_id = clinic.get('id')
            if clinic_id:
                # Получаем кабинеты
                offices_result = get_clinic_offices(clinic_id)
                if offices_result and 'searchClinicOffice' in offices_result:
                    data["clinic_offices"][clinic_id] = offices_result['searchClinicOffice']['elems']

                # Получаем врачей клиники
                doctors_result = get_clinic_doctors(clinic_id)
                if doctors_result and 'searchClinicDoctor' in doctors_result:
                    data["clinic_doctors"][clinic_id] = doctors_result['searchClinicDoctor']['elems']

                    # Получаем расписание для каждого врача
                    for clinic_doctor in doctors_result['searchClinicDoctor']['elems']:
                        clinic_doctor_id = clinic_doctor.get('id')
                        if clinic_doctor_id:
                            availability_result = get_doctor_availability(clinic_doctor_id)
                            if availability_result and 'searchClinicDoctorAvailability' in availability_result:
                                data["doctor_schedules"][clinic_doctor_id] = \
                                availability_result['searchClinicDoctorAvailability']['elems']

                # Получаем записи к врачам
                appointments_result = get_clinic_tables(clinic_id)
                if appointments_result and 'searchClinicTable' in appointments_result:
                    data["appointments"][clinic_id] = appointments_result['searchClinicTable']['elems']

    return data

def main():
    print_header("Medical Information System")

    try:
        # Doctor Types
        print_header("Doctor Types")
        result = get_all_doctor_types()
        if result:
            print(format_doctor_types(result))
            print_success("Successfully retrieved doctor types")
        else:
            print_error("Failed to retrieve doctor types")

        # Doctors
        print_header("Doctors")
        result = get_all_doctors()
        if result:
            print(format_doctors(result))
            print_success("Successfully retrieved doctors")
        else:
            print_error("Failed to retrieve doctors")

        # Customers
        print_header("Customers")
        result = get_all_customers()
        if result:
            print(format_customers(result))
            print_success("Successfully retrieved customers")
        else:
            print_error("Failed to retrieve customers")

        # Clinics
        print_header("Clinics")
        result = get_all_clinics()
        if result:
            print(format_clinics(result))
            print_success("Successfully retrieved clinics")

            # Получаем кабинеты для каждой клиники
            if 'searchClinic' in result and 'elems' in result['searchClinic']:
                for clinic in result['searchClinic']['elems']:
                    clinic_id = clinic.get('id')
                    if clinic_id:
                        print_header(f"Offices for clinic: { clinic.get('name', 'Unknown')} ")
                        offices_result = get_clinic_offices(clinic_id)
                        if offices_result:
                            print(format_clinic_offices(offices_result))
                            print_success("Successfully retrieved clinic offices")
                        else:
                            print_error("Failed to retrieve clinic offices")
        else:
            print_error("Failed to retrieve clinics")

        # Для каждой клиники получаем информацию о врачах и их расписании
        print_header("Doctors Schedule")
        clinics_result = get_all_clinics()
        if clinics_result and 'searchClinic' in clinics_result and 'elems' in clinics_result['searchClinic']:
            for clinic in clinics_result['searchClinic']['elems']:
                clinic_id = clinic.get('id')
                if clinic_id:
                    print_header(f"Doctors in clinic: {clinic.get('name', 'Unknown')} (ID: {clinic_id})")

                    # Получаем врачей клиники
                    doctors_result = get_clinic_doctors(clinic_id)
                    if doctors_result:
                        formatted_output = format_clinic_doctors(doctors_result)
                        if formatted_output:
                            print(formatted_output)
                            print_success("Successfully retrieved clinic doctors")
                        else:
                            print_info("No doctors found for this clinic")
                    else:
                        print_error("Failed to retrieve clinic doctors")

                        # Если есть врачи, получаем их расписание
                        if doctors_result and 'searchClinicDoctor' in doctors_result and 'elems' in doctors_result[
                            'searchClinicDoctor']:
                            for clinic_doctor in doctors_result['searchClinicDoctor']['elems']:
                                clinic_doctor_id = clinic_doctor.get('id')
                                doctor = clinic_doctor.get('doctor', {}).get('entity', {})
                                person = doctor.get('person', {}).get('entity', {})
                                doctor_name = f"{person.get('firstName', '')} {person.get('lastName', '')}"

                                print_header(f"Schedule for doctor: {doctor_name}")
                                availability_result = get_doctor_availability(clinic_doctor_id)
                                if availability_result:
                                    print(format_doctor_availability(availability_result))
                                    print_success("Successfully retrieved doctor's schedule")
                                else:
                                    print_error("Failed to retrieve doctor's schedule")


        # Получаем список клиник
        clinics_result = get_all_clinics()
        if clinics_result and 'searchClinic' in clinics_result and 'elems' in clinics_result['searchClinic']:
            for clinic in clinics_result['searchClinic']['elems']:
                clinic_id = clinic.get('id')
                if clinic_id:
                    print_header(f"Appointments in clinic: {clinic.get('name', 'Unknown')}")

                    # Получаем записи к врачам для данной клиники
                    appointments_result = get_clinic_tables(clinic_id)
                    if appointments_result:
                        formatted_output = format_clinic_tables(appointments_result)
                        if formatted_output:
                            print(formatted_output)
                            print_success("Successfully retrieved appointments")
                        else:
                            print_info("No appointments found for this clinic")
                    else:
                        print_error("Failed to retrieve appointments")


            # Собираем все данные и сохраняем в JSON
            print_header("Saving data to JSON")
            all_data = collect_all_data()

            filename = f"results.json"
            save_to_json(all_data, filename)


    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback
        print_error(traceback.format_exc())

    print_header("End of Report")


if __name__ == "__main__":
    main()