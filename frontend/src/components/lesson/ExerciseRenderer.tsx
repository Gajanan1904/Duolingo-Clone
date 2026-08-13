"use client";

import { Exercise } from "../../types/api";
import MultipleChoiceExercise from "./exercises/MultipleChoiceExercise";
import TranslateExercise from "./exercises/TranslateExercise";
import WordBankExercise from "./exercises/WordBankExercise";
import MatchPairsExercise from "./exercises/MatchPairsExercise";
import FillBlankExercise from "./exercises/FillBlankExercise";
import TypeAnswerExercise from "./exercises/TypeAnswerExercise";

interface ExerciseRendererProps {
  exercise: Exercise;
  selectedAnswer: any;
  onAnswerChange: (value: any) => void;
  disabled: boolean;
}

export default function ExerciseRenderer({
  exercise,
  selectedAnswer,
  onAnswerChange,
  disabled,
}: ExerciseRendererProps) {
  switch (exercise.type) {
    case "multiple_choice":
      return (
        <MultipleChoiceExercise
          options={exercise.data.options || []}
          selectedAnswer={selectedAnswer}
          onAnswerChange={onAnswerChange}
          disabled={disabled}
        />
      );
    case "translate":
      return (
        <TranslateExercise
          sourceText={exercise.data.source_text || ""}
          selectedAnswer={selectedAnswer}
          onAnswerChange={onAnswerChange}
          disabled={disabled}
        />
      );
    case "word_bank":
      return (
        <WordBankExercise
          words={exercise.data.words || []}
          selectedAnswer={selectedAnswer}
          onAnswerChange={onAnswerChange}
          disabled={disabled}
        />
      );
    case "match_pairs":
      return (
        <MatchPairsExercise
          pairs={exercise.data.pairs || []}
          selectedAnswer={selectedAnswer}
          onAnswerChange={onAnswerChange}
          disabled={disabled}
        />
      );
    case "fill_blank":
      return (
        <FillBlankExercise
          question={exercise.question}
          selectedAnswer={selectedAnswer}
          onAnswerChange={onAnswerChange}
          disabled={disabled}
        />
      );
    case "type_answer":
      return (
        <TypeAnswerExercise
          question={exercise.question}
          sourceText={exercise.data.source_text}
          selectedAnswer={selectedAnswer}
          onAnswerChange={onAnswerChange}
          disabled={disabled}
        />
      );
    default:
      return (
        <div style={{ color: "var(--color-red)", fontWeight: "700" }}>
          Unknown exercise type: {exercise.type}
        </div>
      );
  }
}
