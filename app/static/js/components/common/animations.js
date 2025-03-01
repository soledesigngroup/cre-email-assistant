import { keyframes, css } from 'styled-components';

// Keyframes
export const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

export const fadeInUp = keyframes`
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
`;

export const fadeInDown = keyframes`
  from { 
    opacity: 0;
    transform: translateY(-20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
`;

export const fadeInLeft = keyframes`
  from { 
    opacity: 0;
    transform: translateX(-20px);
  }
  to { 
    opacity: 1;
    transform: translateX(0);
  }
`;

export const fadeInRight = keyframes`
  from { 
    opacity: 0;
    transform: translateX(20px);
  }
  to { 
    opacity: 1;
    transform: translateX(0);
  }
`;

export const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

export const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

export const slideIn = keyframes`
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
`;

export const slideOut = keyframes`
  from { transform: translateX(0); }
  to { transform: translateX(-100%); }
`;

// Animation mixins
export const animateFadeIn = (duration = 0.3, delay = 0) => css`
  animation: ${fadeIn} ${duration}s ease-in-out ${delay}s;
`;

export const animateFadeInUp = (duration = 0.3, delay = 0) => css`
  animation: ${fadeInUp} ${duration}s ease-in-out ${delay}s;
`;

export const animateFadeInDown = (duration = 0.3, delay = 0) => css`
  animation: ${fadeInDown} ${duration}s ease-in-out ${delay}s;
`;

export const animateFadeInLeft = (duration = 0.3, delay = 0) => css`
  animation: ${fadeInLeft} ${duration}s ease-in-out ${delay}s;
`;

export const animateFadeInRight = (duration = 0.3, delay = 0) => css`
  animation: ${fadeInRight} ${duration}s ease-in-out ${delay}s;
`;

export const animateSpin = (duration = 1, infinite = true) => css`
  animation: ${spin} ${duration}s linear ${infinite ? 'infinite' : '1'};
`;

export const animatePulse = (duration = 1, infinite = true) => css`
  animation: ${pulse} ${duration}s ease-in-out ${infinite ? 'infinite' : '1'};
`;

// Transition mixins
export const transition = (properties = 'all', duration = 0.3, timingFunction = 'ease') => css`
  transition: ${properties} ${duration}s ${timingFunction};
`;

export const hoverLift = (amount = '2px', duration = 0.2) => css`
  ${transition('transform', duration)}
  
  &:hover {
    transform: translateY(-${amount});
  }
  
  &:active {
    transform: translateY(0);
  }
`;

export const hoverScale = (scale = 1.05, duration = 0.2) => css`
  ${transition('transform', duration)}
  
  &:hover {
    transform: scale(${scale});
  }
  
  &:active {
    transform: scale(1);
  }
`;

export const hoverShadow = (duration = 0.2) => css`
  ${transition('box-shadow, transform', duration)}
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  &:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
`;

// Staggered animation for lists
export const staggeredFadeIn = (childSelector, baseDelay = 0.05, duration = 0.3) => css`
  ${childSelector} {
    opacity: 0;
  }
  
  ${Array.from({ length: 20 }).map((_, i) => css`
    ${childSelector}:nth-child(${i + 1}) {
      animation: ${fadeIn} ${duration}s ease-in-out forwards;
      animation-delay: ${baseDelay * (i + 1)}s;
    }
  `)}
`;

// Page transition animations
export const pageTransitionIn = css`
  .page-enter {
    opacity: 0;
    transform: translateY(20px);
  }
  
  .page-enter-active {
    opacity: 1;
    transform: translateY(0);
    transition: opacity 300ms, transform 300ms;
  }
`;

export const pageTransitionOut = css`
  .page-exit {
    opacity: 1;
    transform: translateY(0);
  }
  
  .page-exit-active {
    opacity: 0;
    transform: translateY(-20px);
    transition: opacity 300ms, transform 300ms;
  }
`;

// Loading animations
export const loadingSpinner = css`
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  ${animateSpin()}
`;

export const loadingDots = css`
  &::after {
    content: '.';
    animation: dots 1.5s steps(5, end) infinite;
  }
  
  @keyframes dots {
    0%, 20% { content: '.'; }
    40% { content: '..'; }
    60% { content: '...'; }
    80%, 100% { content: ''; }
  }
`;

export default {
  fadeIn,
  fadeInUp,
  fadeInDown,
  fadeInLeft,
  fadeInRight,
  spin,
  pulse,
  slideIn,
  slideOut,
  animateFadeIn,
  animateFadeInUp,
  animateFadeInDown,
  animateFadeInLeft,
  animateFadeInRight,
  animateSpin,
  animatePulse,
  transition,
  hoverLift,
  hoverScale,
  hoverShadow,
  staggeredFadeIn,
  pageTransitionIn,
  pageTransitionOut,
  loadingSpinner,
  loadingDots
}; 