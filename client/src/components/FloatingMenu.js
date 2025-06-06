import React, { useState } from 'react';
import '../css/FloatingMenu.css';
import ArticleReminder from './ArticleReminder';
import GoalBreakdown from './GoalBreakdown';
import HabitsBuilding from './HabitsBuilding';

export default function FloatingMenu({ toastRef }) {
  const [open, setOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(null); // null、'article'、'goal'、'habit'

  // menuItems 要寫在 function 裡面，才能用 setCurrentPage
  const menuItems = [
    { 
      label: '記事提醒', 
      desc: '單次事件的紀錄，像是聚餐、開會等一次性事件',
      onClick: () => setCurrentPage('article') 
    },
    { 
      label: '目標規劃',
      desc: '用於需要規劃與拆解的長期目標',
      onClick: () => setCurrentPage('goal') 
    },
    { 
      label: '習慣養成',
      desc: '協助養成持續21天的新習慣', 
      onClick: () => setCurrentPage('habit') 
    },
  ];

  // 條件渲染
  return (
    <div className="floating-menu-container">
      {/* 主按鈕 */}
      <button className="fab-btn" onClick={() => { setOpen(true); setCurrentPage(null); }}>
        + 新增事務
      </button>

      {/* 主選單（只有 open=true 而且 currentPage=null 才顯示） */}
      {open && currentPage === null && (
        <div className="menu-popup">
          <div className="menu-header">
            <button className="menu-close-btn" onClick={() => setOpen(false)}>
              ×
            </button>
            <p className="menu-title">請選擇目標類型</p>
          </div>
          <div className="menu-options">
            {menuItems.map((item, idx) => (
              <div className="menu-option" key={item.label}>
                <div>
                  <div className="menu-label">{item.label}</div>
                  <div className="menu-desc">{item.desc}</div>
                </div>
                <button
                  className="menu-add-btn"
                  onClick={() => item.onClick()}
                >
                  +
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 記事提醒頁面 */}
      {open && currentPage === 'article' && (
        <ArticleReminder onClose={() => setCurrentPage(null)} toastRef={toastRef} />
      )}

      {/* 目標規劃頁面 */}
      {open && currentPage === 'goal' && (
        <GoalBreakdown onClose={() => setCurrentPage(null)} toastRef={toastRef} />
      )}

      {/* 習慣養成頁面 */}
      {open && currentPage === 'habit' && (
        <HabitsBuilding onClose={() => setCurrentPage(null)} toastRef={toastRef} />
      )}
    </div>
  );
}
