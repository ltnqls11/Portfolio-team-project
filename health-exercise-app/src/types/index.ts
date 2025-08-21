// 사용자 증상 타입
export type Symptom = 
  | 'turtle_neck' 
  | 'rounded_shoulders' 
  | 'disc_herniation' 
  | 'carpal_tunnel_syndrome';

// 통증 위치 타입
export type PainLocation = 
  | 'neck' 
  | 'shoulders' 
  | 'back' 
  | 'wrist' 
  | 'arms' 
  | 'legs';

// 통증 심각도 타입
export type PainSeverity = 1 | 2 | 3 | 4 | 5;

// 작업 환경 타입
export type WorkEnvironment = 
  | 'office_desk' 
  | 'standing_work' 
  | 'manual_labor' 
  | 'driving' 
  | 'home_office';

// 일상 습관 타입
export type DailyHabits = 
  | 'sedentary' 
  | 'moderate_activity' 
  | 'active' 
  | 'very_active';

// 모드 타입
export type Mode = 'prevention' | 'exercise' | 'rehabilitation';

// 탭 타입
export type TabType = 'home' | 'input' | 'recommendation' | 'videos' | 'notifications' | 'progress';

// 사용자 정보 인터페이스
export interface UserInfo {
  symptoms: Symptom[];
  painLocation: PainLocation[];
  painSeverity: PainSeverity;
  workEnvironment: WorkEnvironment;
  dailyHabits: DailyHabits;
  age: number;
  workplace: string;
  homeLocation: string;
  workingHours: {
    start: string;
    end: string;
  };
  mode: Mode;
}

// 운동 정보 인터페이스
export interface Exercise {
  id: string;
  name: string;
  description: string;
  duration: number; // 분 단위
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  targetAreas: string[];
  videoUrl?: string;
  instructions: string[];
}

// 운동 루틴 인터페이스
export interface ExerciseRoutine {
  id: string;
  name: string;
  exercises: Exercise[];
  totalDuration: number;
  frequency: string;
  description: string;
}

// YouTube 비디오 정보 인터페이스
export interface YouTubeVideo {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  duration: string;
  viewCount: string;
  rating: number;
  comments: Comment[];
}

// 댓글 정보 인터페이스
export interface Comment {
  id: string;
  author: string;
  text: string;
  rating: number;
  date: string;
}

// 알림 설정 인터페이스
export interface NotificationSettings {
  enabled: boolean;
  breakInterval: number; // 분 단위
  exerciseReminders: boolean;
  stretchReminders: boolean;
}

// 진행 상황 인터페이스
export interface ProgressData {
  completedExercises: number;
  totalExercises: number;
  streak: number; // 연속 운동 일수
  lastExerciseDate: string;
  weeklyGoal: number;
  weeklyCompleted: number;
}
