const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');

const APIClient = require(path.join(__dirname, 'api.js'));

test('getMockDiagnosis accepts a symptom array', () => {
  const result = APIClient.getMockDiagnosis(['fièvre', 'toux']);

  assert.equal(result.success, true);
  assert.ok(result.primary_disease);
  assert.ok(Array.isArray(result.top_3_diseases));
});

test('getMockDiagnosis accepts a plain symptom string', () => {
  const result = APIClient.getMockDiagnosis('mal à la tête');

  assert.equal(result.success, true);
  assert.ok(result.primary_disease);
});
