'use client';
/**
 * Registro único del plugin de React de GSAP (useGSAP). Se centraliza acá
 * para no repetir gsap.registerPlugin en cada componente que anima algo.
 */
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';

gsap.registerPlugin(useGSAP);

export { gsap, useGSAP };
