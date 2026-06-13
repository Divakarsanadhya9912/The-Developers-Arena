# Data Dictionary — house_prices.csv

## Raw Features

| Column          | Type    | Range / Values                                          | Description                          |
|-----------------|---------|----------------------------------------------------------|--------------------------------------|
| area_sqft       | int     | 400 – 4000                                               | Built-up area in square feet         |
| bedrooms        | int     | 1 – 5                                                    | Number of bedrooms                   |
| bathrooms       | int     | 1 – 5                                                    | Number of bathrooms                  |
| age_years       | int     | 0 – 30                                                   | Age of property in years             |
| floors          | int     | 1 – 20                                                   | Floor number of the unit             |
| parking_spaces  | int     | 0 – 2                                                    | Number of covered parking spaces     |
| location        | string  | City Center, Suburbs, Rural, Industrial Zone, Waterfront | Area/locality of the property        |
| property_type   | string  | Apartment, Villa, Independent House, Studio              | Category of property                 |
| price           | int     | 1,500,000+                                               | Actual sale price in Indian Rupees   |

## Engineered Features (added in preprocessing)

| Column          | Type    | Description                                              |
|-----------------|---------|----------------------------------------------------------|
| room_ratio      | float   | bathrooms / bedrooms                                     |
| total_rooms     | int     | bedrooms + bathrooms                                     |
| is_new          | int     | 1 if age_years ≤ 5, else 0                               |
| has_parking     | int     | 1 if parking_spaces > 0, else 0                          |
| size_category   | string  | Small (<800), Medium (800–1500), Large (1500–2500), Luxury(2500+) |

## Target Variable

| Column | Type | Description                |
|--------|------|----------------------------|
| price  | int  | Property sale price in INR |

## Dataset Stats
- Total rows: 300
- Train / Test split: 240 / 60 (80/20)
- No missing values
