import React from 'react';
import './PainScale.css';

const PainScale = () => {
  const painLevels = [
    { level: 0, emoji: "😊", color: "#00FF00", desc: "통증 없음" },
    { level: 1, emoji: "🙂", color: "#66FF66", desc: "매우 경미한 통증" },
    { level: 2, emoji: "😐", color: "#99FF99", desc: "경미한 통증" },
    { level: 3, emoji: "🤕", color: "#CCFF99", desc: "불편함" },
    { level: 4, emoji: "😟", color: "#FFFF99", desc: "약간 아픔" },
    { level: 5, emoji: "😣", color: "#FFCC99", desc: "보통 아픔" },
    { level: 6, emoji: "😖", color: "#FF9966", desc: "상당히 아픔" },
    { level: 7, emoji: "😫", color: "#FF6633", desc: "많이 아픔" },
    { level: 8, emoji: "😵", color: "#FF3300", desc: "심한 통증" },
    { level: 9, emoji: "😱", color: "#CC0000", desc: "매우 심한 통증" },
    { level: 10, emoji: "🥵", color: "#990000", desc: "견딜 수 없는 통증" }
  ];

  return (
    <div className="pain-scale-guide">
      <h4>📊 통증 척도 가이드</h4>
      <p className="pain-scale-subtitle">PAIN MEASUREMENT SCALE - EMOTICON</p>
      
      <div className="pain-scale-container">
        {painLevels.map(({ level, emoji, color, desc }) => (
          <div 
            key={level}
            className="pain-scale-item"
            style={{ backgroundColor: color }}
          >
            <div className="pain-scale-emoji">{emoji}</div>
            <div className="pain-scale-number">{level}</div>
            <div className="pain-scale-desc">{desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PainScale;