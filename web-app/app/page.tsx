'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { fetchAPI, Card, CardDetail } from '@/lib/api';
import StatsBar from '@/components/StatsBar';
import Flashcard from '@/components/Flashcard';
import RatingButtons from '@/components/RatingButtons';
import CompletionMessage from '@/components/CompletionMessage';

export default function Home() {
  const [cards, setCards] = useState<Card[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentDetail, setCurrentDetail] = useState<CardDetail | null>(null);
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [reviewedCount, setReviewedCount] = useState(0);

  // 加载到期卡片
  const loadDueCards = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchAPI<{ cards: Card[] }>('/api/srs/cards/due?limit=50');
      setCards(data.cards || []);
      setCurrentIndex(0);
      setReviewedCount(0);
    } catch (error) {
      console.error('Failed to load cards:', error);
      if (error instanceof Error && error.message === '需要 API Key') {
        const key = prompt('请输入 TheBrain API Key 或 Web 访问密码:');
        if (key) {
          localStorage.setItem('thebrain_api_key', key);
          loadDueCards(); // 重试
        }
      }
    } finally {
      setLoading(false);
    }
  }, []);

  // 当当前卡片变化时，加载详情
  useEffect(() => {
    const card = cards[currentIndex];
    if (card) {
      setFlipped(false);
      setCurrentDetail(null);

      // 并行获取详情和关联图谱
      const fetchDetail = async () => {
        try {
          const [cardData, graphData] = await Promise.all([
            fetchAPI<CardDetail>(`/api/srs/cards/${card.thought_id}`),
            fetchAPI<any>(`/api/thoughts/${card.thought_id}/graph?siblings=true`)
          ]);
          setCurrentDetail({ ...cardData, graph: graphData });
        } catch (error) {
          console.error('Failed to load detail:', error);
        }
      };

      fetchDetail();
    }
  }, [cards, currentIndex]);

  // 初始化加载
  useEffect(() => {
    loadDueCards();
  }, [loadDueCards]);

  // 处理复习提交
  const handleRate = async (quality: number) => {
    const card = cards[currentIndex];
    if (!card || submitting) return;

    try {
      setSubmitting(true);
      await fetchAPI(`/api/srs/cards/${card.thought_id}/review`, {
        method: 'POST',
        body: JSON.stringify({ quality }),
      });

      setReviewedCount((prev) => prev + 1);
      setCurrentIndex((prev) => prev + 1);
    } catch (error) {
      console.error('Failed to submit review:', error);
      alert('提交失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (loading || cards.length === 0 || currentIndex >= cards.length) return;

      switch (e.key) {
        case ' ':
        case 'Enter':
          e.preventDefault();
          setFlipped((prev) => !prev);
          break;
        case '1':
          handleRate(0);
          break;
        case '2':
          handleRate(1);
          break;
        case '3':
          handleRate(2);
          break;
        case '4':
          handleRate(3);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [loading, cards, currentIndex, submitting]); // Dependencies updated

  if (loading) {
    return (
      <div className="container">
        <div className="flex items-center justify-center h-full text-text-secondary">
          加载中...
        </div>
      </div>
    );
  }

  const currentCard = cards[currentIndex];
  const isComplete = !currentCard && cards.length > 0 && currentIndex >= cards.length;
  const newCount = cards.filter(c => c.state === 'new').length;
  const remaining = cards.length - currentIndex;

  return (
    <div className="container">
      <StatsBar
        newCount={newCount}
        dueCount={remaining > 0 ? remaining : 0}
        doneCount={reviewedCount}
      />

      {isComplete ? (
        <CompletionMessage />
      ) : currentCard ? (
        <>
          <Flashcard
            card={currentCard}
            detail={currentDetail}
            flipped={flipped}
            onFlip={() => setFlipped(!flipped)}
          />

          <RatingButtons
            onRate={handleRate}
            disabled={submitting}
            intervals={currentCard.next_intervals || currentDetail?.next_intervals}
          />
        </>
      ) : (
        <div className="completion-message">
          <p>没有待复习的卡片</p>
        </div>
      )}
    </div>
  );
}
