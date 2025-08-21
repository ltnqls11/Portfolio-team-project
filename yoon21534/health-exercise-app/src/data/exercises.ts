import { Exercise, ExerciseRoutine } from '../types';

// 개별 운동 데이터
export const exercises: Exercise[] = [
  // 거북목 운동
  {
    id: 'neck_stretch_1',
    name: '목 스트레칭',
    description: '거북목 증상을 완화하는 목 스트레칭 운동',
    duration: 5,
    difficulty: 'beginner',
    targetAreas: ['neck', 'shoulders'],
    instructions: [
      '의자에 앉아서 등을 곧게 펴세요',
      '천천히 목을 좌우로 돌려주세요',
      '각 방향으로 10초씩 유지하세요',
      '총 3세트 반복하세요'
    ]
  },
  {
    id: 'chin_tuck',
    name: '턱 당기기 운동',
    description: '거북목 교정을 위한 턱 당기기 운동',
    duration: 3,
    difficulty: 'beginner',
    targetAreas: ['neck'],
    instructions: [
      '바른 자세로 앉거나 서세요',
      '턱을 가슴 쪽으로 당겨주세요',
      '10초간 유지한 후 원래대로 돌아가세요',
      '10회 반복하세요'
    ]
  },
  
  // 둥근 어깨 운동
  {
    id: 'shoulder_rolls',
    name: '어깨 돌리기',
    description: '둥근 어깨를 교정하는 어깨 운동',
    duration: 5,
    difficulty: 'beginner',
    targetAreas: ['shoulders'],
    instructions: [
      '어깨를 앞으로 돌려주세요',
      '그 다음 뒤로 돌려주세요',
      '각 방향으로 10회씩 반복하세요',
      '천천히 부드럽게 움직이세요'
    ]
  },
  {
    id: 'wall_angel',
    name: '벽 천사 운동',
    description: '어깨 자세를 교정하는 벽 운동',
    duration: 8,
    difficulty: 'intermediate',
    targetAreas: ['shoulders', 'back'],
    instructions: [
      '벽에 등을 대고 서세요',
      '팔을 벽에 붙여 천천히 위로 올리세요',
      '최대한 올린 후 천천히 내리세요',
      '10회 반복하세요'
    ]
  },
  
  // 디스크 탈출증 운동
  {
    id: 'cat_cow',
    name: '고양이-소 자세',
    description: '허리 디스크 탈출증 완화 운동',
    duration: 5,
    difficulty: 'beginner',
    targetAreas: ['back'],
    instructions: [
      '무릎을 꿇고 손바닥을 바닥에 대세요',
      '숨을 들이마시며 등을 둥글게 만드세요',
      '숨을 내쉬며 등을 아래로 굽히세요',
      '10회 반복하세요'
    ]
  },
  {
    id: 'pelvic_tilt',
    name: '골반 기울기 운동',
    description: '허리 안정화를 위한 골반 운동',
    duration: 5,
    difficulty: 'beginner',
    targetAreas: ['back'],
    instructions: [
      '바닥에 누워 무릎을 구부리세요',
      '골반을 앞으로 기울여 허리를 바닥에 붙이세요',
      '5초간 유지한 후 원래대로 돌아가세요',
      '15회 반복하세요'
    ]
  },
  
  // 손목 터널 증후군 운동
  {
    id: 'wrist_stretch',
    name: '손목 스트레칭',
    description: '손목 터널 증후군 완화 운동',
    duration: 3,
    difficulty: 'beginner',
    targetAreas: ['wrist'],
    instructions: [
      '한 손으로 다른 손의 손가락을 잡고 구부려주세요',
      '10초간 유지한 후 반대 방향으로 구부려주세요',
      '각 방향으로 5회씩 반복하세요',
      '양손 모두 실시하세요'
    ]
  },
  {
    id: 'finger_walk',
    name: '손가락 걷기',
    description: '손목과 손가락 유연성 향상 운동',
    duration: 5,
    difficulty: 'beginner',
    targetAreas: ['wrist', 'arms'],
    instructions: [
      '손바닥을 테이블에 대고 손가락을 구부리세요',
      '손가락을 하나씩 펴면서 테이블 위를 걷듯이 움직이세요',
      '양손 모두 실시하세요',
      '각 손으로 10회씩 반복하세요'
    ]
  }
];

// 증상별 운동 루틴
export const exerciseRoutines: Record<string, ExerciseRoutine[]> = {
  turtle_neck: [
    {
      id: 'turtle_neck_basic',
      name: '거북목 기본 루틴',
      exercises: [
        exercises.find(e => e.id === 'neck_stretch_1')!,
        exercises.find(e => e.id === 'chin_tuck')!
      ],
      totalDuration: 8,
      frequency: '하루 2-3회',
      description: '거북목 증상을 완화하는 기본 운동 루틴입니다.'
    }
  ],
  rounded_shoulders: [
    {
      id: 'rounded_shoulders_basic',
      name: '둥근 어깨 교정 루틴',
      exercises: [
        exercises.find(e => e.id === 'shoulder_rolls')!,
        exercises.find(e => e.id === 'wall_angel')!
      ],
      totalDuration: 13,
      frequency: '하루 2회',
      description: '둥근 어깨 자세를 교정하는 운동 루틴입니다.'
    }
  ],
  disc_herniation: [
    {
      id: 'disc_herniation_basic',
      name: '허리 디스크 탈출증 완화 루틴',
      exercises: [
        exercises.find(e => e.id === 'cat_cow')!,
        exercises.find(e => e.id === 'pelvic_tilt')!
      ],
      totalDuration: 10,
      frequency: '하루 2회',
      description: '허리 디스크 탈출증 증상을 완화하는 운동 루틴입니다.'
    }
  ],
  carpal_tunnel_syndrome: [
    {
      id: 'carpal_tunnel_basic',
      name: '손목 터널 증후군 완화 루틴',
      exercises: [
        exercises.find(e => e.id === 'wrist_stretch')!,
        exercises.find(e => e.id === 'finger_walk')!
      ],
      totalDuration: 8,
      frequency: '하루 3-4회',
      description: '손목 터널 증후군 증상을 완화하는 운동 루틴입니다.'
    }
  ]
};

// 작업 환경별 추가 운동
export const workEnvironmentExercises: Record<string, Exercise[]> = {
  office_desk: [
    {
      id: 'desk_stretch',
      name: '책상 스트레칭',
      description: '오래 앉아있는 직장인을 위한 책상 운동',
      duration: 3,
      difficulty: 'beginner',
      targetAreas: ['neck', 'shoulders', 'back'],
      instructions: [
        '의자에서 일어나서 팔을 위로 뻗어주세요',
        '몸을 좌우로 기울여주세요',
        '허리를 돌려주세요',
        '각 동작을 10초씩 유지하세요'
      ]
    }
  ],
  standing_work: [
    {
      id: 'standing_balance',
      name: '서서 하는 균형 운동',
      description: '오래 서있는 직장인을 위한 운동',
      duration: 5,
      difficulty: 'beginner',
      targetAreas: ['legs', 'back'],
      instructions: [
        '한 발을 들어 무릎을 구부려주세요',
        '30초간 유지한 후 다른 발로 바꿔주세요',
        '양쪽 각각 3회씩 반복하세요'
      ]
    }
  ]
};
