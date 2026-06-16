'use client';
import { useRef } from 'react';
import { useGSAP, gsap } from '@/lib/gsapSetup';

/** Animación de conteo (count-up) cuando cambia `value`, vía gsap.to sobre un objeto proxy. */
export default function StatNumber({ value }) {
  const spanRef = useRef(null);
  const proxy = useRef({ val: 0 });

  useGSAP(() => {
    gsap.to(proxy.current, {
      val: value,
      duration: 0.8,
      ease: 'power2.out',
      onUpdate: () => {
        if (spanRef.current) spanRef.current.textContent = Math.round(proxy.current.val);
      },
    });
  }, [value]);

  return <span ref={spanRef}>0</span>;
}
