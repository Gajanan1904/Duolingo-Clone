"use client";

import styles from "../Exercises.module.css";

interface MultipleChoiceExerciseProps {
  options: string[];
  selectedAnswer: { value: string } | null;
  onAnswerChange: (answer: { value: string }) => void;
  disabled: boolean;
}

export default function MultipleChoiceExercise({
  options,
  selectedAnswer,
  onAnswerChange,
  disabled,
}: MultipleChoiceExerciseProps) {
  return (
    <div className={styles.mcGrid}>
      {options.map((option, index) => {
        const isSelected = selectedAnswer?.value === option;
        return (
          <button
            key={option}
            onClick={() => onAnswerChange({ value: option })}
            className={`${styles.mcCard} ${isSelected ? styles.mcCardSelected : ""}`}
            disabled={disabled}
            type="button"
          >
            <div className={`${styles.mcNumber} ${isSelected ? styles.mcNumberSelected : ""}`}>
              {index + 1}
            </div>
            <div>{option}</div>
          </button>
        );
      })}
    </div>
  );
}
