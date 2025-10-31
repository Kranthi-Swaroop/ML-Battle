import { useEffect, useState, useRef } from 'react';

/**
 * Custom hook for animated number counting
 * @param {number} end - The target number to count to
 * @param {number} duration - Animation duration in milliseconds (default: 2000)
 * @param {number} start - Starting number (default: 0)
 * @returns {number} - Current animated value
 */
export const useCountUp = (end, duration = 2000, start = 0) => {
  const [count, setCount] = useState(start);
  const countRef = useRef(start);
  const startTimeRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    // Reset if end value changes
    countRef.current = start;
    setCount(start);
    startTimeRef.current = null;

    const animate = (timestamp) => {
      if (!startTimeRef.current) {
        startTimeRef.current = timestamp;
      }

      const progress = timestamp - startTimeRef.current;
      const percentage = Math.min(progress / duration, 1);

      // Easing function for smooth animation (easeOutExpo)
      const easeOutExpo = percentage === 1 ? 1 : 1 - Math.pow(2, -10 * percentage);
      
      const currentCount = start + (end - start) * easeOutExpo;
      countRef.current = currentCount;
      setCount(Math.floor(currentCount));

      if (percentage < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        setCount(end); // Ensure we end at exact value
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [end, duration, start]);

  return count;
};

export default useCountUp;
