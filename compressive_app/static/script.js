document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('predictForm');
  const results = document.getElementById('results');

  function showError(msg) {
    results.innerHTML = `<p style="color:red">${msg}</p>`;
  }

  function parseNumbersFromString(s) {
    // Find all floats (handles 1.23, -1.23, 1e-3, etc.)
    const re = /[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?/g;
    const matches = s.match(re);
    return matches ? matches.map(Number) : [];
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    results.innerHTML = '';

    const numSamples = Number(form.num_samples.value);
    const numPredictions = Number(form.num_predictions.value);
    const raw = form.ctm_values.value || '';

    const values = parseNumbersFromString(raw);
    if (values.length === 0) {
      showError('No numeric CTM values found. Use spaces, commas or hyphens as separators.');
      return;
    }
    if (numSamples && values.length !== numSamples) {
      // warn but continue — adjust behavior if you must enforce exact match
      results.innerHTML = `<p style="color:orange">Warning: num_samples (${numSamples}) does not match parsed values (${values.length}). Continuing with parsed values.</p>`;
    }

    try {
      const resp = await fetch(window.location.href, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '' },
        body: JSON.stringify({
          num_samples: numSamples,
          ctm_values: values,
          num_predictions: numPredictions
        })
      });
      const data = await resp.json();
      if (!resp.ok) {
        showError(data.error || 'Server error');
        return;
      }
      results.innerHTML += `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    } catch (err) {
      showError('Network or parsing error: ' + err.message);
    }
  });
});