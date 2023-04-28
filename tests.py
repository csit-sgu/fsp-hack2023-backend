import requests

class TestAPI:
  base_url = "http://localhost:5002"
  
  user_payload = {
      'auth': {
          'email': "test_email@sgu.ru",
          'password': "test_password"
        },
        'profile': {
          'name': "some name",
          'surname': "some surname",
          'patronymic': "some patronymic",
          'birthday': "07/03/2001",
          'passport': "1234567891",
          'phone': "+79616490178",
          'address': "some address",
          'organization': "some organization",
          'insurance': "1111222233334444",
          'gender': "male"
        }
    }
  def test_reqister(self):
    
    response = requests.post(url=f"{TestAPI.base_url}/auth/register", json=TestAPI.user_payload)
    assert response.status_code == 201
    
  def test_login(self):
    