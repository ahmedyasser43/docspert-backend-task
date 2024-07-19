import os
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from .models import Account
import io


class AccountViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.list_url = reverse('List Accounts')
        self.detail_url = lambda pk: reverse('Account Details', kwargs={'id': pk})
        account1_id = uuid.uuid4()
        account2_id = uuid.uuid4()
        self.test_account_1 = Account.objects.create(id=account1_id, name='Test 1', balance=1000)
        self.test_account_2 = Account.objects.create(id=account2_id, name='Test 2', balance=2000)

    def test_list_all_accounts(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts.html')
        self.assertContains(response, self.test_account_1.name)
        self.assertContains(response, self.test_account_2.name)

    def test_get_account_detail(self):
        response = self.client.get(self.detail_url(self.test_account_1.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accountDetails.html')
        self.assertContains(response, self.test_account_1.name)
        self.assertContains(response, self.test_account_1.balance)

    def test_transfer_money(self):
        data = {
            'receiverAccount': self.test_account_2.id,
            'amount': '50.0'
        }
        response = self.client.post(self.detail_url(self.test_account_1.id), data)
        self.assertEqual(response.status_code, 302)
        self.test_account_1.refresh_from_db()
        self.test_account_2.refresh_from_db()
        self.assertEqual(self.test_account_1.balance, 950)
        self.assertEqual(self.test_account_2.balance, 2050)

    def test_upload_csv(self):
        csv_path = os.path.join(os.path.dirname(__file__), 'accounts.csv')
        with open(csv_path, 'rb') as csv_file:
            csv_content = SimpleUploadedFile('accounts.csv', csv_file.read(), content_type='text/csv')
            response = self.client.post(self.list_url, {'file': csv_content}, format='multipart')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Account.objects.filter(name='Joy Dean').exists())
        self.assertTrue(Account.objects.filter(name='Andre Cooper').exists())

    def test_upload_excel(self):
        excel_path = os.path.join(os.path.dirname(__file__), 'accounts.xlsx')
        with open(excel_path, 'rb') as excel_file:
            excel_content = SimpleUploadedFile('accounts.xlsx', excel_file.read(),
                                               content_type='application/vnd.openxmlformats-officedocument'
                                                            '.spreadsheetml.sheet')
            response = self.client.post(self.list_url, {'file': excel_content}, format='multipart')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Account.objects.filter(name='Joy Dean').exists())
        self.assertTrue(Account.objects.filter(name='Andre Cooper').exists())

    def test_upload_no_file(self):
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'No file uploaded')

    def test_upload_unsupported_file_type(self):
        unsupported_content = io.BytesIO(b'test content')
        response = self.client.post(self.list_url, {'file': unsupported_content}, format='multipart')
        self.assertEqual(response.status_code, 302)
