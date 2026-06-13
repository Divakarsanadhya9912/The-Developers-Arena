"""
Test Suite - House Price Prediction System
Run: python -m pytest tests/ -v
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_preprocessing import validate_data, engineer_features, load_data
from model_inference import validate_input, prepare_input, VALID_LOCATIONS, VALID_PROPERTY_TYPES


# ─── Data Preprocessing Tests ────────────────────────────────────────────────

class TestDataPreprocessing:

    def make_sample_df(self, n=10):
        return pd.DataFrame({
            'area_sqft': np.random.randint(500, 3000, n),
            'bedrooms': np.random.randint(1, 5, n),
            'bathrooms': np.random.randint(1, 4, n),
            'age_years': np.random.randint(0, 20, n),
            'floors': np.random.randint(1, 15, n),
            'parking_spaces': np.random.randint(0, 3, n),
            'location': np.random.choice(VALID_LOCATIONS, n),
            'property_type': np.random.choice(VALID_PROPERTY_TYPES, n),
            'price': np.random.randint(3000000, 30000000, n)
        })

    def test_validate_removes_negative_price(self):
        df = self.make_sample_df()
        df.loc[0, 'price'] = -100
        result = validate_data(df)
        assert (result['price'] > 0).all()

    def test_validate_drops_na(self):
        df = self.make_sample_df()
        df.loc[2, 'area_sqft'] = np.nan
        result = validate_data(df)
        assert result.isnull().sum().sum() == 0

    def test_engineer_features_adds_columns(self):
        df = self.make_sample_df()
        df_eng = engineer_features(df)
        for col in ['room_ratio', 'total_rooms', 'is_new', 'has_parking', 'size_category']:
            assert col in df_eng.columns, f"Missing engineered feature: {col}"

    def test_is_new_flag_correct(self):
        df = self.make_sample_df()
        df['age_years'] = [3, 10, 0, 6, 5, 15, 2, 8, 4, 1]
        df_eng = engineer_features(df)
        expected_new = df['age_years'] <= 5
        assert (df_eng['is_new'] == expected_new.astype(int)).all()

    def test_size_category_correct(self):
        df = self.make_sample_df(4)
        df['area_sqft'] = [600, 1200, 2000, 3000]
        df_eng = engineer_features(df)
        cats = df_eng['size_category'].tolist()
        assert cats[0] == 'Small'
        assert cats[1] == 'Medium'
        assert cats[2] == 'Large'
        assert cats[3] == 'Luxury'


# ─── Input Validation Tests ───────────────────────────────────────────────────

class TestInputValidation:

    def valid_input(self):
        return {
            'area_sqft': 1200,
            'bedrooms': 3,
            'bathrooms': 2,
            'age_years': 5,
            'floors': 5,
            'parking_spaces': 1,
            'location': 'City Center',
            'property_type': 'Apartment'
        }

    def test_valid_input_passes(self):
        ok, msg = validate_input(self.valid_input())
        assert ok is True
        assert msg == ""

    def test_invalid_area_too_small(self):
        data = self.valid_input()
        data['area_sqft'] = 50
        ok, msg = validate_input(data)
        assert ok is False
        assert 'Area' in msg

    def test_invalid_area_too_large(self):
        data = self.valid_input()
        data['area_sqft'] = 15000
        ok, msg = validate_input(data)
        assert ok is False

    def test_invalid_bedrooms_zero(self):
        data = self.valid_input()
        data['bedrooms'] = 0
        ok, msg = validate_input(data)
        assert ok is False

    def test_invalid_location(self):
        data = self.valid_input()
        data['location'] = 'Mars'
        ok, msg = validate_input(data)
        assert ok is False
        assert 'Location' in msg

    def test_invalid_property_type(self):
        data = self.valid_input()
        data['property_type'] = 'Treehouse'
        ok, msg = validate_input(data)
        assert ok is False

    def test_prepare_input_shape(self):
        df = prepare_input(self.valid_input())
        assert len(df) == 1
        assert 'area_sqft' in df.columns
        assert 'room_ratio' in df.columns
        assert 'size_category' in df.columns

    @pytest.mark.parametrize("location", VALID_LOCATIONS)
    def test_all_locations_valid(self, location):
        data = self.valid_input()
        data['location'] = location
        ok, _ = validate_input(data)
        assert ok is True

    @pytest.mark.parametrize("ptype", VALID_PROPERTY_TYPES)
    def test_all_property_types_valid(self, ptype):
        data = self.valid_input()
        data['property_type'] = ptype
        ok, _ = validate_input(data)
        assert ok is True


# ─── Edge Cases ───────────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_luxury_property(self):
        data = {
            'area_sqft': 5000, 'bedrooms': 5, 'bathrooms': 4,
            'age_years': 1, 'floors': 20, 'parking_spaces': 2,
            'location': 'Waterfront', 'property_type': 'Villa'
        }
        ok, msg = validate_input(data)
        assert ok is True

    def test_studio_apartment(self):
        data = {
            'area_sqft': 400, 'bedrooms': 1, 'bathrooms': 1,
            'age_years': 30, 'floors': 1, 'parking_spaces': 0,
            'location': 'Rural', 'property_type': 'Studio'
        }
        ok, msg = validate_input(data)
        assert ok is True

    def test_age_boundary_zero(self):
        data = {
            'area_sqft': 1000, 'bedrooms': 2, 'bathrooms': 2,
            'age_years': 0, 'floors': 3, 'parking_spaces': 1,
            'location': 'Suburbs', 'property_type': 'Apartment'
        }
        ok, _ = validate_input(data)
        assert ok is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
