import os
import unittest

from mensor.measures.registry import MeasureRegistry
from mensor.providers.pandas import PandasMeasureProvider


class PandasMeasureProviderTests(unittest.TestCase):

    def setUp(self):
        self.registry = MeasureRegistry()

        data_dir = os.path.join(os.path.dirname(__file__), 'data')

        people = (
            PandasMeasureProvider(
                name='people',
                data=os.path.join(data_dir, 'people.csv')
            )
            .add_identifier('person', expr='id', role='primary')
            .add_identifier('geography', expr='id_country', role='foreign')
            .add_dimension('name')
            .add_measure('age')
        )
        self.registry.register(people)

        transactions = (
            PandasMeasureProvider(
                name='transactions',
                data=os.path.join(data_dir, 'transactions.csv')
            )
            .add_identifier('transaction', expr='id', role='primary')
            .add_identifier('person:buyer', expr='id_buyer', role='foreign')
            .add_identifier('person:seller', expr='id_seller', role='foreign')
            .add_measure('value')
        )
        self.registry.register(transactions)

        self.registry.show()

    def test_simple(self):
        df = self.registry.evaluate(
            'transaction',
            measures=['person:seller/age'],
            segment_by=['person:buyer/name'],
            where=None
        )

        self.assertGreater(len(df), 0)
        self.assertEqual(
            set(df.columns),
            set([
                'person:seller/age|normal|count',
                'person:seller/age|normal|sos',
                'person:seller/age|normal|sum',
                'person:buyer/name'
            ])
        )
        self.assertFalse(df.duplicated('person:buyer/name').any())
