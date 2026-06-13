import pandas as pd
import numpy as np

np.random.seed(42)
n = 300

locations = ['City Center', 'Suburbs', 'Rural', 'Industrial Zone', 'Waterfront']
property_types = ['Apartment', 'Villa', 'Independent House', 'Studio']

loc_premium = {'City Center': 1.4, 'Suburbs': 1.1, 'Waterfront': 1.35, 'Rural': 0.8, 'Industrial Zone': 0.75}
type_factor = {'Apartment': 1.0, 'Villa': 1.5, 'Independent House': 1.25, 'Studio': 0.7}

area = np.random.randint(400, 4000, n)
bedrooms = np.random.choice([1, 2, 3, 4, 5], n, p=[0.1, 0.25, 0.35, 0.2, 0.1])
bathrooms = np.clip(bedrooms - np.random.choice([0, 1], n), 1, None)
age = np.random.randint(0, 30, n)
floors = np.random.randint(1, 20, n)
parking = np.random.choice([0, 1, 2], n, p=[0.2, 0.5, 0.3])
location = np.random.choice(locations, n, p=[0.25, 0.3, 0.15, 0.15, 0.15])
property_type = np.random.choice(property_types, n, p=[0.4, 0.2, 0.3, 0.1])

base = 3000000
price = (
    base
    + area * 3500
    + bedrooms * 800000
    + bathrooms * 400000
    - age * 60000
    + floors * 50000
    + parking * 150000
)
price = price.astype(float)
price *= np.array([loc_premium[l] for l in location])
price *= np.array([type_factor[t] for t in property_type])
price += np.random.normal(0, 500000, n)
price = np.clip(price, 1500000, None).astype(int)

df = pd.DataFrame({
    'area_sqft': area,
    'bedrooms': bedrooms,
    'bathrooms': bathrooms,
    'age_years': age,
    'floors': floors,
    'parking_spaces': parking,
    'location': location,
    'property_type': property_type,
    'price': price
})
df.to_csv('/home/claude/house-price-ml/data/house_prices.csv', index=False)
print(f"Generated {len(df)} rows")
print(df.head())
