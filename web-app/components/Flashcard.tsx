import React from 'react';
import { Card, CardDetail } from '@/lib/api';
import OutlineView from './OutlineView';

interface FlashcardProps {
    card: Card;
    detail: CardDetail | null;
    flipped: boolean;
    onFlip: () => void;
}

export default function Flashcard({ card, detail, flipped, onFlip }: FlashcardProps) {
    return (
        <div className="flashcard-area">
            <div
                className={`flashcard ${flipped ? 'flipped' : ''}`}
                onClick={onFlip}
            >
                {/* 正面 */}
                <div className="card-face card-front">
                    <div className="card-content">
                        <h1 className="card-title">{card.name}</h1>
                        {detail?.graph?.tags && (
                            <div className="card-tags">
                                {detail.graph.tags.map((tag) => (
                                    <span key={tag.id} className="tag">
                                        {tag.name}
                                    </span>
                                ))}
                            </div>
                        )}
                        <div className="card-hint">点击卡片查看答案</div>
                    </div>
                </div>

                {/* 背面 */}
                <div className="card-face card-back">
                    <div className="card-content">
                        <h2 className="card-title-small">{card.name}</h2>

                        <OutlineView graph={detail?.graph} currentName={card.name} />

                        <div className="card-note">
                            <div className="note-label">📝 笔记</div>
                            <div className="note-content">
                                {detail?.note || (detail?.note_error ? `加载失败: ${detail.note_error}` : '')}
                            </div>
                        </div>

                        <div className="card-meta">
                            {detail?.graph?.activeThought?.label && (
                                <span className="meta-item">📋 {detail.graph.activeThought.label}</span>
                            )}
                            <span className="meta-item">⏰ 间隔: {card.interval_days}天</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
