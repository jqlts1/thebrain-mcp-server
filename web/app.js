/**
 * TheBrain SRS 闪卡应用
 */

// API 配置
const API_BASE = window.location.origin;
const API_KEY = localStorage.getItem('thebrain_api_key') || '';

// 状态
let cards = [];
let currentIndex = 0;
let currentCard = null;
let reviewedCount = 0;

// DOM 元素
const flashcard = document.getElementById('flashcard');
const cardTitle = document.getElementById('card-title');
const cardTitleBack = document.getElementById('card-title-back');
const cardTags = document.getElementById('card-tags');
const cardNote = document.getElementById('note-content');
const cardLabel = document.getElementById('card-label');
const cardInterval = document.getElementById('card-interval');
const ratingButtons = document.getElementById('rating-buttons');
const completionMessage = document.getElementById('completion-message');

// 大纲元素
const outlineParents = document.querySelector('#outline-parents .outline-nodes');
const outlineChildren = document.querySelector('#outline-children .outline-nodes');
const currentNode = document.getElementById('current-node');
const siblingLeft = document.getElementById('sibling-left');
const siblingRight = document.getElementById('sibling-right');

// 统计元素
const statNew = document.getElementById('stat-new');
const statDue = document.getElementById('stat-due');
const statDone = document.getElementById('stat-done');

/**
 * API 请求封装
 */
