import csv

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views.generic import TemplateView
import pandas as pd

from . import models
from .models import Account


# Create your views here.

class AccountView(TemplateView):
    template_name = "accounts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        if 'id' in kwargs:
            return self.get_account_detail(request, *args, **kwargs)
        return self.list_all_accounts(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'id' in kwargs:
            return self.transfer_money(request, *args, **kwargs)
        if 'file' not in request.FILES:
            return HttpResponse("No file uploaded", status=400)

        file = request.FILES['file']
        supported_extensions = ['csv', 'xlsx', 'xls']
        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in supported_extensions:
            return redirect(request.path)
        elif file_extension == 'csv':
            return self._extract_csv_data(request, file)
        else:
            return self._extarct_excel_data(request, file)

    def list_all_accounts(self, request, *args, **kwargs):
        template = loader.get_template('accounts.html')
        accounts = models.Account.objects.all()
        context = self.get_context_data(**kwargs)
        context['accounts'] = accounts
        return HttpResponse(template.render(context, request))

    def get_account_detail(self, request, *args, **kwargs):
        template = loader.get_template('accountDetails.html')
        account_id = kwargs.get('id')
        try:
            account = Account.objects.get(pk=account_id)
            context = self.get_context_data(**kwargs)
            context['account'] = account
            context['selection_accounts'] = Account.objects.filter().order_by('name').values()
            return HttpResponse(template.render(context, request))
        except Account.DoesNotExist:
            return HttpResponse()

    def transfer_money(self, request, *args, **kwargs):
        sender_id = kwargs.get("id")
        receiver_id = request.POST.get("receiverAccount")
        amount = request.POST.get("amount")
        try:
            if not amount:
                return HttpResponse()
            transfer_amount = float(amount)
            sender = Account.objects.get(pk=sender_id)
            receiver = Account.objects.get(pk=receiver_id)
            if transfer_amount > sender.balance:
                return HttpResponse()
            receiver.balance += transfer_amount
            sender.balance -= transfer_amount
            receiver.save()
            sender.save()
        except Account.DoesNotExist:
            return HttpResponse()

        return redirect(request.path)

    def _extract_csv_data(self, request, file):
        try:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                Account.objects.create(
                    name=row['Name'],
                    id=row['ID'],
                    balance=row['Balance']
                )
            return redirect(request.path)

        except Exception as e:
            return HttpResponse("Error processing file", status=500)

    def _extarct_excel_data(self, request, file):
        try:
            df = pd.read_excel(file)
            for row in df.itertuples(index=False, name='Pandas'):
                Account.objects.create(
                    name=row.Name,
                    id=row.ID,
                    balance=row.Balance
                )
            return redirect(request.path)
        except Exception as e:
            return HttpResponse("Error processing file", status=500)