import { NotificationSettings } from '../types';

// 알림 설정 기본값
const defaultSettings: NotificationSettings = {
  enabled: true,
  breakInterval: 60, // 60분마다
  exerciseReminders: true,
  stretchReminders: true
};

// 알림 권한 요청
export const requestNotificationPermission = async (): Promise<boolean> => {
  if (!('Notification' in window)) {
    console.log('이 브라우저는 알림을 지원하지 않습니다.');
    return false;
  }

  if (Notification.permission === 'granted') {
    return true;
  }

  if (Notification.permission === 'denied') {
    console.log('알림 권한이 거부되었습니다.');
    return false;
  }

  const permission = await Notification.requestPermission();
  return permission === 'granted';
};

// 알림 설정 저장
export const saveNotificationSettings = (settings: NotificationSettings): void => {
  localStorage.setItem('notificationSettings', JSON.stringify(settings));
};

// 알림 설정 불러오기
export const loadNotificationSettings = (): NotificationSettings => {
  const saved = localStorage.getItem('notificationSettings');
  if (saved) {
    return { ...defaultSettings, ...JSON.parse(saved) };
  }
  return defaultSettings;
};

// 휴식 시간 알림 시작
export const startBreakNotifications = (interval: number): NodeJS.Timeout | null => {
  if (!('Notification' in window) || Notification.permission !== 'granted') {
    console.log('알림 권한이 없습니다.');
    return null;
  }

  const timer = setInterval(() => {
    new Notification('휴식 시간입니다!', {
      body: '잠시 일어나서 스트레칭을 해보세요. 목과 어깨를 돌려주세요.',
      icon: '/favicon.ico',
      tag: 'break-notification'
    });
  }, interval * 60 * 1000); // 분을 밀리초로 변환

  return timer;
};

// 운동 알림 시작
export const startExerciseReminders = (): NodeJS.Timeout | null => {
  if (!('Notification' in window) || Notification.permission !== 'granted') {
    console.log('알림 권한이 없습니다.');
    return null;
  }

  // 매일 오전 9시와 오후 6시에 운동 알림
  const timer = setInterval(() => {
    const now = new Date();
    const hour = now.getHours();
    
    if (hour === 9 || hour === 18) {
      new Notification('운동 시간입니다!', {
        body: '오늘의 운동 루틴을 시작해보세요. 건강한 하루를 만들어보세요!',
        icon: '/favicon.ico',
        tag: 'exercise-notification'
      });
    }
  }, 60 * 60 * 1000); // 1시간마다 체크

  return timer;
};

// 스트레칭 알림 시작
export const startStretchReminders = (): NodeJS.Timeout | null => {
  if (!('Notification' in window) || Notification.permission !== 'granted') {
    console.log('알림 권한이 없습니다.');
    return null;
  }

  // 2시간마다 스트레칭 알림
  const timer = setInterval(() => {
    new Notification('스트레칭 시간입니다!', {
      body: '오래 앉아있었다면 잠시 일어나서 간단한 스트레칭을 해보세요.',
      icon: '/favicon.ico',
      tag: 'stretch-notification'
    });
  }, 2 * 60 * 60 * 1000); // 2시간

  return timer;
};

// 알림 중지
export const stopNotifications = (timer: NodeJS.Timeout | null): void => {
  if (timer) {
    clearInterval(timer);
  }
};

// 즉시 알림 보내기
export const sendImmediateNotification = (
  title: string, 
  body: string, 
  options?: NotificationOptions
): void => {
  if (!('Notification' in window) || Notification.permission !== 'granted') {
    console.log('알림 권한이 없습니다.');
    return;
  }

  new Notification(title, {
    body,
    icon: '/favicon.ico',
    ...options
  });
};

// 알림 테스트
export const testNotification = (): void => {
  sendImmediateNotification(
    '알림 테스트',
    '알림이 정상적으로 작동합니다!',
    { tag: 'test-notification' }
  );
};

// 작업 시간 체크 및 알림
export const checkWorkHours = (
  startTime: string, 
  endTime: string, 
  breakInterval: number
): void => {
  const now = new Date();
  const currentHour = now.getHours();
  const currentMinute = now.getMinutes();
  
  const [startHour, startMinute] = startTime.split(':').map(Number);
  const [endHour, endMinute] = endTime.split(':').map(Number);
  
  const currentTime = currentHour * 60 + currentMinute;
  const workStart = startHour * 60 + startMinute;
  const workEnd = endHour * 60 + endMinute;
  
  // 작업 시간 내에 있는지 확인
  if (currentTime >= workStart && currentTime <= workEnd) {
    // 휴식 시간이 되었는지 확인
    const timeSinceStart = currentTime - workStart;
    if (timeSinceStart > 0 && timeSinceStart % breakInterval === 0) {
      sendImmediateNotification(
        '휴식 시간입니다!',
        '잠시 일어나서 스트레칭을 해보세요. 목과 어깨를 돌려주세요.'
      );
    }
  }
};