async function api(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
    };

    if (API_KEY) {
        headers['Authorization'] = `Bearer ${API_KEY}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: { ...headers, ...options.headers }
    });

    if (!response.ok) {
        if (response.status === 401) {
            promptForApiKey();
            throw new Error('需要 API Key');
        }
        throw new Error(`API 错误: ${response.status}`);
    }

    return response.json();
}

/**
 * 请求 API Key
 */
function promptForApiKey() {
    const key = prompt('请输入 TheBrain API Key:');
    if (key) {
        localStorage.setItem('thebrain_api_key', key);
        location.reload();
    }
}

/**
 * 检查 API Key
 */
function checkApiKey() {
    if (!API_KEY) {
        promptForApiKey();
        return false;
    }
    return true;
}

/**
 * 加载待复习卡片
 */
async function loadDueCards() {
    try {
        const data = await api('/api/srs/cards/due?limit=50');
        cards = data.cards || [];
        currentIndex = 0;
        reviewedCount = 0;

        updateStats();

        if (cards.length > 0) {
            await showCard(cards[0]);
        } else {
            showCompletion();
        }
    } catch (error) {
        console.error('加载卡片失败:', error);
        cardTitle.textContent = '加载失败，请刷新重试';
    }
}

/**
 * 获取卡片详情（含笔记和大纲）
 */
async function getCardDetail(thoughtId) {
    try {
        // 并行获取卡片详情和图谱
        const [cardData, graphData] = await Promise.all([
            api(`/api/srs/cards/${thoughtId}`),
            api(`/api/thoughts/${thoughtId}/graph?siblings=true`)
        ]);

        return {
            ...cardData,
            graph: graphData
        };
    } catch (error) {
        console.error('获取卡片详情失败:', error);
        return null;
    }
}

/**
 * 显示卡片
 */
async function showCard(card) {
    currentCard = card;

    // 重置卡片状态
    flashcard.classList.remove('flipped');
    ratingButtons.removeAttribute('disabled');
    completionMessage.style.display = 'none';
    flashcard.style.display = 'block';

    // 显示正面
    cardTitle.textContent = card.name;
    cardTitleBack.textContent = card.name;

    // 显示预估间隔
    if (card.next_intervals) {
        document.getElementById('interval-0').textContent = card.next_intervals[0] || '1d';
        document.getElementById('interval-1').textContent = card.next_intervals[1] || '2d';
        document.getElementById('interval-2').textContent = card.next_intervals[2] || '5d';
        document.getElementById('interval-3').textContent = card.next_intervals[3] || '10d';
    }

    // 加载详情
    const detail = await getCardDetail(card.thought_id);
    if (detail) {
        // 显示笔记
        cardNote.textContent = detail.note || '';

        // 显示标签
        renderTags(detail.graph?.tags || []);

        // 显示大纲
        renderOutline(detail.graph, card.name);

        // 显示元信息
        if (detail.graph?.activeThought?.label) {
            cardLabel.textContent = `📋 ${detail.graph.activeThought.label}`;
        } else {
            cardLabel.textContent = '';
        }
        cardInterval.textContent = `⏰ 间隔: ${card.interval_days}天`;
    }
}

/**
 * 渲染标签
 */
function renderTags(tags) {
    cardTags.innerHTML = '';
    tags.forEach(tag => {
        const tagEl = document.createElement('span');
        tagEl.className = 'tag';
        tagEl.textContent = tag.name;
        cardTags.appendChild(tagEl);
    });
}

/**
 * 渲染大纲视图
 */
function renderOutline(graph, currentName) {
    if (!graph) return;

    // 父节点
    outlineParents.innerHTML = '';
    (graph.parents || []).slice(0, 3).forEach(parent => {
        const node = document.createElement('div');
        node.className = 'outline-node parent-node';
        node.textContent = parent.name;
        node.title = parent.name;
        outlineParents.appendChild(node);
    });

    // 当前节点
    currentNode.textContent = currentName;
    currentNode.title = currentName;
    currentNode.className = 'outline-node current-node';

    // 兄弟节点
    const siblings = graph.siblings || [];
    if (siblings.length > 0) {
        siblingLeft.textContent = siblings[0]?.name || '';
        siblingLeft.title = siblings[0]?.name || '';
        siblingLeft.className = siblings[0] ? 'outline-node sibling-node' : '';
    } else {
        siblingLeft.textContent = '';
        siblingLeft.className = '';
    }

    if (siblings.length > 1) {
        siblingRight.textContent = siblings[1]?.name || '';
        siblingRight.title = siblings[1]?.name || '';
        siblingRight.className = siblings[1] ? 'outline-node sibling-node' : '';
    } else {
        siblingRight.textContent = '';
        siblingRight.className = '';
    }

    // 子节点
    outlineChildren.innerHTML = '';
    (graph.children || []).slice(0, 5).forEach(child => {
        const node = document.createElement('div');
        node.className = 'outline-node child-node';
        node.textContent = child.name;
        node.title = child.name;
        outlineChildren.appendChild(node);
    });
}

/**
 * 翻转卡片
 */
function flipCard() {
    flashcard.classList.toggle('flipped');
}

/**
 * 提交复习结果
 */
async function submitReview(quality) {
    if (!currentCard) return;

    try {
        ratingButtons.setAttribute('disabled', 'true');

        await api(`/api/srs/cards/${currentCard.thought_id}/review`, {
            method: 'POST',
            body: JSON.stringify({ quality })
        });

        reviewedCount++;
        currentIndex++;

        updateStats();

        // 显示下一张卡片
        if (currentIndex < cards.length) {
            await showCard(cards[currentIndex]);
        } else {
            showCompletion();
        }
    } catch (error) {
        console.error('提交复习失败:', error);
        alert('提交失败，请重试');
        ratingButtons.removeAttribute('disabled');
    }
}

/**
 * 显示完成提示
 */
function showCompletion() {
    flashcard.style.display = 'none';
    ratingButtons.setAttribute('disabled', 'true');
    completionMessage.style.display = 'block';
}

/**
 * 更新统计
 */
function updateStats() {
    const newCards = cards.filter(c => c.state === 'new').length;
    const remaining = cards.length - currentIndex;

    statNew.textContent = newCards;
    statDue.textContent = remaining;
    statDone.textContent = reviewedCount;
}

// ========== 事件绑定 ==========

// 卡片翻转
flashcard.addEventListener('click', flipCard);

// 评分按钮
document.querySelectorAll('.rating-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const quality = parseInt(btn.dataset.quality);
        submitReview(quality);
    });
});

// 键盘快捷键
document.addEventListener('keydown', (e) => {
    switch (e.key) {
        case ' ':
        case 'Enter':
            e.preventDefault();
            flipCard();
            break;
        case '1':
            submitReview(0); // Again
            break;
        case '2':
            submitReview(1); // Hard
            break;
        case '3':
            submitReview(2); // Good
            break;
        case '4':
            submitReview(3); // Easy
            break;
    }
});

// 初始化
if (checkApiKey()) {
    loadDueCards();
}
