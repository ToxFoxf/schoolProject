import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import './Dashboard.css';
import { Package, TrendingUp, Clock, AlertCircle } from 'lucide-react';

const Dashboard = () => {
  const { user, addNotification } = useAuth();
  const [donorForm, setDonorForm] = useState({
    productName: '',
    quantity: '',
    expiryDate: '',
    description: ''
  });

  const handleDonorChange = (e) => {
    const { name, value } = e.target;
    setDonorForm(prev => ({ ...prev, [name]: value }));
  };

  const handleDonorSubmit = (e) => {
    e.preventDefault();
    addNotification(`Продукт "${donorForm.productName}" выставлен на раздачу`);
    setDonorForm({ productName: '', quantity: '', expiryDate: '', description: '' });
  };

  const renderDonorDashboard = () => (
    <div className="dashboard-content">
      <div className="error-banner">
        <AlertCircle size={18} />
        <span>Внимание: проверьте срок годности продуктов!</span>
      </div>

      <h2>Панель донора</h2>
      <form className="donor-form" onSubmit={handleDonorSubmit}>
        <div className="form-group">
          <label>Название продукта</label>
          <input
            type="text"
            name="productName"
            value={donorForm.productName}
            onChange={handleDonorChange}
            placeholder="Хлеб, молоко, овощи..."
            required
          />
        </div>
        <div className="form-group">
          <label>Количество</label>
          <input
            type="text"
            name="quantity"
            value={donorForm.quantity}
            onChange={handleDonorChange}
            placeholder="10 шт, 2 кг..."
            required
          />
        </div>
        <div className="form-group">
          <label>Дата истечения</label>
          <input
            type="date"
            name="expiryDate"
            value={donorForm.expiryDate}
            onChange={handleDonorChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Описание</label>
          <textarea
            name="description"
            value={donorForm.description}
            onChange={handleDonorChange}
            placeholder="Дополнительная информация..."
            rows="4"
          />
        </div>
        <button type="submit" className="btn-submit">Выставить продукт</button>
      </form>

      <div className="donation-history">
        <h3>История отдач</h3>
        <div className="empty-state">
          <Package size={40} />
          <p>Пока нет отданных продуктов</p>
        </div>
      </div>
    </div>
  );

  const renderDelivererDashboard = () => (
    <div className="dashboard-content">
      <div className="error-banner">
        <AlertCircle size={18} />
        <span>Внимание: у вас есть новые заказы!</span>
      </div>

      <h2>Панель доставщика</h2>
      <div className="stats-grid">
        <div className="stat-card">
          <TrendingUp size={32} />
          <h3>Всего доставок</h3>
          <p>{user?.deliveries || 150}</p>
        </div>
        <div className="stat-card">
          <Package size={32} />
          <h3>Рейтинг</h3>
          <p>{user?.rating || 4.8}</p>
        </div>
        <div className="stat-card">
          <Clock size={32} />
          <h3>На пути</h3>
          <p>2 заказа</p>
        </div>
      </div>

      <div className="orders-section">
        <h3>Доступные заказы</h3>
        <div className="empty-state">
          <Package size={40} />
          <p>Нет доступных заказов</p>
        </div>
      </div>
    </div>
  );

  const renderReceiverDashboard = () => (
    <div className="dashboard-content">
      <div className="error-banner">
        <AlertCircle size={18} />
        <span>Внимание: найденные продукты ждут вас на карте!</span>
      </div>

      <h2>Панель получателя</h2>
      <div className="receiver-info">
        <p>Доступные продукты находятся на карте. Откройте раздел "Карта" чтобы найти ближайшие доступные продукты.</p>
      </div>
      <div className="empty-state">
        <Package size={40} />
        <p>Нет доступных продуктов</p>
      </div>
    </div>
  );

  return (
    <div className="dashboard-container">
      {user?.role === 'Donor' && renderDonorDashboard()}
      {user?.role === 'Deliverer' && renderDelivererDashboard()}
      {user?.role === 'Receiver' && renderReceiverDashboard()}
    </div>
  );
};

export default Dashboard;