// API service para comunicarse con el backend
const API_BASE_URL = 'http://localhost:8000';

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
};

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (response.status === 401) {
    // Token expired or invalid
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    window.location.reload();
    throw new Error('Session expired. Please login again.');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || 'An error occurred');
  }

  return response.json();
};

export const api = {
  // Authentication
  async register(userData) {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    return handleResponse(response);
  },

  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return handleResponse(response);
  },

  async getMe() {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  // Inventario
  async getInventory() {
    const response = await fetch(`${API_BASE_URL}/api/inventory`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  async addInventoryItem(item) {
    const response = await fetch(`${API_BASE_URL}/api/inventory`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(item)
    });
    return handleResponse(response);
  },

  async updateInventoryItem(id, updates) {
    const response = await fetch(`${API_BASE_URL}/api/inventory/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates)
    });
    return handleResponse(response);
  },

  async deleteInventoryItem(id) {
    const response = await fetch(`${API_BASE_URL}/api/inventory/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  // Recetas
  async getRecipes() {
    const response = await fetch(`${API_BASE_URL}/api/recipes`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  async getSuggestedRecipes() {
    const response = await fetch(`${API_BASE_URL}/api/recipes/suggested`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  // Chat
  async sendChatMessage(message, conversationHistory = []) {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory
      })
    });
    return handleResponse(response);
  },

  async getChatHistory(limit = 20) {
    const response = await fetch(`${API_BASE_URL}/api/chat/history?limit=${limit}`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  // Tickets
  async uploadTicket(ticketData) {
    const response = await fetch(`${API_BASE_URL}/api/tickets`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(ticketData)
    });
    return handleResponse(response);
  },

  // Meal Plans (Premium)
  async generateMealPlan(planData) {
    const response = await fetch(`${API_BASE_URL}/api/meal-plans/generate`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(planData)
    });
    return handleResponse(response);
  },

  async getMealPlans() {
    const response = await fetch(`${API_BASE_URL}/api/meal-plans`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  async getMealPlan(planId) {
    const response = await fetch(`${API_BASE_URL}/api/meal-plans/${planId}`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  // Subscriptions
  async getSubscriptionStatus() {
    const response = await fetch(`${API_BASE_URL}/api/subscriptions/status`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  async upgradeSubscription(tier, paymentMethodId) {
    const response = await fetch(`${API_BASE_URL}/api/subscriptions/upgrade`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ tier, payment_method_id: paymentMethodId })
    });
    return handleResponse(response);
  },

  async cancelSubscription() {
    const response = await fetch(`${API_BASE_URL}/api/subscriptions/cancel`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  }
};
