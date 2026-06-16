'use client';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

/**
 * Mapa de parcelas con react-leaflet. Este archivo solo se carga vía
 * next/dynamic con { ssr: false } desde la página del dashboard, porque
 * Leaflet necesita `window`/`document` y rompe en el render de servidor.
 *
 * A diferencia del panel original (que manejaba el mapa imperativamente
 * con L.map/L.marker dentro de Alpine.js), acá el mapa es declarativo:
 * los <Marker> se agregan/quitan solos según el array `parcelas` que les
 * pasamos como prop, sin código manual de "crear o actualizar marcador".
 */
const icono = L.divIcon({
  className: '',
  html: `<div style="background:#059669;width:18px;height:18px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,.3)"></div>`,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

export default function MapaParcelas({ parcelas }) {
  return (
    <MapContainer center={[-38.73, -62.28]} zoom={12} style={{ height: '100%', minHeight: 500, borderRadius: '1rem' }}>
      <TileLayer
        attribution="&copy; OpenStreetMap"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {parcelas.map((p) => (
        <Marker key={p.nombre_parcela} position={[p.lat, p.lon]} icon={icono}>
          <Popup>
            <div style={{ fontFamily: 'Inter, sans-serif', minWidth: 160 }}>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>{p.nombre_parcela}</div>
              <div style={{ fontSize: 12, color: '#666' }}>Sensor: {p.nombre_codigo_sensor}</div>
              <div style={{ marginTop: 6, paddingTop: 6, borderTop: '1px solid #eee', fontSize: 12 }}>
                💧 {p.ultima_lectura?.valor_humedad?.toFixed(1) ?? '—'}%
                &nbsp;&nbsp;🌡️ {p.ultima_lectura?.valor_temperatura?.toFixed(1) ?? '—'}°C
              </div>
              <div style={{ fontSize: 11, color: '#888', marginTop: 4 }}>
                Clima ambiente: {p.clima_actual?.temperature ?? '—'}°C
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
