const BACKEND_URL = 'http://127.0.0.1:5000';
const form = document.getElementById('predictionForm');
const buttonText = document.getElementById('btnText');
const spinner = document.getElementById('loadingSpinner');
const resultCard = document.getElementById('resultCard');
const errorCard = document.getElementById('errorCard');
const recommendedCrop = document.getElementById('recommendedCrop');
const cropInfo = document.getElementById('cropInfo');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  buttonText.textContent = 'Processing Features...';
  spinner.classList.remove('hidden');
  resultCard.classList.add('hidden');
  errorCard.classList.add('hidden');

  const values = Object.fromEntries(new FormData(form));
  const payload = {
    Temperature: Number(values.temperature),
    Rainfall: Number(values.rainfall),
    Humidity: Number(values.humidity),
    Soil_Type: values.soil_type,
  };

  try {
    const response = await fetch(`${BACKEND_URL}/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Backend returned an error.');

    recommendedCrop.textContent = data.crop;
    cropInfo.textContent = `${data.confidence}% model confidence. Other possibilities: ${data.alternatives.map((item) => `${item.crop} (${item.confidence}%)`).join(', ')}.`;
    resultCard.classList.remove('hidden');
  } catch (requestError) {
    console.error('Prediction error:', requestError);
    errorCard.textContent = `${requestError.message} Make sure the sujal1 backend is running on port 5000.`;
    errorCard.classList.remove('hidden');
  } finally {
    buttonText.textContent = 'Analyze & Recommend Crop';
    spinner.classList.add('hidden');
  }
});
