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

  // Prevent rendering if user data is not ready
  if (!user) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#0b0c0d',
        color: '#e6e7eb'
      }}>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  // Normalize user role for rendering
  const userRole = user.role ? String(user.role).toLowerCase() : 'receiver';

  const handleDonorChange = (e) => {
    const { name, value } = e.target;
    setDonorForm(prev => ({ ...prev, [name]: value }));
  };

  const handleDonorSubmit = (e) => {
    e.preventDefault();
    addNotification(`Продукт "${donorForm.productName}" выставлен на раздачу`);
    setDonorForm({ productName: '', quantity: '', expiryDate: '', description: '' });
  };

  const handleTakeProduct = (productName) => {
    addNotification(`Вы зарезервировали: ${productName}`);
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
        <div className="donations-grid">
          <div className="donation-card">
            <div className="donation-icon">🍞</div>
            <h4>Хлеб ржаной</h4>
            <p>10 шт</p>
            <p className="status">✓ Получено</p>
            <p className="date">2 дня назад</p>
          </div>
          <div className="donation-card">
            <div className="donation-icon">🥛</div>
            <h4>Молоко коровье</h4>
            <p>5 л</p>
            <p className="status">✓ Получено</p>
            <p className="date">1 неделю назад</p>
          </div>
          <div className="donation-card">
            <div className="donation-icon">🥗</div>
            <h4>Овощная смесь</h4>
            <p>3 кг</p>
            <p className="status">✓ Получено</p>
            <p className="date">2 недели назад</p>
          </div>
          <div className="donation-card">
            <div className="donation-icon">🍎</div>
            <h4>Яблоки</h4>
            <p>15 шт</p>
            <p className="status">✓ Получено</p>
            <p className="date">3 недели назад</p>
          </div>
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
        <div className="orders-grid">
          <div className="order-card">
            <div className="order-status">Ожидает получения</div>
            <h4>Доставка продуктов №1</h4>
            <p>📍 Улица Ленина, 45</p>
            <p>🕐 Сегодня 14:00 - 16:00</p>
            <button className="btn-accept">Принять</button>
          </div>
          <div className="order-card">
            <div className="order-status">Ожидает получения</div>
            <h4>Доставка продуктов №2</h4>
            <p>📍 Пр. Мира, 12</p>
            <p>🕐 Завтра 10:00 - 12:00</p>
            <button className="btn-accept">Принять</button>
          </div>
          <div className="order-card">
            <div className="order-status">Ожидает получения</div>
            <h4>Доставка продуктов №3</h4>
            <p>📍 Ул. Советская, 88</p>
            <p>🕐 Завтра 15:00 - 17:00</p>
            <button className="btn-accept">Принять</button>
          </div>
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

      <div className="available-products">
        <h3>Доступные продукты</h3>
        <div className="products-grid">
          <button className="product-card" onClick={() => handleTakeProduct('Пицца')}>
            <div className="product-icon">🍕</div>
            <h4>Пицца</h4>
            <p>2 шт</p>
            <p className="location">📍 2 км от вас</p>
            <span className="product-action">Зарезервировать</span>
          </button>
          <button className="product-card" onClick={() => handleTakeProduct('Овощная миска')}>
            <div className="product-icon">🥗</div>
            <h4>Овощная миска</h4>
            <p>3 шт</p>
            <p className="location">📍 5 км от вас</p>
            <span className="product-action">Зарезервировать</span>
          </button>
          <button className="product-card" onClick={() => handleTakeProduct('Хлеб')}>
            <div className="product-icon">🍞</div>
            <h4>Хлеб</h4>
            <p>5 шт</p>
            <p className="location">📍 1 км от вас</p>
            <span className="product-action">Зарезервировать</span>
          </button>
          <button className="product-card" onClick={() => handleTakeProduct('Молоко')}>
            <div className="product-icon">🥛</div>
            <h4>Молоко</h4>
            <p>10 л</p>
            <p className="location">📍 3 км от вас</p>
            <span className="product-action">Зарезервировать</span>
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="dashboard-container">
      {userRole === 'donor' && renderDonorDashboard()}
      {userRole === 'deliverer' && renderDelivererDashboard()}
      {userRole === 'receiver' && renderReceiverDashboard()}
      {!['donor', 'deliverer', 'receiver'].includes(userRole) && (
        <div style={{ padding: '20px' }}>
          <p>Dashboard not configured for this role.</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;