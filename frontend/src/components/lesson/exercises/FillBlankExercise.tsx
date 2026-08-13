"use client";

import styles from "../Exercises.module.css";

interface FillBlankExerciseProps {
  question: string;
  selectedAnswer: { value: string } | null;
  onAnswerChange: (answer: { value: string }) => void;
  disabled: boolean;
}

export default function FillBlankExercise({
  question,
  selectedAnswer,
  onAnswerChange,
  disabled,
}: FillBlankExerciseProps) {
  const hasBlank = question.includes("___");

  if (!hasBlank) {
    // Fallback if blank is not specified as ___
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
          {question}
        </div>
        <input
          type="text"
          className={styles.textInput}
          placeholder="Fill in the blank"
          value={selectedAnswer?.value || ""}
          onChange={(e) => onAnswerChange({ value: e.target.value })}
          disabled={disabled}
          autoFocus
        />
      </div>
    );
  }

  // Split sentence by the blank placeholder
  const parts = question.split("___");

  return (
    <div style={{ textAlign: "center", width: "100%" }}>
      <div className={styles.blankSentence}>
        <span>{parts[0]}</span>
        <input
          type="text"
          style={{
            width: "120px",
            border: "none",
            borderBottom: "3px solid var(--color-charcoal)",
            outline: "none",
            fontSize: "20px",
            fontWeight: "700",
            textAlign: "center",
            padding: "2px 8px",
            backgroundColor: "transparent",
            color: "var(--color-blue)",
          }}
          placeholder="..."
          value={selectedAnswer?.value || ""}
          onChange={(e) => onAnswerChange({ value: e.target.value })}
          disabled={disabled}
          autoFocus
        />
        <span>{parts[1]}</span>
      </div>
    </div>
  );
}
