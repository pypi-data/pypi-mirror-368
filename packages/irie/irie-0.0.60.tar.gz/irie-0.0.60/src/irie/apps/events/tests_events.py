#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   Author: Claudio Perez
#
#----------------------------------------------------------------------------#
from django.test import TestCase
from django.contrib.auth.models import User
import json

test_user = {"username": "testuser", "password": "testpassword"}
event_file = "../tests/58658_007_20210426_10.09.54.P.zip"

class QuakeEventTest(TestCase):
    def setUp(self):
        new_user = User.objects.create(username=test_user["username"])
        new_user.set_password(test_user["password"])
        new_user.save()

    def get_token(self):
        res = self.client.post(
            "/api/token/",
            data=json.dumps(
                {
                    "username": test_user["username"],
                    "password": test_user["password"],
                }
            ),
            content_type="application/json",
        )
        result = json.loads(res.content)
        self.assertTrue("access" in result)
        return result["access"]

    def test_add_events_forbidden(self):
        with open(event_file, "rb") as fp:
            res = self.client.post(
                "/api/events/",
                {
                    "upload_data": {"name": "name"},
                    "event_file": fp,
                },
                #content_type="multipart/form-data",
            )
        self.assertEquals(res.status_code, 401)
        res = self.client.post(
            "/api/events/",
            {
                "upload_data": {"name": "2"},
                "event_file": open(event_file,"rb")
            },
            #content_type="multipart/form-data",
            HTTP_AUTHORIZATION=f"Bearer WRONG TOKEN",
        )
        self.assertEquals(res.status_code, 401)

    def test_add_events_ok(self):
        token = self.get_token()
        with open(event_file,"rb") as fp:
            res = self.client.post(
                "/api/events/",
                {
                    "upload_data": '{"name": "2"}',
                    "event_file": fp
                },
                #content_type="multipart/form-data",
                HTTP_AUTHORIZATION=f"Bearer {token}",
            )
        self.assertEquals(res.status_code, 201)
        print("res.content: ",res.content)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["upload_data"]["name"], "2")

    def test_add_events_wrong_data(self):
        token = self.get_token()
        res = self.client.post(
            "/api/events/",
            data=json.dumps(
                {
                    "upload_data": '{"name": "2020-01-01"}',
                    "item": "Hard Drive",
                    "price": -1,
                    "quantity": 10,
                }
            ),
            content_type="multipart/form-data",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEquals(res.status_code, 400)

        res = self.client.post(
            "/api/events/",
            data=json.dumps(
                {
                    "upload_data": '{"name": "2020-01-01"}',
                    "item": "Hard Drive",
                    "price": 1,
                    "quantity": -10,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEquals(res.status_code, 400)

        res = self.client.post(
            "/api/events/",
            data=json.dumps(
                {
                    "upload_data": '{"date": "2020-01-01"}',
                    "item": "",
                    "price": 1,
                    "quantity": 10,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEquals(res.status_code, 400)

    def test_add_events_calculate(self):
        token = self.get_token()
        res = self.client.post(
            "/api/events/",
            {
                "upload_data": '{"name": "2020-01-01"}',
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEquals(res.status_code, 201)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["amount"], 35)  # should be calculated

    #  -------------------------- GET RECORDS -------------------------------------------

    def test_get_records(self):
        token = self.get_token()
        with open(event_file, "rb") as fp:
            res = self.client.post(
                "/api/events/",
                {"upload_data": '{"name":"1"}', "event_file": fp},
                #content_type="multipart/form-data",
                HTTP_AUTHORIZATION=f"Bearer {token}",
            )
        self.assertEquals(res.status_code, 201)
        id1 = json.loads(res.content)["data"]["id"]

        with open(event_file, "rb") as fp:
            res = self.client.post(
                "/api/events/",
                {"upload_data": '{"name":"2"}', "event_file": fp},
                #content_type="multipart/form-data",
                HTTP_AUTHORIZATION=f"Bearer {token}",
            )
        self.assertEquals(res.status_code, 201)
        id2 = json.loads(res.content)["data"]["id"]
        

        # Perform GET requests
        res = self.client.get(
            "/api/events/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)["data"]
        self.assertEquals(len(result), 2)  # 2 records
        self.assertTrue(result[0]["id"] == id1 or result[1]["id"] == id1)
        self.assertTrue(result[0]["id"] == id2 or result[1]["id"] == id2)

        res = self.client.get(
            f"/api/events/{id1}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["upload_data"]["name"], "1")


    #  -------------------------- PUT AND DELETE RECORDS --------------------------------------

    def test_put_delete_records(self):
        token = self.get_token()
        with open(event_file, "rb") as fp:
            res = self.client.post(
                "/api/events/",
                {
                    "upload_data": '{"name":"test_put_delete_records"}',
                    "event_file": fp
                },
                #content_type="multipart/form-data",
                HTTP_AUTHORIZATION=f"Bearer {token}",
            )
        self.assertEquals(res.status_code, 201)
        id = json.loads(res.content)["data"]["id"]

        with open(event_file, "rb") as fp:
            res = self.client.put(
                f"/api/events/{id}/",
                {"name": "new_name", "event_file": fp},
                #content_type="multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
                content_type="multipart/form-data",
                HTTP_AUTHORIZATION=f"Bearer {token}",
            )

        print(res.content)
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["upload_data"]["name"], "new_name")

        res = self.client.get(
            f"/api/events/{id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["upload_data"]["name"], "new_name")


        res = self.client.delete(
            f"/api/events/{id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEquals(res.status_code, 410)  # Gone

        res = self.client.get(
            f"/api/events/{id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEquals(res.status_code, 404)  # Not found

