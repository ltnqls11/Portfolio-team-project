import React, { useState, useEffect } from 'react';
import { Play, Pause, Heart, Coffee, Gamepad2, Trophy, Star, Zap, Shield, Brain, Timer, Gift } from 'lucide-react';

const CodePetGame = () => {
  // 펫 상태
  const [pet, setPet] = useState({
    name: 'Debuggy',
    type: 'Code Sprite',
    level: 1,
    exp: 0,
    expToNext: 100,
    happiness: 85,
    health: 90,
    energy: 75,
    hunger: 60,
    evolution: 'Newbie Dev', // 진화 단계
    mood: '😊',
    age: 1, // 일 단위
    lastCared: Date.now(),
    personality: 'Curious', // Curious, Lazy, Energetic, Focused
    specialAbilities: ['Quick Debug', 'Code Review'],
    favorite_treats: ['☕ Coffee', '🍕 Pizza', '🧠 Knowledge'],
    stats: {
      intelligence: 25,
      creativity: 20,
      debugging: 30,
      focus: 18,
      social: 15
    },
    accessories: {
      hat: null,
      glasses: 'Reading Glasses',
      background: 'Dark Theme'
    }
  });

  // 작업 상태
  const [workData, setWorkData] = useState({
    isWorking: false,
    workTime: 0,
    breaks: 0,
    productivity: 100,
    posture: 'good'
  });

  // 운동/케어 활동
  const [activities, setActivities] = useState([
    {
      id: 'neck_stretch',
      name: '거북목 교정',
      icon: '🦒',
      duration: '5분',
      effect: { health: +15, happiness: +5, energy: +10 },
      completed: false,
      cooldown: 0,
      description: '목을 좌우로 천천히 돌려주세요'
    },
    {
      id: 'shoulder_roll',
      name: '어깨 스트레칭',
      icon: '💪',
      duration: '3분',
      effect: { health: +10, energy: +15, stats: { focus: +2 } },
      completed: false,
      cooldown: 0,
      description: '어깨를 크게 원을 그리며 돌려주세요'
    },
    {
      id: 'back_stretch',
      name: '허리 운동',
      icon: '🤸',
      duration: '7분',
      effect: { health: +20, happiness: +10, stats: { creativity: +3 } },
      completed: false,
      cooldown: 0,
      description: '허리를 좌우로 천천히 비틀어주세요'
    },
    {
      id: 'wrist_exercise',
      name: '손목 스트레칭',
      icon: '🖐️',
      duration: '2분',
      effect: { health: +8, stats: { debugging: +2 } },
      completed: false,
      cooldown: 0,
      description: '손목을 부드럽게 원을 그리며 돌려주세요'
    },
    {
      id: 'eye_rest',
      name: '눈 휴식',
      icon: '👁️',
      duration: '1분',
      effect: { energy: +12, stats: { focus: +3 } },
      completed: false,
      cooldown: 0,
      description: '20-20-20 룰: 20초간 6미터 거리를 바라보세요'
    }
  ]);

  // 펫 먹이/아이템
  const [inventory, setInventory] = useState({
    coffee: 3,
    pizza: 2,
    book: 1,
    energy_drink: 2,
    meditation_app: 1,
    ergonomic_chair: 0,
    blue_light_glasses: 0
  });

  // 일일 로그인 보상
  const [lastLoginDate, setLastLoginDate] = useState(new Date().toDateString());
  const [dailyRewardClaimed, setDailyRewardClaimed] = useState(false);

  useEffect(() => {
    const today = new Date().toDateString();
    if (lastLoginDate !== today) {
      setLastLoginDate(today);
      setDailyRewardClaimed(false);
      // 일일 로그인 보상
      setInventory(prev => ({
        ...prev,
        coffee: prev.coffee + 2,
        meditation_app: prev.meditation_app + 1
      }));
      addNotification('🎁 일일 로그인 보상! 커피 2개, 명상앱 1개 획득!', 'success');
    }
  }, []);

  // 레벨업 보상
  useEffect(() => {
    if (pet.level > 1) {
      const levelRewards = {
        2: { book: 1 },
        5: { pizza: 2, coffee: 3 },
        10: { meditation_app: 2, energy_drink: 3 },
        15: { book: 2, pizza: 3 },
        20: { coffee: 5, meditation_app: 3, book: 2 }
      };
      
      if (levelRewards[pet.level]) {
        Object.entries(levelRewards[pet.level]).forEach(([item, amount]) => {
          setInventory(prev => ({
            ...prev,
            [item]: prev[item] + amount
          }));
        });
      }
    }
  }, [pet.level]);
  
  // 성취 시스템
  const [achievements, setAchievements] = useState([
    { id: 'first_exercise', name: '첫 운동', description: '첫 번째 운동 완료', unlocked: false, reward: 'coffee' },
    { id: 'healthy_week', name: '건강한 일주일', description: '7일 연속 운동', unlocked: false, reward: 'book' },
    { id: 'work_life_balance', name: '워라밸 달인', description: '적절한 휴식과 운동 유지', unlocked: false, reward: 'meditation_app' },
    { id: 'pet_evolution', name: '펫 진화', description: '펫이 다음 단계로 진화', unlocked: false, reward: 'blue_light_glasses' }
  ]);

  // 타이머 효과
  useEffect(() => {
    let interval;
    if (workData.isWorking) {
      interval = setInterval(() => {
        setWorkData(prev => ({ ...prev, workTime: prev.workTime + 1 }));
        
        // 30분마다 펫 상태 변화
        if (workData.workTime > 0 && workData.workTime % 1800 === 0) {
          updatePetFromWork();
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [workData.isWorking, workData.workTime]);

  // 펫 자동 상태 변화 (시간에 따라)
  useEffect(() => {
    const petInterval = setInterval(() => {
      setPet(prev => {
        const newHunger = Math.max(0, prev.hunger - 2);
        const newEnergy = prev.energy > 20 ? prev.energy - 1 : prev.energy;
        let newMood = prev.mood;
        
        if (newHunger < 30) newMood = '😟';
        else if (newEnergy < 30) newMood = '😴';
        else if (prev.happiness > 80) newMood = '😄';
        else if (prev.happiness < 50) newMood = '😞';
        else newMood = '😊';

        return {
          ...prev,
          hunger: newHunger,
          energy: newEnergy,
          mood: newMood
        };
      });
    }, 60000); // 1분마다

    return () => clearInterval(petInterval);
  }, []);

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${mins}m`;
  };

  const addNotification = (message, type = 'info') => {
    const notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date().toLocaleTimeString()
    };
    setNotifications(prev => [notification, ...prev.slice(0, 4)]);
  };

  const updatePetFromWork = () => {
    setPet(prev => ({
      ...prev,
      energy: Math.max(0, prev.energy - 15),
      hunger: Math.max(0, prev.hunger - 10),
      happiness: prev.happiness > 70 ? prev.happiness - 8 : prev.happiness,
      mood: '😅'
    }));
    addNotification(`${pet.name}이 피곤해 보여요! 휴식이 필요합니다 💤`, 'warning');
  };

  const completeActivity = (activityId) => {
    const activity = activities.find(a => a.id === activityId);
    if (!activity || activity.completed || activity.cooldown > 0) return;

    // 활동 완료 처리
    setActivities(prev => prev.map(a => 
      a.id === activityId 
        ? { ...a, completed: true, cooldown: 3600 } // 1시간 쿨다운
        : a
    ));

    // 펫 상태 개선
    setPet(prev => {
      let newPet = { ...prev };
      
      // 기본 스탯 적용
      if (activity.effect.health) newPet.health = Math.min(100, prev.health + activity.effect.health);
      if (activity.effect.happiness) newPet.happiness = Math.min(100, prev.happiness + activity.effect.happiness);
      if (activity.effect.energy) newPet.energy = Math.min(100, prev.energy + activity.effect.energy);
      
      // 특수 스탯 적용
      if (activity.effect.stats) {
        Object.keys(activity.effect.stats).forEach(stat => {
          if (newPet.stats[stat]) {
            newPet.stats[stat] = Math.min(100, prev.stats[stat] + activity.effect.stats[stat]);
          }
        });
      }
      
      // 경험치 증가
      newPet.exp = prev.exp + 30;
      if (newPet.exp >= prev.expToNext) {
        newPet.level += 1;
        newPet.exp = 0;
        newPet.expToNext = prev.expToNext + 50;
        addNotification(`🎉 ${pet.name}이 레벨 ${newPet.level}이 되었어요!`, 'success');
      }
      
      newPet.mood = '😊';
      return newPet;
    });

    // 아이템 보상 시스템
    const itemRewards = {
      'neck_stretch': ['coffee'],
      'shoulder_roll': ['coffee', 'meditation_app'],
      'back_stretch': ['pizza', 'book'],
      'wrist_exercise': ['energy_drink'],
      'eye_rest': ['meditation_app', 'book']
    };

    const possibleRewards = itemRewards[activityId] || [];
    if (possibleRewards.length > 0 && Math.random() < 0.7) { // 70% 확률로 아이템 획득
      const randomReward = possibleRewards[Math.floor(Math.random() * possibleRewards.length)];
      setInventory(prev => ({
        ...prev,
        [randomReward]: prev[randomReward] + 1
      }));
      
      const itemNames = {
        coffee: '☕ 커피',
        pizza: '🍕 피자',
        book: '📚 개발서',
        energy_drink: '⚡ 에너지음료',
        meditation_app: '🧘 명상앱'
      };
      
      addNotification(`🎁 보너스! ${itemNames[randomReward]}를 획득했어요!`, 'success');
    }

    addNotification(`${activity.name} 완료! ${pet.name}이 건강해졌어요! +30 EXP`, 'success');
  };

  const feedPet = (item) => {
    if (inventory[item] <= 0) return;

    const feedEffects = {
      coffee: { energy: +25, happiness: +10, hunger: +15 },
      pizza: { happiness: +20, hunger: +30, health: -5 },
      book: { stats: { intelligence: +5 }, happiness: +15 },
      energy_drink: { energy: +35, health: -8, stats: { focus: +3 } },
      meditation_app: { happiness: +25, energy: +15, stats: { focus: +5 } }
    };

    const effect = feedEffects[item];
    if (!effect) return;

    setPet(prev => {
      let newPet = { ...prev };
      
      Object.keys(effect).forEach(key => {
        if (key === 'stats') {
          Object.keys(effect.stats).forEach(stat => {
            newPet.stats[stat] = Math.min(100, prev.stats[stat] + effect.stats[stat]);
          });
        } else {
          newPet[key] = Math.min(100, Math.max(0, prev[key] + effect[key]));
        }
      });
      
      newPet.mood = '😋';
      newPet.lastCared = Date.now();
      return newPet;
    });

    setInventory(prev => ({ ...prev, [item]: prev[item] - 1 }));
    
    const itemNames = {
      coffee: '☕ 커피',
      pizza: '🍕 피자',
      book: '📚 개발서',
      energy_drink: '⚡ 에너지음료',
      meditation_app: '🧘 명상앱'
    };
    
    addNotification(`${pet.name}에게 ${itemNames[item]}을 줬어요!`, 'success');
  };

  const toggleWork = () => {
    setWorkData(prev => ({ ...prev, isWorking: !prev.isWorking }));
    if (!workData.isWorking) {
      addNotification('코딩 시작! 건강도 챙기면서 하세요 🚀', 'info');
    } else {
      // 작업 완료 시 아이템 보상
      const workMinutes = Math.floor(workData.workTime / 60);
      if (workMinutes >= 30) { // 30분 이상 작업했을 때만 보상
        const workRewards = ['coffee', 'energy_drink'];
        if (workMinutes >= 120) workRewards.push('pizza'); // 2시간 이상이면 피자도
        
        const randomReward = workRewards[Math.floor(Math.random() * workRewards.length)];
        setInventory(prev => ({
          ...prev,
          [randomReward]: prev[randomReward] + 1
        }));
        
        const itemNames = {
          coffee: '☕ 커피',
          pizza: '🍕 피자',
          energy_drink: '⚡ 에너지음료'
        };
        
        addNotification(`💼 ${workMinutes}분 작업 완료! ${itemNames[randomReward]} 보상!`, 'success');
      }
      addNotification('작업 완료! 수고하셨어요 👏', 'info');
    }
  };

  // 쿨다운 감소
  useEffect(() => {
    const cooldownInterval = setInterval(() => {
      setActivities(prev => prev.map(a => ({
        ...a,
        cooldown: Math.max(0, a.cooldown - 1),
        completed: a.cooldown <= 1 ? false : a.completed
      })));
    }, 1000);

    return () => clearInterval(cooldownInterval);
  }, []);

  const getPetEvolutionStage = () => {
    if (pet.level >= 20) return { name: 'Tech Lead', emoji: '👑', color: 'text-purple-400' };
    if (pet.level >= 15) return { name: 'Senior Dev', emoji: '🧙‍♂️', color: 'text-blue-400' };
    if (pet.level >= 10) return { name: 'Mid-level Dev', emoji: '👨‍💻', color: 'text-green-400' };
    if (pet.level >= 5) return { name: 'Junior Dev', emoji: '🐣', color: 'text-yellow-400' };
    return { name: 'Intern', emoji: '🥚', color: 'text-gray-400' };
  };

  const evolutionStage = getPetEvolutionStage();

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 text-white p-4">
      <div className="max-w-6xl mx-auto">
        {/* 헤더 */}
        <div className="text-center mb-6">
          <h1 className="text-4xl font-bold mb-2">🐱 Code Pet - 개발자 펫 키우기</h1>
          <p className="text-purple-200">건강한 개발 습관으로 귀여운 코드 펫을 키워보세요!</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 펫 상태 */}
          <div className="lg:col-span-1">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-6 border border-white/20">
              <div className="text-center mb-6">
                <div className="text-8xl mb-3">{pet.mood}</div>
                <h2 className="text-2xl font-bold mb-1">{pet.name}</h2>
                <div className={`text-lg font-semibold ${evolutionStage.color} flex items-center justify-center`}>
                  <span className="mr-2">{evolutionStage.emoji}</span>
                  {evolutionStage.name}
                </div>
                <div className="text-sm text-purple-200">Level {pet.level} • {pet.age}일째</div>
              </div>

              {/* 경험치 바 */}
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-2">
                  <span>EXP</span>
                  <span>{pet.exp}/{pet.expToNext}</span>
                </div>
                <div className="w-full bg-white/20 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${(pet.exp / pet.expToNext) * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* 펫 상태 바들 */}
              <div className="space-y-3 mb-6">
                {[
                  { name: '행복도', value: pet.happiness, color: 'from-pink-500 to-rose-500', icon: '😊' },
                  { name: '건강', value: pet.health, color: 'from-green-500 to-emerald-500', icon: '❤️' },
                  { name: '에너지', value: pet.energy, color: 'from-yellow-500 to-orange-500', icon: '⚡' },
                  { name: '배고픔', value: pet.hunger, color: 'from-blue-500 to-cyan-500', icon: '🍽️' }
                ].map(stat => (
                  <div key={stat.name}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="flex items-center">
                        <span className="mr-1">{stat.icon}</span>
                        {stat.name}
                      </span>
                      <span>{stat.value}%</span>
                    </div>
                    <div className="w-full bg-white/20 rounded-full h-2">
                      <div 
                        className={`bg-gradient-to-r ${stat.color} h-2 rounded-full transition-all duration-500`}
                        style={{ width: `${stat.value}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>

              {/* 펫 능력치 */}
              <div>
                <h3 className="font-bold mb-3 flex items-center">
                  <Brain className="mr-2" size={20} />
                  능력치
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(pet.stats).map(([stat, value]) => (
                    <div key={stat} className="bg-white/10 rounded-lg p-2">
                      <div className="text-xs capitalize font-semibold mb-1">
                        {stat === 'intelligence' ? '지능' :
                         stat === 'creativity' ? '창의력' :
                         stat === 'debugging' ? '디버깅' :
                         stat === 'focus' ? '집중력' : '사교성'}
                      </div>
                      <div className="text-sm font-bold">{value}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 작업 타이머 */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-bold mb-4 flex items-center">
                <Timer className="mr-2" />
                작업 시간
              </h3>
              
              <div className="text-center mb-4">
                <div className="text-3xl font-mono mb-2">
                  {formatTime(workData.workTime)}
                </div>
                <div className="text-sm text-purple-200">
                  생산성: {workData.productivity}%
                </div>
              </div>

              <button
                onClick={toggleWork}
                className={`w-full py-3 px-4 rounded-xl font-bold flex items-center justify-center transition-all ${
                  workData.isWorking 
                    ? 'bg-red-600 hover:bg-red-700' 
                    : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                {workData.isWorking ? <Pause className="mr-2" size={20} /> : <Play className="mr-2" size={20} />}
                {workData.isWorking ? '작업 중지' : '작업 시작'}
              </button>
            </div>
          </div>

          {/* 활동 및 케어 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 건강 활동 */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold mb-6 flex items-center">
                <Heart className="mr-3 text-red-400" />
                건강 케어 활동
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {activities.map(activity => (
                  <div key={activity.id} className="bg-white/10 rounded-xl p-4 border border-white/10">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        <span className="text-3xl mr-3">{activity.icon}</span>
                        <div>
                          <h3 className="font-bold">{activity.name}</h3>
                          <div className="text-sm text-purple-200">{activity.duration}</div>
                        </div>
                      </div>
                    </div>
                    
                    <p className="text-sm text-purple-200 mb-3">{activity.description}</p>
                    
                    <div className="flex items-center justify-between">
                      <div className="text-xs">
                        보상: {Object.entries(activity.effect).map(([key, value]) => (
                          key !== 'stats' && `${key === 'health' ? '❤️' : key === 'happiness' ? '😊' : '⚡'}+${value}`
                        )).filter(Boolean).join(' ')}
                      </div>
                      
                      <button
                        onClick={() => completeActivity(activity.id)}
                        disabled={activity.completed || activity.cooldown > 0}
                        className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                          activity.completed || activity.cooldown > 0
                            ? 'bg-gray-600 cursor-not-allowed'
                            : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
                        }`}
                      >
                        {activity.completed ? '완료!' :
                         activity.cooldown > 0 ? `${Math.ceil(activity.cooldown / 60)}분 후` :
                         '시작'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 아이템 획득 방법 안내 */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold mb-6 flex items-center">
                <Gift className="mr-3 text-yellow-400" />
                아이템 & 먹이
              </h2>
              
              <div className="mb-4 p-4 bg-blue-900/30 rounded-xl border border-blue-400/30">
                <h3 className="font-bold mb-2">🎯 아이템 획득 방법</h3>
                <div className="text-sm space-y-1 text-blue-200">
                  <div>• 운동 완료 시 70% 확률로 랜덤 보상</div>
                  <div>• 30분 이상 작업 완료 시 보상</div>
                  <div>• 매일 로그인 시 커피 2개 + 명상앱 1개</div>
                  <div>• 레벨업 시 특별 보상 패키지</div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {Object.entries(inventory).map(([item, count]) => {
                  const itemData = {
                    coffee: { name: '☕ 커피', desc: '에너지 +25, 행복 +10', source: '운동, 작업, 로그인' },
                    pizza: { name: '🍕 피자', desc: '배고픔 +30, 행복 +20', source: '허리운동, 장시간 작업' },
                    book: { name: '📚 개발서', desc: '지능 +5, 행복 +15', source: '허리운동, 눈휴식' },
                    energy_drink: { name: '⚡ 에너지음료', desc: '에너지 +35, 집중 +3', source: '손목운동, 작업' },
                    meditation_app: { name: '🧘 명상앱', desc: '행복 +25, 집중 +5', source: '어깨운동, 눈휴식' }
                  };
                  
                  if (!itemData[item]) return null;
                  
                  return (
                    <div key={item} className="bg-white/10 rounded-xl p-4 text-center border border-white/10">
                      <div className="text-2xl mb-2">{itemData[item].name.split(' ')[0]}</div>
                      <h3 className="font-bold text-sm mb-1">{itemData[item].name.split(' ').slice(1).join(' ')}</h3>
                      <p className="text-xs text-purple-200 mb-2">{itemData[item].desc}</p>
                      <p className="text-xs text-yellow-200 mb-3">획득: {itemData[item].source}</p>
                      <div className="text-sm mb-2">보유: {count}개</div>
                      <button
                        onClick={() => feedPet(item)}
                        disabled={count <= 0}
                        className={`w-full py-2 px-3 rounded-lg text-sm font-bold transition-all ${
                          count <= 0
                            ? 'bg-gray-600 cursor-not-allowed'
                            : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
                        }`}
                      >
                        {count <= 0 ? '없음' : '주기'}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* 알림 */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
              <h2 className="text-xl font-bold mb-4">펫 일기</h2>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="text-purple-300 text-center py-4">
                    {pet.name}와 함께하는 여정을 시작해보세요! 🌟
                  </div>
                ) : (
                  notifications.map(notification => (
                    <div
                      key={notification.id}
                      className={`p-3 rounded-lg text-sm border border-white/10 ${
                        notification.type === 'success' ? 'bg-green-900/30 text-green-200' :
                        notification.type === 'warning' ? 'bg-orange-900/30 text-orange-200' :
                        'bg-blue-900/30 text-blue-200'
                      }`}
                    >
                      <div>{notification.message}</div>
                      <div className="text-xs opacity-75 mt-1">
                        {notification.timestamp}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodePetGame;