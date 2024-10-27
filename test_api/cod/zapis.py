import requests
import json

# Добавить цикл для постоянного обновления данных
# Соеденить с моделью


# URL GraphQL сервера
url = "https://smapi.pv-api.sbc.space/ds-7429590172239724545/graphql"

def graphql_query(query, variables=None):
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

def create_person(first_name, last_name, inn, birth_date):
    mutation = """
    mutation createPerson($input: _CreatePersonInput!) {
      packet {
        createPerson(input: $input) {
          id
          firstName
          lastName
          inn
          birthDate
        }
      }
    }
    """

    # Формируем входные данные для мутации
    variables = {
        "input": {
            "firstName": first_name,
            "lastName": last_name,
            "inn": inn,
            "birthDate": birth_date
        }
    }

    # Выполняем запрос
    result = graphql_query(mutation, variables)

    if result and 'packet' in result and 'createPerson' in result['packet']:
        print("Person created successfully")
        return result['packet']['createPerson']
    else:
        print("Failed to create person")
        return None

def create_customer(person_id, insurance_policy_number, phone_number):
    mutation = """
    mutation createCustomer($personId: String!, $insurancePolicyNumber: String!, $phoneNumber: String) {
      packet {
        createCustomer(input: {
          person: { entityId: $personId }
          insurancePolicyNumber: $insurancePolicyNumber
          phoneNumber: $phoneNumber
        }) {
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

    # Формируем входные данные для мутации
    variables = {
        "personId": person_id,
        "insurancePolicyNumber": insurance_policy_number,
        "phoneNumber": phone_number
    }

    # Выполняем запрос
    result = graphql_query(mutation, variables)

    if result and 'packet' in result and 'createCustomer' in result['packet']:
        print("Customer created successfully")
        return result['packet']['createCustomer']
    else:
        print("Failed to create customer")
        return None

def main(first_name, last_name, inn, birth_date, phone_number, insurance_policy_number):
    print("Creating New Person")

    new_person = create_person(first_name, last_name, inn, birth_date)
    if new_person:
        print(f"New person created: {new_person}")

        # Теперь создаем клиента с данными нового человека
        person_id = new_person['id']
        print("Creating New Customer")

        new_customer = create_customer(person_id, insurance_policy_number, phone_number)
        if new_customer:
            print(f"New customer created: {new_customer}")
