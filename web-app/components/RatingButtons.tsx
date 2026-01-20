import React from 'react';

interface RatingButtonsProps {
    onRate: (quality: number) => void;
    disabled?: boolean;
    intervals?: number[];
}

export default function RatingButtons({ onRate, disabled, intervals = [1, 2, 5, 10] }: RatingButtonsProps) {
    const qualities = [
        { label: 'Again', value: 0, class: 'rating-again' },
        { label: 'Hard', value: 1, class: 'rating-hard' },
        { label: 'Good', value: 2, class: 'rating-good' },
        { label: 'Easy', value: 3, class: 'rating-easy' },
    ];

    return (
        <footer className="rating-buttons">
            {qualities.map((q, idx) => (
                <button
                    key={q.value}
                    className={`rating-btn ${q.class}`}
                    onClick={(e) => {
                        e.stopPropagation();
                        onRate(q.value);
                    }}
                    disabled={disabled}
                >
                    <span className="rating-name">{q.label}</span>
                    <span className="rating-interval">{intervals[idx] || '?'}d</span>
                </button>
            ))}
        </footer>
    );
}
