import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from config import google_sheet_id


api_json = {
  "type": "service_account",
  "project_id": "facebook-marketplace-scraper",
  "private_key_id": "80734cb17b03a7414512e313ad74fb8b06f0b108",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCVV5+c3K8k+uus\nBrN7XRFcaDj8vPOVvfWiyWoYPMPQSj4YhvpVA2vqcghhZAKA1vLh0QQxj5AMuvVa\nklXjSjPQJMBZ/BAATZUXKzz5U67MpdT8IOgCzGsR+FTv5NCY+d5IfnjBjP7tdD+C\nMfi7UUxgIVhRBp3QfnCP6bvRIZzauNnLbUdj+rQesu2wuqNiUUCbkMaG+3aRyDUL\nbyr5Aigzn2AntW0EnMj+0zDRNeLHLA7DlL+LoEh3VX3yUwbgY6PL+WgrCICN09ir\noEF68iOQFVj6ZUei9Z3VEyaqIN/bUQgXdsYG0IKXSvuGpSq5gUH9rTJEChSwFNUi\nvdnv0ZxnAgMBAAECggEAMZJmXvE6CfJobC/FP/vCmYPW9r3ZtSja8nAdEXKKJQef\n2RBk4/dAyQ+VDI7f7dhrwt1YoQLgc/lTG/9bFxk4Xaz1VGlA/njCNnCZysEmUrPx\nIMfje5pTKCHgP8kaHM1EJZgliUm+DR/7PMJNqA/yZC5tXGfv1pdB0eNp/p9Dq64S\ndeZ7buI/+y9KTrz8b1MAUlYudSJgWKdvZ8kCYp5F70VV+nLbI3k7ou307HobCbuw\nRjD7gIAoQw6JVcpXN9wrRy3HE5zE6+6DxGj1AicK/Gx0p0CnGHtXbvDJiKrVqxOD\nNfGq0wbFa+ogd+n3tb0zd/qQClNSVrc1DBKrL79S0QKBgQDIDTSgEd/BGSBsvMbs\nhr//myvQEZjxJoLVbg+hF4aBWCkk7v6rTeSDzhQCdWF94akyfhJgl4HxuB5Etaea\nLWbZkJNuY/fbCo8h1P781Q3ZCcOURfBqRq/GqVND8h/Vmz+LQQCXG8U9SjpYx5aW\nxRqIayeuJid5ryhk4SIFI64JtQKBgQC/G9wMM/uo7/mSyvX1vfE8y+E/GS9WMaJW\n8G0v+mBR8fJ8dzEf7JDJmfsI3GTpB2r4rka8C04tqZmxdFwAqsHRs1kxVFpUxsCi\nX/QTBXJpOMZyWzFoHWE2uSyXpUnnOtpc+f2ThqUGhdC7Mxt65HTtJi939jYOVD77\nUJq72C7vKwKBgEdObbOgq2Do0+XuY/lrDoTNipBftWQ/leL9mBSTjh4Mjp3bkmr9\nGLbifb9il52HEggtZ9+GIYtHVYKoPVV3WXGzVtnCSFaLLPmiMkFsr8Ls+Amh5E/9\nYiotsMBHTZGWBNBeGxfBjkyKaMG8YrDbENoPV9V7RBbbmEpc9QNf9GkBAoGBAIu+\n4Irf3E+to29PEMpw6Z2ObJiKXw4FX3N5fi5ORO7HII0ZT4fLohh5i5LwLq4kKXnN\nXpYVIkbLtUKJFtm6A97G6hrjVuaVK7nQtpbOLdp5lMt8mcVLbpHomI4PZNo8M/83\nItEk7Tm20mqBNcAInOPpP17WYLLbse5uA6gGrlNfAoGAQRIGI8MqHH5Dr9x9cHVB\nTSRN1f68DNazL6qRmSUnYFHMlJMhnXnDw5Qvo2Q/WnoS/QQFpczzeFAB3kxsWnKU\nYhfCNl9A7X8dWqhb/HKh8EWWdBYs3AmwOWPTqR21vpnZufTr3/eACYuni2cyoP0H\n1zwMiAVarrYsw/5A+7wUUWI=\n-----END PRIVATE KEY-----\n",
  "client_email": "facebook-parser@facebook-marketplace-scraper.iam.gserviceaccount.com",
  "client_id": "117487334748237450530",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/facebook-parser%40facebook-marketplace-scraper.iam.gserviceaccount.com"
}


def get_service_sacc():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_service = ServiceAccountCredentials.from_json_keyfile_dict(api_json, scopes=scopes).authorize(httplib2.Http())
    return build(serviceName="sheets", version="v4", http=creds_service)


def get_data():
    service = get_service_sacc()
    sheet = service.spreadsheets()
    response = sheet.values().get(spreadsheetId=google_sheet_id, range=f"Facebook Marketplace!A2:AS100000").execute()
    result = list()
    if "values" in list(response.keys()):
        for element in response["values"]:
            result.append(element[6])
    return result


def record_data(result):
    service = get_service_sacc()
    sheet = service.spreadsheets()
    values = list()
    for element in result:
        element_values = [element["title"], element["price"], element["address"], element["animal_friendly"],
                          element["date_of_publication"], element["description"], element["object_url"],
                          element["rating"], element["date_of_registration"]]
        values.append(element_values)
    body = {"values": values}
    sheet.values().append(spreadsheetId=google_sheet_id,
                          range=f"Facebook Marketplace!A1:K1",
                          valueInputOption="RAW", body=body).execute()
    print(f"[INFO] Данные были успешно записаны в Google Sheets")
