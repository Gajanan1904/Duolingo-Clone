"use client";

import { useEffect, useState } from "react";
import styles from "../Exercises.module.css";

interface WordBankExerciseProps {
  words: string[];
  selectedAnswer: { words: string[] } | null;
  onAnswerChange: (answer: { words: string[] }) => void;
  disabled: boolean;
}

export default function WordBankExercise({
  words,
  selectedAnswer,
  onAnswerChange,
  disabled,
}: WordBankExerciseProps) {
  // Store indices to handle duplicate words correctly
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);

  // Sync state if selectedAnswer is reset by parent
  useEffect(() => {
    if (!selectedAnswer || !selectedAnswer.words || selectedAnswer.words.length === 0) {
      setSelectedIndices([]);
    }
  }, [selectedAnswer]);

  const handleWordTap = (index: number) => {
    if (disabled) return;
    if (selectedIndices.includes(index)) return; // already used

    const newIndices = [...selectedIndices, index];
    setSelectedIndices(newIndices);
    onAnswerChange({
      words: newIndices.map((idx) => words[idx]),
    });
  };

  const handleRemoveWord = (trayIndex: number) => {
    if (disabled) return;
    
    const newIndices = [...selectedIndices];
    newIndices.splice(trayIndex, 1);
    setSelectedIndices(newIndices);
    onAnswerChange({
      words: newIndices.map((idx) => words[idx]),
    });
  };

  return (
    <div className={styles.wordBankContainer}>
      {/* Answer Tray */}
      <div className={styles.answerTray}>
        {selectedIndices.length === 0 ? (
          <span style={{ color: "var(--color-muted)", fontWeight: "500", marginLeft: "12px" }}>
            Tap words to build your answer
          </span>
        ) : (
          selectedIndices.map((wordIdx, trayIdx) => (
            <button
              key={`${words[wordIdx]}-${trayIdx}`}
              type="button"
              className={styles.wordToken}
              onClick={() => handleRemoveWord(trayIdx)}
              disabled={disabled}
            >
              {words[wordIdx]}
            </button>
          ))
        )}
      </div>

      {/* Word Pool */}
      <div className={styles.wordPool}>
        {words.map((word, index) => {
          const isUsed = selectedIndices.includes(index);
          return (
            <button
              key={`${word}-${index}`}
              type="button"
              className={`${styles.wordToken} ${isUsed ? styles.wordTokenUsed : ""}`}
              onClick={() => handleWordTap(index)}
              disabled={disabled || isUsed}
            >
              {word}
            </button>
          );
        })}
      </div>
    </div>
  );
}
