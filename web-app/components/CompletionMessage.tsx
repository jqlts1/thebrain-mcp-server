import React from 'react';

export default function CompletionMessage() {
    return (
        <div className="completion-message">
            <div className="completion-icon">🎉</div>
            <h2>今日复习完成！</h2>
            <p>你已完成所有待复习的卡片</p>
        </div>
    );
}
