// Set this to the deployed sujal1 backend URL when the API is hosted online.
const BACKEND_URL = 'http://127.0.0.1:5000';
const form = document.querySelector('#recommendation-form');
const result = document.querySelector('#result');
const error = document.querySelector('#error');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  error.textContent = '';
  const button = form.querySelector('button');
  button.disabled = true;
  button.querySelector('span').textContent = 'Reading conditions...';
  try {
    const response = await fetch(`${BACKEND_URL}/api/recommend`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(Object.fromEntries(new FormData(form))),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The model could not make a recommendation.');
    result.innerHTML = `<div class="answer"><span>BEST FIT FOR THIS PLOT</span><h2>${data.crop}</h2><p>${data.confidence}% model confidence</p><div class="meter"><i style="width:${data.confidence}%"></i></div><small>OTHER POSSIBILITIES</small>${data.alternatives.map(item => `<div class="alternative"><b>${item.crop}</b><em>${item.confidence}%</em></div>`).join('')}</div>`;
  } catch (requestError) {
    error.textContent = `${requestError.message} Check that the sujal1 backend is running.`;
  } finally {
    button.disabled = false;
    button.querySelector('span').textContent = 'Find my crop';
  }
});
