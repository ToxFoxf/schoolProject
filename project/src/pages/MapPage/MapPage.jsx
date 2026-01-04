import React from 'react';
import './MapPage.css';
import { Map, Package } from 'lucide-react';

const MapPage = () => {
  return (
    <div className="map-container">
      <h2>Карта и история заказов</h2>
      <div className="map-placeholder">
        <Map size={64} color="#ff6b6b" />
        <p>В работе</p>
        <p className="subtitle">Доступные заказы в вашем районе</p>
      </div>

      <div className="orders-list">
        <h3>Последние заказы</h3>
        <div className="empty-state">
          <Package size={40} color="#ff6b6b" />
          <p>История пуста</p>
        </div>
      </div>
    </div>
  );
};

export default MapPage;