import React, { useState, useRef, useEffect } from 'react';
import './AnimatedButton.css';

interface AnimatedButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  icon?: string;
  fullWidth?: boolean;
  className?: string;
}

const AnimatedButton: React.FC<AnimatedButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  icon,
  fullWidth = false,
  className = ''
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [ripples, setRipples] = useState<Array<{ id: number; x: number; y: number }>>([]);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const rippleId = useRef(0);

  const handleMouseDown = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || loading) return;
    
    setIsPressed(true);
    createRipple(e);
  };

  const handleMouseUp = () => {
    setIsPressed(false);
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    setIsPressed(false);
  };

  const createRipple = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (!buttonRef.current) return;

    const rect = buttonRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const id = rippleId.current++;

    setRipples(prev => [...prev, { id, x, y }]);

    // 리플 애니메이션 완료 후 제거
    setTimeout(() => {
      setRipples(prev => prev.filter(ripple => ripple.id !== id));
    }, 600);
  };

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || loading) return;
    
    if (onClick) {
      onClick();
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
          hoverBackground: 'linear-gradient(135deg, #2563eb, #1e40af)',
          shadow: '0 4px 12px rgba(59, 130, 246, 0.3)',
          hoverShadow: '0 8px 20px rgba(59, 130, 246, 0.4)'
        };
      case 'secondary':
        return {
          background: '#f8fafc',
          hoverBackground: '#e2e8f0',
          shadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
          hoverShadow: '0 4px 8px rgba(0, 0, 0, 0.15)'
        };
      case 'success':
        return {
          background: 'linear-gradient(135deg, #10b981, #059669)',
          hoverBackground: 'linear-gradient(135deg, #059669, #047857)',
          shadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
          hoverShadow: '0 8px 20px rgba(16, 185, 129, 0.4)'
        };
      case 'warning':
        return {
          background: 'linear-gradient(135deg, #f59e0b, #d97706)',
          hoverBackground: 'linear-gradient(135deg, #d97706, #b45309)',
          shadow: '0 4px 12px rgba(245, 158, 11, 0.3)',
          hoverShadow: '0 8px 20px rgba(245, 158, 11, 0.4)'
        };
      case 'danger':
        return {
          background: 'linear-gradient(135deg, #ef4444, #dc2626)',
          hoverBackground: 'linear-gradient(135deg, #dc2626, #b91c1c)',
          shadow: '0 4px 12px rgba(239, 68, 68, 0.3)',
          hoverShadow: '0 8px 20px rgba(239, 68, 68, 0.4)'
        };
      default:
        return {
          background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
          hoverBackground: 'linear-gradient(135deg, #2563eb, #1e40af)',
          shadow: '0 4px 12px rgba(59, 130, 246, 0.3)',
          hoverShadow: '0 8px 20px rgba(59, 130, 246, 0.4)'
        };
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return { padding: '8px 16px', fontSize: '0.875rem' };
      case 'large':
        return { padding: '16px 32px', fontSize: '1.125rem' };
      default:
        return { padding: '12px 24px', fontSize: '1rem' };
    }
  };

  const variantStyles = getVariantStyles();
  const sizeStyles = getSizeStyles();

  return (
    <button
      ref={buttonRef}
      className={`animated-button ${variant} ${size} ${fullWidth ? 'full-width' : ''} ${className}`}
      style={{
        background: isHovered ? variantStyles.hoverBackground : variantStyles.background,
        boxShadow: isHovered ? variantStyles.hoverShadow : variantStyles.shadow,
        padding: sizeStyles.padding,
        fontSize: sizeStyles.fontSize,
        transform: isPressed ? 'scale(0.95)' : isHovered ? 'translateY(-2px)' : 'translateY(0)',
        opacity: disabled ? 0.6 : 1,
        cursor: disabled || loading ? 'not-allowed' : 'pointer',
        width: fullWidth ? '100%' : 'auto'
      }}
      onClick={handleClick}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      disabled={disabled || loading}
    >
      {/* 리플 효과 */}
      {ripples.map(ripple => (
        <span
          key={ripple.id}
          className="ripple"
          style={{
            left: ripple.x,
            top: ripple.y
          }}
        />
      ))}

      {/* 로딩 스피너 */}
      {loading && (
        <span className="loading-spinner">
          <svg viewBox="0 0 24 24" className="spinner-svg">
            <circle
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="2"
              fill="none"
              strokeLinecap="round"
              className="spinner-circle"
            />
          </svg>
        </span>
      )}

      {/* 아이콘 */}
      {icon && !loading && (
        <span className="button-icon">{icon}</span>
      )}

      {/* 텍스트 */}
      <span className="button-text" style={{ opacity: loading ? 0.7 : 1 }}>
        {children}
      </span>
    </button>
  );
};

export default AnimatedButton;
