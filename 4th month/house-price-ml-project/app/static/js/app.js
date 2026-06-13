document.getElementById('predict-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  const btn = document.querySelector('.btn-predict');
  btn.textContent = '⏳ Predicting...';
  btn.disabled = true;

  const formData = {
    area_sqft: parseFloat(document.getElementById('area_sqft').value),
    bedrooms: parseInt(document.getElementById('bedrooms').value),
    bathrooms: parseInt(document.getElementById('bathrooms').value),
    age_years: parseInt(document.getElementById('age_years').value),
    floors: parseInt(document.getElementById('floors').value),
    parking_spaces: parseInt(document.getElementById('parking_spaces').value),
    location: document.getElementById('location').value,
    property_type: document.getElementById('property_type').value
  };

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(formData)
    });
    const result = await response.json();
    const section = document.getElementById('result-section');
    section.style.display = 'block';

    if (result.success) {
      document.getElementById('price-value').textContent = result.formatted_price;
      document.getElementById('range-value').textContent = result.formatted_range;
      document.getElementById('error-msg').style.display = 'none';
    } else {
      document.getElementById('price-value').textContent = '—';
      document.getElementById('range-value').textContent = '';
      const errEl = document.getElementById('error-msg');
      errEl.textContent = '⚠️ ' + result.error;
      errEl.style.display = 'block';
    }
    section.scrollIntoView({behavior: 'smooth', block: 'nearest'});
  } catch (err) {
    alert('Network error: ' + err.message);
  } finally {
    btn.textContent = '🔍 Predict Price';
    btn.disabled = false;
  }
});
