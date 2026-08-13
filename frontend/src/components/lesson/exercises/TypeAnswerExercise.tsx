"use client";

import styles from "../Exercises.module.css";

interface TypeAnswerExerciseProps {
  question: string;
  sourceText?: string;
  selectedAnswer: { value: string } | null;
  onAnswerChange: (answer: { value: string }) => void;
  disabled: boolean;
}

export default function TypeAnswerExercise({
  question,
  sourceText,
  selectedAnswer,
  onAnswerChange,
  disabled,
}: TypeAnswerExerciseProps) {
  return (
    <div className={styles.inputContainer}>
      <div
        style={{
          backgroundColor: "var(--color-white)",
          border: "2px solid var(--color-border)",
          borderRadius: "16px",
          padding: "20px",
          fontSize: "18px",
          fontWeight: "600",
          marginBottom: "20px",
          color: "var(--color-charcoal)",
        }}
      >
        {sourceText || question}
      </div>

      <input
        type="text"
        className={styles.textInput}
        placeholder="Type your answer here..."
        value={selectedAnswer?.value || ""}
        onChange={(e) => onAnswerChange({ value: e.target.value })}
        disabled={disabled}
        autoFocus
      />
    </div>
  );
}
