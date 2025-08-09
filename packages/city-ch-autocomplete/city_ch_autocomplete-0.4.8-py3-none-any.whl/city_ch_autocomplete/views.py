import re

import httpx

from django.conf import settings
from django.core.mail import mail_admins
from django.http import JsonResponse
from django.views.generic import View


class CityCHAutocompleteView(View):
    # Read https://developer.post.ch/en/address-web-services-rest, section 4.4
    POST_API = 'https://webservices.post.ch:17023/IN_SYNSYN_EXT/REST/v1/autocomplete4'

    def get(self, request, *args, **kwargs):
        values = []
        q = request.GET.get('q').strip().lower().replace('saint', 'st')
        if q:
            if settings.POST_API_USER:
                values = self.search_from_api(q)
            else:
                values = self.search_from_db(q)
        return JsonResponse(values, safe=False)

    def search_from_api(self, q):
        params = {'dataset': 'plz_verzeichnis_v2', 'rows': 30, 'q': q}
        try:
            zip_part = re.match(r'\s*(\d+)\s?', q).group().strip()
        except AttributeError:
            zip_part = ""
        town_part = q.replace(zip_part, '').strip()
        params = {
            "request": {
                "ONRP": 0,
                "ZipCode": zip_part,
                "ZipAddition": "",
                "TownName": town_part,
                "STRID": 0,
                "StreetName": "",
                "HouseKey": 0,
                "HouseNo": "",
                "HouseNoAddition": ""
            },
            "zipOrderMode": 1,  # ZipTypeNotPoBox
            "zipFilterMode": 0
        }
        try:
            response = httpx.post(
                self.POST_API,
                auth=(settings.POST_API_USER, settings.POST_API_PASSWORD),
                json=params,
                headers={'Accept': "application/json"}
            )
        except httpx.HTTPError:
            return self.error_response(response)
        if response.status_code != 200:
            return self.error_response(response)
        json_resp = response.json()
        results = json_resp.get('QueryAutoComplete4Result', {}).get('AutoCompleteResult', [])
        values = [
            f"{res['ZipCode']} {res['TownName']}" for res in results
        ]
        return [
            {'value': val, 'label': val} for val in values
        ]

    def search_from_db(self, q):
        """In the case the API is unavailable."""
        from .models import PLZdb

        if q.isdigit():
            query = PLZdb.objects.filter(plz__startswith=q)
        else:
            query = PLZdb.objects.filter(name__icontains=q)
        return [
            {'value': line.pk, 'label': f'{line.plz} {line.name}'}
            for line in query[:30]
        ]

    def error_response(self, response):
        mail_admins("Error API Swisspost", f"Error connecting to SwissPost: {response}")
        err_msg = {'result': 'error', 'message': "Failed to connect to SwissPost API"}
        return JsonResponse(err_msg)
