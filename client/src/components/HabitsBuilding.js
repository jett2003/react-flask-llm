import React, { useState,useRef } from 'react';
import '../css/ArticleReminder.css';
import { Toast } from 'primereact/toast';

export default function HabitsBuilding({ onClose, toastRef }) {
    const toast = useRef(null)
    const [name, setName] = useState('');
    const [frequency, setFrequency] = useState('medium');
    const [intensity, setIntensity] = useState('medium');

    const handleCreate = async () => {
        if (!name || !frequency || !intensity) {
            toastRef.current?.show({
            severity: 'warn',
            summary: '提醒',
            detail: "請填寫所有欄位",
            life: 3000
            });
            return;
        }

        const userId = "user123"; // 根據實際情況修改
        const url = `http://localhost:5000/api/users/${userId}/habit_building`;

        const payload = {
            name,
            frequency,
            intensity
        };

        try {
            const res = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                toastRef.current?.show({
                severity: 'success',
                summary: '完成',
                detail: "習慣建立成功！",
                life: 3000
                });
                onClose();
            } else {
                const err = await res.json();
                toast.current.show({
                severity: 'error',
                summary: '建立失敗',
                detail: (err.error || res.status),
                life: 3000
                });
            }
        } catch (e) {
                toastRef.current?.show({
                severity: 'error',
                summary: '錯誤',
                detail: '網路錯誤',
                life: 3000
                });
        }
    };

    return (
        <div className="reminder-modal">
            <Toast ref={toast}  />
            <div className="reminder-container">
                <button className="close-btn" onClick={onClose}>×</button>
                <div className="reminder-header">
                    <div className="reminder-title">習慣名稱：</div>
                    <input
                        className="reminder-input"
                        type="text"
                        value={name}
                        onChange={e => setName(e.target.value)}
                        placeholder="例如：每天喝水 2000ml"
                    />
                </div>

                <div className="reminder-row">
                    <div className="reminder-title">頻率：</div>
                    <select
                        className="reminder-input"
                        value={frequency}
                        onChange={e => setFrequency(e.target.value)}
                        style={{width:"75px"}}
                    >
                        <option value="low">低</option>
                        <option value="medium">中</option>
                        <option value="high">高</option>
                    </select>
                </div>

                <div className="reminder-row">
                    <div className="reminder-title">強度：</div>
                    <select
                        className="reminder-input"
                        value={intensity}
                        onChange={e => setIntensity(e.target.value)}
                        style={{width:"75px"}}
                    >
                        <option value="low">低</option>
                        <option value="medium">中</option>
                        <option value="high">高</option>
                    </select>
                </div>

                <div className="reminder-desc">
                    系統將依照你的設定幫你拆解成每日小任務，幫助你 21 天養成這個習慣。
                </div>

                <button className="reminder-create-btn" onClick={handleCreate}>建立習慣</button>
            </div>
        </div>
    );
}
