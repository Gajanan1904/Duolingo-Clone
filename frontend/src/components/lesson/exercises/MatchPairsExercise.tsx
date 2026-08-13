"use client";

import { useEffect, useState } from "react";
import styles from "../Exercises.module.css";

interface PairItem {
  id: string;
  left: string;
  right: string;
}

interface MatchPairsExerciseProps {
  pairs: PairItem[];
  selectedAnswer: { pairs: { [key: string]: string } } | null;
  onAnswerChange: (answer: { pairs: { [key: string]: string } }) => void;
  disabled: boolean;
}

export default function MatchPairsExercise({
  pairs,
  selectedAnswer,
  onAnswerChange,
  disabled,
}: MatchPairsExerciseProps) {
  const [shuffledLeft, setShuffledLeft] = useState<PairItem[]>([]);
  const [shuffledRight, setShuffledRight] = useState<string[]>([]);
  
  const [selectedLeft, setSelectedLeft] = useState<string | null>(null); // holds pair.id
  const [selectedRight, setSelectedRight] = useState<string | null>(null); // holds text
  
  const [matches, setMatches] = useState<{ [key: string]: string }>({}); // pair.id -> text

  // Initialize and shuffle columns
  useEffect(() => {
    setShuffledLeft([...pairs].sort(() => Math.random() - 0.5));
    setShuffledRight(pairs.map((p) => p.right).sort(() => Math.random() - 0.5));
    setMatches({});
    setSelectedLeft(null);
    setSelectedRight(null);
  }, [pairs]);

  // Sync state if selectedAnswer is reset by parent
  useEffect(() => {
    if (!selectedAnswer || !selectedAnswer.pairs || Object.keys(selectedAnswer.pairs).length === 0) {
      setMatches({});
      setSelectedLeft(null);
      setSelectedRight(null);
    }
  }, [selectedAnswer]);

  const handleLeftTap = (id: string) => {
    if (disabled) return;
    if (matches[id]) return; // already matched

    if (selectedLeft === id) {
      setSelectedLeft(null);
    } else {
      setSelectedLeft(id);
      // Check if we can form a match
      if (selectedRight) {
        makeMatch(id, selectedRight);
      }
    }
  };

  const handleRightTap = (text: string) => {
    if (disabled) return;
    
    // Check if this right option is already matched
    const isAlreadyMatched = Object.values(matches).includes(text);
    if (isAlreadyMatched) return;

    if (selectedRight === text) {
      setSelectedRight(null);
    } else {
      setSelectedRight(text);
      // Check if we can form a match
      if (selectedLeft) {
        makeMatch(selectedLeft, text);
      }
    }
  };

  const makeMatch = (leftId: string, rightText: string) => {
    const newMatches = { ...matches, [leftId]: rightText };
    setMatches(newMatches);
    setSelectedLeft(null);
    setSelectedRight(null);
    
    onAnswerChange({ pairs: newMatches });
  };

  const handleRemoveMatch = (leftId: string) => {
    if (disabled) return;
    
    const newMatches = { ...matches };
    delete newMatches[leftId];
    setMatches(newMatches);
    onAnswerChange({ pairs: newMatches });
  };

  return (
    <div className={styles.matchContainer}>
      {/* Left Column */}
      <div className={styles.matchCol}>
        {shuffledLeft.map((item) => {
          const isSelected = selectedLeft === item.id;
          const isMatched = !!matches[item.id];
          return (
            <button
              key={`left-${item.id}`}
              type="button"
              className={`${styles.matchItem} ${
                isMatched ? styles.matchItemMatched : isSelected ? styles.matchItemSelected : ""
              }`}
              onClick={() => (isMatched ? handleRemoveMatch(item.id) : handleLeftTap(item.id))}
              disabled={disabled}
            >
              {item.left}
            </button>
          );
        })}
      </div>

      {/* Right Column */}
      <div className={styles.matchCol}>
        {shuffledRight.map((rightText, index) => {
          const isSelected = selectedRight === rightText;
          const isMatched = Object.values(matches).includes(rightText);
          
          // Find matching left id to support undoing match on click
          const matchedLeftId = Object.keys(matches).find((key) => matches[key] === rightText);

          return (
            <button
              key={`right-${rightText}-${index}`}
              type="button"
              className={`${styles.matchItem} ${
                isMatched ? styles.matchItemMatched : isSelected ? styles.matchItemSelected : ""
              }`}
              onClick={() =>
                isMatched && matchedLeftId
                  ? handleRemoveMatch(matchedLeftId)
                  : handleRightTap(rightText)
              }
              disabled={disabled}
            >
              {rightText}
            </button>
          );
        })}
      </div>
    </div>
  );
}
