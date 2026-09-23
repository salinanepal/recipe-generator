import { useState } from "react";

const MAX_QUESTIONS = 6;

// how relevant a candidate currently is, given everything the user has
// answered so far (recalculated fresh on every answer)
function scoreCandidate(candidate, answeredMap) {
  let confirmed = 0;
  let declined = 0;
  let answered = 0;

  for (const ingredient of candidate.extra_ingredients) {
    if (ingredient in answeredMap) {
      answered += 1;
      if (answeredMap[ingredient]) confirmed += 1;
      else declined += 1;
    }
  }

  const feedbackScore = answered > 0 ? (confirmed - declined) / answered : 0;
  const gapPenalty = candidate.gap_size * 0.01; // small tiebreaker, favors fewer unknowns
  return feedbackScore - gapPenalty;
}

// which ingredient to ask about next: score every candidate right now,
// then take the next un-asked question from whichever is currently on top
function getNextQuestion(candidates, answeredMap, askedSet) {
  const ranked = [...candidates].sort(
    (a, b) => scoreCandidate(b, answeredMap) - scoreCandidate(a, answeredMap) || a.gap_size - b.gap_size
  );

  for (const candidate of ranked) {
    const next = (candidate.questions || []).find(ing => !askedSet.has(ing));
    if (next) return next;
  }
  return null; // nothing left to ask, anywhere
}

export default function RecommendationWalk({ candidates, availableStyles, onFinalize }) {
  const [selectedStyle, setSelectedStyle] = useState(undefined); // undefined = not chosen yet, null = "no preference"
  const [answeredMap, setAnsweredMap] = useState({});
  const [askedSet, setAskedSet] = useState(new Set());
  const [questionsAsked, setQuestionsAsked] = useState(0);

  const styleFiltered = selectedStyle
    ? candidates.filter(c => c.cooking_methods?.includes(selectedStyle))
    : candidates;

  function handleStyleChoice(style) {
    setSelectedStyle(style ?? null);
  }

  function handleAnswer(ingredient, included) {
    setAnsweredMap(prev => ({ ...prev, [ingredient]: included }));
    setAskedSet(prev => new Set(prev).add(ingredient));
    setQuestionsAsked(prev => prev + 1);
  }

  // --- Phase 1: cooking style ---
  if (selectedStyle === undefined) {
    return (
      <div className="card">
        <h2 className="font-display text-lg text-ink">How do you want to cook it?</h2>
        <div className="mt-4 flex flex-wrap gap-2">
          {availableStyles.map(style => (
            <button key={style} onClick={() => handleStyleChoice(style)} className="btn-primary">
              {style}
            </button>
          ))}
          <button onClick={() => handleStyleChoice(null)} className="rounded-md border border-clay px-4 py-2 text-sm">
            No preference
          </button>
        </div>
      </div>
    );
  }

  if (styleFiltered.length === 0) {
    return <p className="text-sm text-ink/60">No matching recipes found for that style.</p>;
  }

  // --- Phase 2: questions (dynamic, cross-candidate, capped) ---
  const nextQuestion =
    questionsAsked < MAX_QUESTIONS
      ? getNextQuestion(styleFiltered, answeredMap, askedSet)
      : null;

  if (nextQuestion) {
    return (
      <div className="card">
        <h2 className="font-display text-lg text-ink">Add {nextQuestion}?</h2>
        <div className="mt-4 flex gap-3">
          <button onClick={() => handleAnswer(nextQuestion, true)} className="btn-primary">Yes</button>
          <button onClick={() => handleAnswer(nextQuestion, false)} className="rounded-md border border-clay px-4 py-2 text-sm">No</button>
        </div>
      </div>
    );
  }

  // --- Phase 3: final top 3 ---
  const topThree = [...styleFiltered]
    .sort((a, b) => scoreCandidate(b, answeredMap) - scoreCandidate(a, answeredMap) || a.gap_size - b.gap_size)
    .slice(0, 3);

  const confirmedIngredients = Object.keys(answeredMap).filter(k => answeredMap[k]);
  const declinedIngredients = Object.keys(answeredMap).filter(k => !answeredMap[k]);

  return (
    <div>
      <h2 className="font-display text-2xl">Recommended Nepali Recipes</h2>
      <div className="mt-4 space-y-3">
        {topThree.map(candidate => (
          <button
            key={candidate.name}
            type="button"
            onClick={() =>
              onFinalize({
                recipeName: candidate.name,
                cookingStyle: selectedStyle,
                confirmedIngredients,
                declinedIngredients,
              })
            }
            className="w-full rounded-lg border border-clay bg-paper p-4 text-left hover:border-basil transition-colors"
          >
            <div className="font-semibold text-lg">{candidate.name}</div>
          </button>
        ))}
      </div>
    </div>
  );
}