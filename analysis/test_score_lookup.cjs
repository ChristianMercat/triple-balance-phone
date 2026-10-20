/* Run with: node analysis/test_score_lookup.cjs (no npm dependencies). */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'tripleBalance.twee'), 'utf8');
const script = source.split('/* Score distribution lookup. */')[1]
  .split('/* End score distribution lookup. */')[0];
const context = { window: {}, engine: { extend: (_version, callback) => callback() } };
vm.runInNewContext(script, context);
const { distribution, percentile, minimumScore } = context.window.TripleBalanceScores;
const generated = JSON.parse(fs.readFileSync(path.join(__dirname, 'results/score-distribution.json'), 'utf8'));
assert.deepEqual(JSON.parse(JSON.stringify(distribution)), generated);
assert.equal(distribution.population, 'successful_paths');
assert.equal(distribution.totalPaths, 3597500);
assert.equal(percentile(0), 0);
assert.equal(percentile(53), 100);
assert.equal(percentile(100), 100);
assert.equal(Math.floor(percentile(37)), 97);
assert.equal(percentile(37), 100 * 3508388 / 3597500);
assert.deepEqual([0,20,40,60,90,100].map(minimumScore), [7.5,21,24.5,27,33,53]);

// Compare binary searches to simple linear reference calculations. Fractional
// scores between bins must use the preceding bin, without interpolation.
for (let score = 0; score <= 54; score += 0.25) {
  let count = 0;
  distribution.scores.forEach((value, index) => {
    if (value <= score) count = distribution.cumulativeCounts[index];
  });
  assert.equal(percentile(score), 100 * count / distribution.totalPaths);
}
for (let p = 0; p <= 100; p += 0.25) {
  const index = distribution.cumulativeCounts.findIndex(count =>
    100 * count / distribution.totalPaths >= p);
  assert.equal(minimumScore(p), distribution.scores[index]);
}
for (const score of distribution.scores) {
  assert.equal(minimumScore(percentile(score)), score);
}
for (const invalid of [NaN, Infinity, -Infinity, null, undefined, '37']) {
  assert.throws(() => percentile(invalid), /finite number/);
  assert.throws(() => minimumScore(invalid), /finite number/);
}
assert.throws(() => minimumScore(-1), /between 0 and 100/);
assert.throws(() => minimumScore(101), /between 0 and 100/);
assert.ok(Object.isFrozen(distribution));
assert.ok(Object.isFrozen(distribution.scores));
assert.ok(Object.isFrozen(distribution.cumulativeCounts));
console.log('Score lookup checks passed: generated data, CDF, quantiles, boundaries, ties and invalid inputs.');

// Exercise the actual End3 conditions, including scores exactly on each boundary.
const end3 = source.split(':: End3 ')[1].split('\n:: End4 ')[0];
const conditions = [...end3.matchAll(/^\[if (.+)\]$/gm)].map(match => match[1]);
assert.equal(conditions.length, 6);
const bandFor = score => conditions.flatMap((condition, index) =>
  vm.runInNewContext(condition, { score, window: context.window }) ? [index] : []);
for (let score = 7.5; score <= 53; score += 0.5) {
  assert.equal(bandFor(score).length, 1, `Exactly one assessment for ${score}`);
}
for (const [score, band] of [[7.5,5],[20.5,5],[21,4],[24,4],[24.5,3],
  [26.5,3],[27,2],[32.5,2],[33,1],[52,1],[53,0]]) {
  assert.deepEqual(bandFor(score), [band]);
}
assert.equal((end3.match(/"end\.end3\.scoreText"/g) || []).length, 1);
assert.ok(end3.includes('percentile: Math.floor(window.TripleBalanceScores.percentile(score))'));
assert.ok(!end3.includes('[if score > -5]'));
assert.match(end3, /\[continue\]\s*\{translated link: "common\.runAgain"/);
for (const language of ['en', 'de']) {
  const dictionary = JSON.parse(fs.readFileSync(path.join(root,'i18n',`${language}.json`),'utf8'));
  const text = dictionary.end.end3.scoreText;
  assert.ok(text.includes('{{score}}') && text.includes('{{percentile}}'));
  for (const band of ['outstanding','good','average','poor','barelySurvived']) {
    assert.ok(!('scoreText' in dictionary.end.end3[band]));
  }
}
console.log('End3 checks passed: exclusive quantile bands, all boundaries, shared score text and unconditional replay.');

// Success is based on this run's history, not on whether a score fits the chart.
const lookups = {};
const derived = source.split(':: StoryScript [script]\n')[1]
  .split('/* Score distribution lookup. */')[0];
vm.runInNewContext(derived, {engine: {
  extend: (_version, callback) => callback(),
  state: {setLookup: (name, callback) => {lookups[name] = callback;}}
}});
const successful = (trail, happy = 2, money = 10) => lookups.gameSuccessful(key => ({trail,happy,money})[key]);
assert.equal(successful(['Start','End1','End4','End6']), true);
assert.equal(successful(['Start','Game over','End4','End6']), false);
assert.equal(successful(['Start','Game over2','End4','End6']), false);
assert.equal(successful(['Start','End.Credits','End4','End6']), false);
assert.equal(successful(['Start','End1','Start','End4','End6']), false);
assert.equal(successful(['Start','End1','Game over','End6']), false);
assert.equal(successful(['Start','End1','End6'],0,10), false);
assert.equal(successful(['Start','End1','End6'],2,0), false);
assert.equal(successful(undefined), false);
console.log('Success-history checks passed: wins, both failures, unfinished runs, restart and depleted resources.');
