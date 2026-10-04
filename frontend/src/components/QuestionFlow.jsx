import { useState } from "react";

export default function QuestionFlow({ questions, onFinish, onSkipAll }) {
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState([]);

  if (!questions || questions.length === 0) return null;

  const current = questions[index];

  const answer = (value) => {
    const updated = [
      ...answers,
      {
        ingredient: current.ingredient,
        verb: current.verb,
        answer: value,
      },
    ];

    if (index + 1 >= questions.length) {
      onFinish(updated);
    } else {
      setAnswers(updated);
      setIndex(index + 1);
    }
  };

  return (
    <div
      key={current.id}
      className="mt-8 rounded-lg border border-clay bg-paper px-5 py-6 text-center"
    >
      <p className="text-xs text-ink/50">
        Question {index + 1} of {questions.length}
      </p>

      <h3 className="mt-3 font-display text-xl text-ink">{current.text}</h3>

      <div className="mt-5 flex justify-center gap-3">
        <button
          type="button"
          onClick={() => answer("yes")}
          className="rounded-md bg-basil px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-basil-dark"
        >
          Yes
        </button>

        <button
          type="button"
          onClick={() => answer("no")}
          className="rounded-md border border-clay px-5 py-2 text-sm font-medium text-ink transition-colors hover:border-basil"
        >
          No
        </button>

        <button
          type="button"
          onClick={() => answer("skip")}
          className="rounded-md border border-clay px-5 py-2 text-sm font-medium text-ink/60 transition-colors hover:border-basil"
        >
          Skip
        </button>
      </div>

      <button
        type="button"
        onClick={onSkipAll}
        className="mt-4 text-xs text-ink/40 underline hover:text-ink/70"
      >
        Skip all questions
      </button>
    </div>
  );
}