import React, { useState } from 'react';

const SAMPLE_TICKET = {
  items: [
    { name: 'Leche Semidesnatada', price: 0.95, qty: 2 },
    { name: 'Pan de Molde', price: 1.25, qty: 1 },
    { name: 'Huevos L', price: 2.45, qty: 1 },
    { name: 'Yogur Natural', price: 1.80, qty: 4 },
  ],
  total: 7.40
};

const RECIPES = [
  { name: 'Arroz con Pollo', time: '45 min', desc: 'Clásico reconfortante', match: 3, total: 4 },
  { name: 'Tortilla Española', time: '30 min', desc: 'Con cebolla caramelizada', match: 2, total: 3 },
  { name: 'Pasta Carbonara', time: '20 min', desc: 'Cremosa y rápida', match: 2, total: 4 },
];

export default function PantryApp() {
  const [tab, setTab] = useState('home');
  const [showScanner, setShowScanner] = useState(false);
  const [scannedTicket, setScannedTicket] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState([
    { from: 'bot', text: '¡Hola! ¿Qué te apetece cocinar hoy?' }
  ]);
  
  const [inventory, setInventory] = useState([
    { id: 1, name: 'Leche', qty: 2, expiry: '2025-01-17', category: 'Lácteos' },
    { id: 2, name: 'Pollo', qty: 1, expiry: '2025-01-12', category: 'Carnes' },
    { id: 3, name: 'Arroz', qty: 1, expiry: null, category: 'Cereales' },
    { id: 4, name: 'Huevos', qty: 6, expiry: '2025-01-25', category: 'Frescos' },
    { id: 5, name: 'Pimientos', qty: 3, expiry: '2025-01-15', category: 'Verduras' },
  ]);

  const getExpiryStatus = (expiry) => {
    if (!expiry) return null;
    const today = new Date();
    const exp = new Date(expiry);
    const diff = Math.ceil((exp - today) / (1000 * 60 * 60 * 24));
    if (diff < 0) return 'expired';
    if (diff <= 3) return 'soon';
    return 'ok';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return null;
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
  };

  const handleScan = () => {
    setScanning(true);
    setTimeout(() => {
      setScanning(false);
      setScannedTicket(SAMPLE_TICKET);
    }, 1800);
  };

  const addToInventory = () => {
    const newItems = scannedTicket.items.map((item, i) => ({
      id: Date.now() + i,
      name: item.name,
      qty: item.qty,
      expiry: null,
      category: 'Sin categoría'
    }));
    setInventory([...newItems, ...inventory]);
    setScannedTicket(null);
    setShowScanner(false);
  };

  const updateExpiry = (id, date) => {
    setInventory(inventory.map(item => 
      item.id === id ? { ...item, expiry: date } : item
    ));
    setEditingItem(null);
  };

  const deleteItem = (id) => {
    setInventory(inventory.filter(item => item.id !== id));
  };

  const sendMessage = () => {
    if (!chatInput.trim()) return;
    setMessages([...messages, { from: 'user', text: chatInput }]);
    setChatInput('');
    setTimeout(() => {
      setMessages(m => [...m, { 
        from: 'bot', 
        text: 'Con lo que tienes te recomiendo Arroz con Pollo. Tienes pollo, arroz y pimientos. ¿Te cuento los pasos?' 
      }]);
    }, 800);
  };

  const totalSpent = 156.40;
  const categories = [
    { name: 'Lácteos', pct: 32, color: '#3b82f6' },
    { name: 'Carnes', pct: 28, color: '#10b981' },
    { name: 'Verduras', pct: 22, color: '#f59e0b' },
    { name: 'Otros', pct: 18, color: '#8b5cf6' },
  ];

  const soonExpiring = inventory.filter(i => getExpiryStatus(i.expiry) === 'soon' || getExpiryStatus(i.expiry) === 'expired');

  return (
    <div style={{
      maxWidth: 390,
      margin: '0 auto',
      minHeight: '100vh',
      background: '#fafafa',
      fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
      position: 'relative',
      color: '#1a1a1a'
    }}>
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        input:focus { outline: none; border-color: #3b82f6 !important; }
      `}</style>
      
      {/* Header */}
      <div style={{
        padding: '20px 20px 16px',
        background: '#fff',
        borderBottom: '1px solid #eee'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0, letterSpacing: -0.5 }}>Despensa</h1>
          </div>
          <button 
            onClick={() => setShowScanner(true)}
            style={{
              background: '#1a1a1a',
              color: '#fff',
              border: 'none',
              width: 44,
              height: 44,
              borderRadius: 12,
              fontSize: 22,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >+</button>
        </div>
      </div>

      {/* Content */}
      <div style={{ paddingBottom: 90 }}>
        
        {/* Home Tab */}
        {tab === 'home' && (
          <div style={{ padding: 16 }}>
            
            {/* Alerta de caducidad */}
            {soonExpiring.length > 0 && (
              <div style={{
                background: '#fef9e7',
                borderRadius: 14,
                padding: 16,
                marginBottom: 16
              }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: '#92400e', marginBottom: 6 }}>
                  {soonExpiring.length} producto{soonExpiring.length > 1 ? 's' : ''} por caducar
                </div>
                <div style={{ fontSize: 13, color: '#a16207' }}>
                  {soonExpiring.map(i => i.name).join(', ')}
                </div>
              </div>
            )}

            {/* Lista */}
            <div style={{ background: '#fff', borderRadius: 16, overflow: 'hidden' }}>
              {inventory.map((item, idx) => {
                const status = getExpiryStatus(item.expiry);
                return (
                  <div key={item.id} style={{
                    padding: '16px 18px',
                    display: 'flex',
                    alignItems: 'center',
                    borderBottom: idx < inventory.length - 1 ? '1px solid #f0f0f0' : 'none'
                  }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 16, fontWeight: 500 }}>{item.name}</div>
                      <div style={{ fontSize: 13, color: '#888', marginTop: 3, display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span>{item.qty} ud.</span>
                        {item.expiry ? (
                          <span style={{
                            color: status === 'expired' ? '#dc2626' : status === 'soon' ? '#d97706' : '#888'
                          }}>
                            · {status === 'expired' ? 'Caducado' : `Cad. ${formatDate(item.expiry)}`}
                          </span>
                        ) : (
                          <button 
                            onClick={() => setEditingItem(item.id)}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: '#3b82f6',
                              fontSize: 13,
                              cursor: 'pointer',
                              padding: 0
                            }}
                          >+ Añadir caducidad</button>
                        )}
                      </div>
                    </div>
                    <button 
                      onClick={() => deleteItem(item.id)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#ccc',
                        fontSize: 20,
                        cursor: 'pointer',
                        padding: '4px 8px'
                      }}
                    >×</button>
                  </div>
                );
              })}
              
              {inventory.length === 0 && (
                <div style={{ padding: 40, textAlign: 'center', color: '#888' }}>
                  <div style={{ fontSize: 32, marginBottom: 8 }}>📦</div>
                  <div style={{ fontSize: 14 }}>Tu despensa está vacía</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Recetas Tab */}
        {tab === 'recipes' && (
          <div style={{ padding: 16 }}>
            
            {/* Recetas */}
            <h2 style={{ fontSize: 18, fontWeight: 600, margin: '0 0 12px' }}>Sugerencias</h2>
            
            {RECIPES.map((recipe, i) => (
              <div key={i} style={{
                background: '#fff',
                borderRadius: 14,
                padding: 16,
                marginBottom: 10
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontSize: 16, fontWeight: 600 }}>{recipe.name}</div>
                    <div style={{ fontSize: 13, color: '#888', marginTop: 2 }}>{recipe.desc}</div>
                    <div style={{ fontSize: 13, color: '#888', marginTop: 6 }}>{recipe.time}</div>
                  </div>
                  <div style={{
                    background: recipe.match === recipe.total ? '#dcfce7' : '#f3f4f6',
                    color: recipe.match === recipe.total ? '#16a34a' : '#666',
                    fontSize: 13,
                    fontWeight: 500,
                    padding: '6px 10px',
                    borderRadius: 8
                  }}>
                    {recipe.match}/{recipe.total}
                  </div>
                </div>
              </div>
            ))}

            {/* Chat */}
            <h2 style={{ fontSize: 18, fontWeight: 600, margin: '24px 0 12px' }}>Asistente</h2>
            
            <div style={{
              background: '#fff',
              borderRadius: 14,
              overflow: 'hidden'
            }}>
              <div style={{ height: 220, overflowY: 'auto', padding: 14 }}>
                {messages.map((msg, i) => (
                  <div key={i} style={{
                    marginBottom: 12,
                    display: 'flex',
                    justifyContent: msg.from === 'user' ? 'flex-end' : 'flex-start'
                  }}>
                    <div style={{
                      background: msg.from === 'user' ? '#1a1a1a' : '#f3f4f6',
                      color: msg.from === 'user' ? '#fff' : '#1a1a1a',
                      padding: '10px 14px',
                      borderRadius: 16,
                      borderBottomRightRadius: msg.from === 'user' ? 4 : 16,
                      borderBottomLeftRadius: msg.from === 'bot' ? 4 : 16,
                      fontSize: 14,
                      maxWidth: '80%',
                      lineHeight: 1.4
                    }}>{msg.text}</div>
                  </div>
                ))}
              </div>
              
              <div style={{ 
                display: 'flex', 
                gap: 8, 
                padding: 12,
                borderTop: '1px solid #f0f0f0'
              }}>
                <input
                  value={chatInput}
                  onChange={e => setChatInput(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && sendMessage()}
                  placeholder="Escribe un mensaje..."
                  style={{
                    flex: 1,
                    border: '1px solid #e5e7eb',
                    borderRadius: 10,
                    padding: '10px 14px',
                    fontSize: 14,
                    background: '#fafafa'
                  }}
                />
                <button 
                  onClick={sendMessage}
                  style={{
                    background: '#1a1a1a',
                    color: '#fff',
                    border: 'none',
                    borderRadius: 10,
                    width: 44,
                    fontSize: 16,
                    cursor: 'pointer'
                  }}
                >→</button>
              </div>
            </div>
          </div>
        )}

        {/* Gastos Tab */}
        {tab === 'stats' && (
          <div style={{ padding: 16 }}>
            
            {/* Total */}
            <div style={{
              background: '#1a1a1a',
              borderRadius: 18,
              padding: 28,
              textAlign: 'center',
              marginBottom: 20
            }}>
              <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.6)', marginBottom: 6 }}>Este mes</div>
              <div style={{ fontSize: 38, fontWeight: 700, color: '#fff', letterSpacing: -1 }}>
                {totalSpent.toFixed(2).replace('.', ',')} €
              </div>
            </div>

            {/* Categorías */}
            <h2 style={{ fontSize: 18, fontWeight: 600, margin: '0 0 14px' }}>Por categoría</h2>
            
            <div style={{ background: '#fff', borderRadius: 14, padding: 16 }}>
              {/* Barra visual */}
              <div style={{ 
                display: 'flex', 
                height: 10, 
                borderRadius: 5, 
                overflow: 'hidden',
                marginBottom: 20
              }}>
                {categories.map((cat, i) => (
                  <div key={i} style={{ 
                    width: `${cat.pct}%`, 
                    background: cat.color 
                  }} />
                ))}
              </div>
              
              {/* Leyenda */}
              {categories.map((cat, i) => (
                <div key={i} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px 0',
                  borderBottom: i < categories.length - 1 ? '1px solid #f5f5f5' : 'none'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ 
                      width: 10, 
                      height: 10, 
                      borderRadius: 3, 
                      background: cat.color 
                    }} />
                    <span style={{ fontSize: 14, color: '#444' }}>{cat.name}</span>
                  </div>
                  <span style={{ fontSize: 14, fontWeight: 600 }}>{cat.pct}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Bottom Navigation */}
      <div style={{
        position: 'fixed',
        bottom: 0,
        left: '50%',
        transform: 'translateX(-50%)',
        width: '100%',
        maxWidth: 390,
        background: '#fff',
        borderTop: '1px solid #eee',
        display: 'flex',
        padding: '10px 0 28px'
      }}>
        {[
          { id: 'home', label: 'Despensa', icon: '🏠' },
          { id: 'recipes', label: 'Recetas', icon: '👨‍🍳' },
          { id: 'stats', label: 'Gastos', icon: '📊' },
        ].map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            style={{
              flex: 1,
              background: 'none',
              border: 'none',
              padding: '6px 0',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 4
            }}
          >
            <span style={{ fontSize: 22 }}>{t.icon}</span>
            <span style={{ 
              fontSize: 11, 
              fontWeight: tab === t.id ? 600 : 400,
              color: tab === t.id ? '#1a1a1a' : '#999'
            }}>{t.label}</span>
          </button>
        ))}
      </div>

      {/* Scanner Modal */}
      {showScanner && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: '#fff',
          zIndex: 100,
          maxWidth: 390,
          margin: '0 auto'
        }}>
          <div style={{
            padding: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: 12
          }}>
            <button 
              onClick={() => { setShowScanner(false); setScannedTicket(null); }}
              style={{ 
                background: '#f3f4f6', 
                border: 'none', 
                width: 40,
                height: 40,
                borderRadius: 10,
                fontSize: 18,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >←</button>
            <span style={{ fontSize: 18, fontWeight: 600 }}>Escanear ticket</span>
          </div>

          {!scannedTicket ? (
            <div style={{ padding: '0 20px 20px' }}>
              <div style={{
                aspectRatio: '3/4',
                background: '#f8f8f8',
                borderRadius: 16,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: 20,
                border: '2px dashed #ddd'
              }}>
                {scanning ? (
                  <div style={{ textAlign: 'center' }}>
                    <div style={{
                      width: 44, 
                      height: 44, 
                      border: '3px solid #eee',
                      borderTopColor: '#1a1a1a',
                      borderRadius: '50%',
                      animation: 'spin 0.8s linear infinite',
                      margin: '0 auto 14px'
                    }} />
                    <div style={{ fontSize: 14, color: '#666' }}>Analizando...</div>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', color: '#999' }}>
                    <div style={{ fontSize: 48, marginBottom: 12 }}>📄</div>
                    <div style={{ fontSize: 15 }}>Encuadra el ticket</div>
                  </div>
                )}
              </div>

              <button
                onClick={handleScan}
                disabled={scanning}
                style={{
                  width: '100%',
                  background: scanning ? '#ccc' : '#1a1a1a',
                  color: '#fff',
                  border: 'none',
                  padding: 16,
                  borderRadius: 14,
                  fontSize: 16,
                  fontWeight: 600,
                  cursor: scanning ? 'default' : 'pointer'
                }}
              >
                {scanning ? 'Procesando...' : 'Capturar'}
              </button>
            </div>
          ) : (
            <div style={{ padding: '0 20px 20px' }}>
              <div style={{
                background: '#e8f5e9',
                borderRadius: 12,
                padding: 14,
                marginBottom: 20,
                display: 'flex',
                alignItems: 'center',
                gap: 10
              }}>
                <span style={{ fontSize: 18 }}>✓</span>
                <span style={{ fontSize: 14, color: '#2e7d32', fontWeight: 500 }}>
                  {scannedTicket.items.length} productos detectados
                </span>
              </div>

              <div style={{ background: '#f8f8f8', borderRadius: 14, overflow: 'hidden', marginBottom: 20 }}>
                {scannedTicket.items.map((item, i) => (
                  <div key={i} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '14px 16px',
                    borderBottom: i < scannedTicket.items.length - 1 ? '1px solid #eee' : 'none'
                  }}>
                    <div>
                      <div style={{ fontSize: 15, fontWeight: 500 }}>{item.name}</div>
                      <div style={{ fontSize: 13, color: '#888', marginTop: 2 }}>×{item.qty}</div>
                    </div>
                    <div style={{ fontSize: 15, fontWeight: 600 }}>{(item.price * item.qty).toFixed(2)} €</div>
                  </div>
                ))}
              </div>

              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '0 4px',
                marginBottom: 24
              }}>
                <span style={{ fontSize: 16, fontWeight: 500 }}>Total</span>
                <span style={{ fontSize: 22, fontWeight: 700 }}>{scannedTicket.total.toFixed(2)} €</span>
              </div>

              <button
                onClick={addToInventory}
                style={{
                  width: '100%',
                  background: '#1a1a1a',
                  color: '#fff',
                  border: 'none',
                  padding: 16,
                  borderRadius: 14,
                  fontSize: 16,
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Añadir a despensa
              </button>
            </div>
          )}
        </div>
      )}

      {/* Edit Expiry Modal */}
      {editingItem && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.4)',
          zIndex: 100,
          display: 'flex',
          alignItems: 'flex-end',
          justifyContent: 'center'
        }}>
          <div style={{
            background: '#fff',
            width: '100%',
            maxWidth: 390,
            borderRadius: '20px 20px 0 0',
            padding: 24
          }}>
            <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 20 }}>Fecha de caducidad</div>
            <input
              type="date"
              onChange={(e) => updateExpiry(editingItem, e.target.value)}
              style={{
                width: '100%',
                padding: 14,
                fontSize: 16,
                border: '1px solid #ddd',
                borderRadius: 12,
                marginBottom: 16
              }}
            />
            <button
              onClick={() => setEditingItem(null)}
              style={{
                width: '100%',
                background: '#f3f4f6',
                color: '#666',
                border: 'none',
                padding: 14,
                borderRadius: 12,
                fontSize: 15,
                cursor: 'pointer'
              }}
            >Cancelar</button>
          </div>
        </div>
      )}
    </div>
  );
}
