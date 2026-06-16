'use client';
import { useEffect, useRef, useState } from 'react';

/**
 * Dropdown multi-select de parcelas. Equivalente al filtro del panel
 * original (Alpine.js x-data), reescrito como componente controlado de
 * React. Sin librería de UI externa: el caso es simple (lista + checkboxes)
 * y no justifica una dependencia como headlessui/radix para este alcance.
 */
export default function ParcelaSelector({ parcelas, seleccionadas, onChange }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function onClickOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', onClickOutside);
    return () => document.removeEventListener('mousedown', onClickOutside);
  }, []);

  function toggle(nombre) {
    if (seleccionadas.includes(nombre)) {
      onChange(seleccionadas.filter((n) => n !== nombre));
    } else {
      onChange([...seleccionadas, nombre]);
    }
  }

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="px-4 py-2 bg-white border border-stone-300 hover:bg-stone-50 text-sm font-medium rounded-lg flex items-center gap-2 transition"
      >
        <span>📍 Parcelas:</span>
        <span className="text-emerald-700 font-semibold">
          {seleccionadas.length}/{parcelas.length}
        </span>
        <svg
          className={`w-4 h-4 transition ${open ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl border border-stone-200 shadow-lg z-20 overflow-hidden">
          <div className="p-3 border-b border-stone-100 flex items-center justify-between text-xs">
            <button
              onClick={() => onChange(parcelas.map((p) => p.nombre_parcela))}
              className="text-emerald-700 hover:text-emerald-900 font-medium"
            >
              Todas
            </button>
            <span className="text-stone-400">·</span>
            <button onClick={() => onChange([])} className="text-stone-500 hover:text-stone-900 font-medium">
              Limpiar
            </button>
          </div>
          <div className="max-h-72 overflow-y-auto p-2">
            {parcelas.map((p) => (
              <label
                key={p.nombre_parcela}
                className="flex items-center gap-3 px-3 py-2 hover:bg-stone-50 rounded cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={seleccionadas.includes(p.nombre_parcela)}
                  onChange={() => toggle(p.nombre_parcela)}
                  className="rounded text-emerald-600 focus:ring-emerald-500"
                />
                <div className="flex-1">
                  <div className="text-sm font-medium text-stone-900">{p.nombre_parcela}</div>
                  <div className="text-xs text-stone-500">{p.nombre_codigo_sensor}</div>
                </div>
              </label>
            ))}
            {parcelas.length === 0 && (
              <p className="text-xs text-stone-500 px-3 py-4 text-center">Sin parcelas configuradas</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
