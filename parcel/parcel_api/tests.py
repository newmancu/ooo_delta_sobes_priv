from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from parcel_api.tasks import get_usd2rub, perodic_update
from unittest.mock import patch
from parcel_api.models import ParcelTypeModel
from django.forms.models import model_to_dict
from django.core.cache import cache


class Usd2RubMockResponse:

    def __init__(self):
        self.status_code = 200

    def json(self):
        return {
            "Date": "2023-04-08T11:30:00+03:00",
            "PreviousDate": "2023-04-07T11:30:00+03:00",
            "PreviousURL": "\/\/www.cbr-xml-daily.ru\/archive\/2023\/04\/07\/daily_json.js",
            "Timestamp": "2023-04-10T14:00:00+03:00",
            "Valute": {
                "USD": {
                    "ID": "R01235",
                    "NumCode": "840",
                    "CharCode": "USD",
                    "Nominal": 1,
                    "Name": "Доллар США",
                    "Value": 82.3988,
                    "Previous": 80.6713
                }
            }
        }


class ParcelTestCase(APITestCase):

    def setUp(self) -> None:
        self.t1 = ParcelTypeModel.objects.create(name='Одежда')
        self.t2 = ParcelTypeModel.objects.create(name='Электроника')
        self.t3 = ParcelTypeModel.objects.create(name='Разное')

        names = ['test1', 'test2', 'test3', 'test4']
        weights = [1.0, 1.2, 2.0, 3.5]
        prices = [0.0, 1.0, 2.0, 1.4]
        types = [self.t1.id, self.t2.id, self.t3.id, self.t1.id]
        self.parcels = [
            {
                'name': n,
                'weight': w,
                'parcel_price': p,
                'type': t
            }
            for n, w, p, t
            in zip(names, weights, prices, types)
        ]

    def test_parcel_create(self):
        res = []
        for d in self.parcels:
            res.append(self.client.post(
                reverse('register_parcel'),
                d,
                format='json'
            ))
        statuses = all([r.status_code == 201 for r in res])
        self.assertTrue(statuses)

    def test_parcel_blank_name(self):
        obj = self.parcels[0]
        obj['name'] = ''
        res = self.client.post(
            reverse('register_parcel'),
            obj,
            format='json'
        )
        self.assertEqual(res.status_code, 400)

    def test_parcel_negative_create(self):
        res = self.client.post(
            reverse('register_parcel'),
            {
                'name': 'neg1',
                'weight': -12,
                'parcel_price': 12,
                'type': self.t1.id
            },
            format='json'
        )
        self.assertNotEqual(res.status_code, 201)

        res = self.client.post(
            reverse('register_parcel'),
            {
                'name': 'neg2',
                'weight': 12,
                'parcel_price': -12,
                'type': self.t1.id
            },
            format='json'
        )
        self.assertNotEqual(res.status_code, 201)

        res = self.client.post(
            reverse('register_parcel'),
            {
                'name': 'neg3',
                'weight': 0,
                'parcel_price': 0,
                'type': self.t1.id
            },
            format='json'
        )
        self.assertEqual(res.status_code, 201)

    @patch("requests.get", return_value=Usd2RubMockResponse())
    def test_get_parsel_by_id(self, *args, **kwargs):
        obj = self.parcels[0].copy()
        res = self.client.post(
            reverse('register_parcel'),
            obj,
            format='json'
        )
        pid = res.json()['id']

        ret = self.client.get(
            reverse('parcel-detail', kwargs={'pk': pid}),
            format='json'
        )
        obj.update({
            'id': pid,
            'deliver_price': "Не рассчитано",
            'type': self.t1.name
        })
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.json(), obj)

        perodic_update.apply()
        USD2RUB = get_usd2rub()

        cache.delete_many(cache.keys('views.decorators.cache.cache_page.*'))

        ret = self.client.get(
            reverse('parcel-detail', kwargs={'pk': pid}),
            format='json'
        )
        obj.update({
            'deliver_price': (obj['weight'] / 2 + obj['parcel_price'] / 100) * USD2RUB
        })
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.json(), obj)

    def test_get_user_parsels(self, *args, **kwargs):
        client = APIClient()
        client.post(
            reverse('register_parcel'),
            self.parcels[0],
            format='json'
        )
        client.post(
            reverse('register_parcel'),
            self.parcels[1],
            format='json'
        )
        res = client.get(
            reverse('parcel-list'),
            format='json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['count'], 2)
        cache.delete_many(cache.keys('views.decorators.cache.cache_page.*'))
        cache.delete_many(cache.keys('views.decorators.cache.cache_header.*'))

        client.post(
            reverse('register_parcel'),
            self.parcels[2],
            format='json'
        )
        res = client.get(
            reverse('parcel-list'),
            format='json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['count'], 3)


class TypesTestCase(APITestCase):
    def setUp(self) -> None:
        self.t1 = ParcelTypeModel.objects.create(name='Одежда')
        self.t2 = ParcelTypeModel.objects.create(name='Электроника')
        self.t3 = ParcelTypeModel.objects.create(name='Разное')
        self.real = list(map(model_to_dict, [self.t1, self.t2, self.t3]))

    def test_get_types(self):
        self.real = list(map(model_to_dict, [self.t1, self.t2, self.t3]))
        cache.clear()
        res = self.client.get(
            reverse('parcel_types'),
            format='json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['results'], self.real)
