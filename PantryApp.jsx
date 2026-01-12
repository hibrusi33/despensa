import React, { useState } from 'react';

// Componentes de Iconos SVG
const HomeIcon = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
    <polyline points="9 22 9 12 15 12 15 22"/>
  </svg>
);

const CameraIcon = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
    <circle cx="12" cy="13" r="4"/>
  </svg>
);

const MessageCircleIcon = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
);

const BarChartIcon = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="20" x2="12" y2="10"/>
    <line x1="18" y1="20" x2="18" y2="4"/>
    <line x1="6" y1="20" x2="6" y2="16"/>
  </svg>
);

const PackageIcon = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16.5 9.4l-9-5.19"/>
    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
    <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
    <line x1="12" y1="22.08" x2="12" y2="12"/>
  </svg>
);

const FileTextIcon = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
    <polyline points="10 9 9 9 8 9"/>
  </svg>
);

const CheckIcon = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const SendIcon = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13"/>
    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
  </svg>
);

const ArrowLeftIcon = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="19" y1="12" x2="5" y2="12"/>
    <polyline points="12 19 5 12 12 5"/>
  </svg>
);

const XIcon = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
);

const SAMPLE_TICKET = {
  items: [
    { name: 'Leche Semidesnatada', price: 0.95, qty: 2 },
    { name: 'Pan de Molde', price: 1.25, qty: 1 },
    { name: 'Huevos L', price: 2.45, qty: 1 },
    { name: 'Yogur Natural', price: 1.80, qty: 4 },
  ],
  total: 7.40
};

export default function PantryApp() {
  const [tab, setTab] = useState('home');
  const [scannedTicket, setScannedTicket] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState([
    { from: 'bot', text: '¡Hola! ¿En qué puedo ayudarte hoy?' }
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
    setTab('home'); // Volver a la pestaña de despensa
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
        text: 'Puedo ayudarte a gestionar tu despensa, sugerirte recetas con los ingredientes que tienes, o responder preguntas sobre alimentación. ¿Qué necesitas?'
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
        </div>
      </div>

      {/* Content */}
      <div style={{ paddingBottom: 90 }}>

        {/* Home Tab - Despensa */}
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
                        cursor: 'pointer',
                        padding: '4px 8px',
                        display: 'flex',
                        alignItems: 'center'
                      }}
                    >
                      <XIcon size={20} />
                    </button>
                  </div>
                );
              })}

              {inventory.length === 0 && (
                <div style={{ padding: 40, textAlign: 'center', color: '#888' }}>
                  <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'center' }}>
                    <PackageIcon size={48} color="#ccc" />
                  </div>
                  <div style={{ fontSize: 14 }}>Tu despensa está vacía</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Scanner Tab - Escáner */}
        {tab === 'scanner' && (
          <div style={{ padding: 16 }}>
            {!scannedTicket ? (
              <div>
                <h2 style={{ fontSize: 20, fontWeight: 600, margin: '0 0 16px' }}>Escanear ticket</h2>
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
                      <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'center' }}>
                        <FileTextIcon size={64} color="#ccc" />
                      </div>
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
              <div>
                <h2 style={{ fontSize: 20, fontWeight: 600, margin: '0 0 16px' }}>Productos detectados</h2>
                <div style={{
                  background: '#e8f5e9',
                  borderRadius: 12,
                  padding: 14,
                  marginBottom: 20,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10
                }}>
                  <CheckIcon size={20} color="#2e7d32" />
                  <span style={{ fontSize: 14, color: '#2e7d32', fontWeight: 500 }}>
                    {scannedTicket.items.length} productos detectados
                  </span>
                </div>

                <div style={{ background: '#fff', borderRadius: 14, overflow: 'hidden', marginBottom: 20 }}>
                  {scannedTicket.items.map((item, i) => (
                    <div key={i} style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '14px 16px',
                      borderBottom: i < scannedTicket.items.length - 1 ? '1px solid #f0f0f0' : 'none'
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

                <div style={{ display: 'flex', gap: 12 }}>
                  <button
                    onClick={() => setScannedTicket(null)}
                    style={{
                      flex: 1,
                      background: '#f3f4f6',
                      color: '#666',
                      border: 'none',
                      padding: 16,
                      borderRadius: 14,
                      fontSize: 16,
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={addToInventory}
                    style={{
                      flex: 2,
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
              </div>
            )}
          </div>
        )}

        {/* Chatbot Tab - Asistente */}
        {tab === 'chatbot' && (
          <div style={{ padding: 16 }}>
            <h2 style={{ fontSize: 20, fontWeight: 600, margin: '0 0 16px' }}>Asistente</h2>

            <div style={{
              background: '#fff',
              borderRadius: 14,
              overflow: 'hidden',
              height: 'calc(100vh - 240px)',
              display: 'flex',
              flexDirection: 'column'
            }}>
              <div style={{ flex: 1, overflowY: 'auto', padding: 14 }}>
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
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <SendIcon size={18} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Gastos Tab - Stats */}
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
          { id: 'home', label: 'Despensa', icon: HomeIcon },
          { id: 'scanner', label: 'Escáner', icon: CameraIcon },
          { id: 'chatbot', label: 'Asistente', icon: MessageCircleIcon },
          { id: 'stats', label: 'Gastos', icon: BarChartIcon },
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
            <t.icon size={22} color={tab === t.id ? '#1a1a1a' : '#999'} />
            <span style={{
              fontSize: 11,
              fontWeight: tab === t.id ? 600 : 400,
              color: tab === t.id ? '#1a1a1a' : '#999'
            }}>{t.label}</span>
          </button>
        ))}
      </div>

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
