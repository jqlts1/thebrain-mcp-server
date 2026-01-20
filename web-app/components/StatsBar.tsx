import React from 'react';

interface StatsBarProps {
    newCount: number;
    dueCount: number;
    doneCount: number;
}

export default function StatsBar({ newCount, dueCount, doneCount }: StatsBarProps) {
    return (
        <header className="stats-bar">
            <div className="stat">
                <span className="stat-value">{newCount}</span>
                <span className="stat-label">新卡片</span>
            </div>
            <div className="stat">
                <span className="stat-value">{dueCount}</span>
                <span className="stat-label">待复习</span>
            </div>
            <div className="stat">
                <span className="stat-value">{doneCount}</span>
                <span className="stat-label">已完成</span>
            </div>
        </header>
    );
}
