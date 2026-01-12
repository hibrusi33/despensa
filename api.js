// API service para comunicarse con el backend
const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Inventario
  async getInventory() {
    const response = await fetch(`${API_BASE_URL}/api/inventory`);
    return response.json();
  },

  async addInventoryItem(item) {
    const response = await fetch(`${API_BASE_URL}/api/inventory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(item)
    });
    return response.json();
  },

  async updateInventoryItem(id, updates) {
    const response = await fetch(`${API_BASE_URL}/api/inventory/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    return response.json();
  },

  async deleteInventoryItem(id) {
    const response = await fetch(`${API_BASE_URL}/api/inventory/${id}`, {
      method: 'DELETE'
    });
    return response.json();
  },

  // Recetas
  async getRecipes() {
    const response = await fetch(`${API_BASE_URL}/api/recipes`);
    return response.json();
  },

  async getSuggestedRecipes() {
    const response = await fetch(`${API_BASE_URL}/api/recipes/suggested`);
    return response.json();
  },

  // Chat
  async sendChatMessage(message, conversationHistory = []) {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory
      })
    });
    return response.json();
  },

  async getChatHistory(limit = 20) {
    const response = await fetch(`${API_BASE_URL}/api/chat/history?limit=${limit}`);
    return response.json();
  }
};
