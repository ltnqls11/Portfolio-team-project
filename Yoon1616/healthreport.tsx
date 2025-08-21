import { useState, FC, useEffect } from 'react';

// Define the type for a single daily report entry
interface DailyReport {
  date: string;
  painScore: number | null;
  completed: boolean;
}

const HealthAndRoutineDashboard: FC = () => {
  // State for today's routine completion status
  const [isRoutineCompleted, setIsRoutineCompleted] = useState<boolean>(false);
  // State for today's pain score input
  const [currentPainScore, setCurrentPainScore] = useState<number | null>(null);
  // State for the historical weekly report data
  const [reportHistory, setReportHistory] = useState<DailyReport[]>([]);

  /**
   * Generates an array of dates for the current week (Monday to Sunday).
   * This is used to create the data structure for the weekly report.
   */
  const getWeekDates = () => {
    const today = new Date();
    // Start of the current week (Monday)
    const startOfWeek = new Date(today.setDate(today.getDate() - (today.getDay() === 0 ? 6 : today.getDay() - 1)));
    const weekDates = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(startOfWeek);
      date.setDate(startOfWeek.getDate() + i);
      weekDates.push(date.toISOString().slice(0, 10));
    }
    return weekDates;
  };

  /**
   * useEffect hook to load data from localStorage when the component mounts.
   * It initializes the report history with data from the current week.
   */
  useEffect(() => {
    // Load health report history
    const storedHistory = localStorage.getItem('healthReportHistory');
    const weekDates = getWeekDates();
    let history: DailyReport[] = [];
    if (storedHistory) {
      history = JSON.parse(storedHistory);
    }
    const weeklyHistory = weekDates.map(date => {
      const existingData = history.find(entry => entry.date === date);
      return existingData || { date, painScore: null, completed: false };
    });
    setReportHistory(weeklyHistory);

    // Set today's pain score and routine completion status from history
    const today = new Date().toISOString().slice(0, 10);
    const todayEntry = weeklyHistory.find(entry => entry.date === today);
    if (todayEntry) {
      setCurrentPainScore(todayEntry.painScore);
      setIsRoutineCompleted(todayEntry.completed);
    }
  }, []);

  /**
   * Handles the routine completion by updating the state.
   */
  const handleCompleteRoutine = () => {
    setIsRoutineCompleted(true);
    alert('오늘의 운동 루틴을 완료했습니다! 🎉');
  };

  /**
   * Saves the current day's pain score and routine completion status.
   * This function combines the saving logic for both pain score and completion status.
   */
  const saveDailyReport = () => {
    if (currentPainScore === null) {
      alert("통증 점수를 입력해주세요.");
      return;
    }

    const today = new Date().toISOString().slice(0, 10);
    const updatedHistory = reportHistory.map(entry => {
      if (entry.date === today) {
        return {
          ...entry,
          painScore: currentPainScore,
          completed: isRoutineCompleted,
        };
      }
      return entry;
    });

    localStorage.setItem('healthReportHistory', JSON.stringify(updatedHistory));
    setReportHistory(updatedHistory);
    alert('오늘의 통증 점수가 기록되었습니다.');
  };

  /**
   * Determines the color of the bar based on the pain score.
   */
  const getBarColor = (score: number | null) => {
    if (score === null) return 'bg-gray-300';
    if (score <= 3) return 'bg-green-500';
    if (score <= 7) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  
  /**
   * Maps a number to a day of the week in Korean.
   */
  const getDayName = (dayIndex: number): string => {
    const days = ['월', '화', '수', '목', '금', '토', '일'];
    return days[dayIndex];
  };

  return (
    <div className="p-6 bg-white rounded-xl shadow-lg mt-8">
      {/* Daily Routine Section */}
      <div className="p-6 bg-purple-50 rounded-lg shadow-inner flex items-center justify-between mb-8">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-purple-800">오늘의 루틴</h3>
          <p className="text-purple-600 mt-1">오늘 운동을 완료하고 기록하세요!</p>
        </div>
        {isRoutineCompleted ? (
          <span className="text-green-600 font-bold">완료 ✅</span>
        ) : (
          <button
            onClick={handleCompleteRoutine}
            className="bg-purple-600 text-white px-4 py-2 rounded-full font-semibold hover:bg-purple-700 transition-colors"
          >
            완료하기
          </button>
        )}
      </div>

      {/* Weekly Report Section */}
      <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">주간 통증 & 운동 리포트 📊</h3>
      
      {/* Pain Score Input Section */}
      <div className="flex flex-col md:flex-row items-center justify-center space-y-4 md:space-y-0 md:space-x-4 mb-8">
        <label htmlFor="painScore" className="text-gray-700 font-medium">오늘의 통증 점수 (0-10):</label>
        <input
          id="painScore"
          type="number"
          min="0"
          max="10"
          value={currentPainScore ?? ''}
          onChange={(e) => {
            const value = e.target.value;
            setCurrentPainScore(value === '' ? null : Math.min(10, Math.max(0, parseInt(value))));
          }}
          className="w-full md:w-20 p-2 border border-gray-300 rounded-lg text-center"
          placeholder="0-10"
        />
        <button
          onClick={saveDailyReport}
          className="w-full md:w-auto px-6 py-2 bg-indigo-600 text-white rounded-full font-semibold hover:bg-indigo-700 transition-colors"
        >
          기록하기
        </button>
      </div>

      {/* Bar Chart Visualization */}
      <div className="flex items-end justify-between h-48 py-2 px-1 bg-gray-50 rounded-lg border border-gray-200">
        {reportHistory.map((entry, index) => (
          <div key={index} className="flex flex-col items-center flex-1 h-full px-1">
            <div className="flex-grow flex items-end w-full">
              <div
                className={`w-4/5 mx-auto rounded-t-lg transition-all duration-300 ease-out transform`}
                style={{
                  height: `${entry.painScore !== null ? (entry.painScore / 10) * 100 : 0}%`,
                  backgroundColor: entry.painScore !== null ? getBarColor(entry.painScore) : 'transparent',
                }}
              ></div>
            </div>
            <span className="text-xs text-gray-600 mt-1 font-bold">
              {entry.painScore !== null ? entry.painScore : '-'}
            </span>
            <span className="text-xs text-gray-500 mt-1">
              {getDayName(index)}
            </span>
            <div className="mt-1">
              {entry.completed && (
                <span className="text-green-500 text-sm">✓</span>
              )}
            </div>
          </div>
        ))}
      </div>
      <p className="text-sm text-center text-gray-500 mt-4">
        통증 점수: 🟢 낮음 (0-3), 🟡 보통 (4-7), 🔴 심함 (8-10)
      </p>
    </div>
  );
};

export default HealthAndRoutineDashboard;
