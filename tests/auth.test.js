const request = require('supertest');

// Mock modules before requiring app
jest.mock('../src/models', () => {
  const bcrypt = require('bcryptjs');
  const mockUser = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    password: '$2a$12$hashedpassword',
    validatePassword: jest.fn().mockResolvedValue(true),
  };

  return {
    sequelize: {
      authenticate: jest.fn().mockResolvedValue(),
      sync: jest.fn().mockResolvedValue(),
    },
    User: {
      create: jest.fn().mockResolvedValue(mockUser),
      findOne: jest.fn().mockResolvedValue(mockUser),
      findByPk: jest.fn().mockResolvedValue(mockUser),
    },
    Conversation: {
      findAll: jest.fn().mockResolvedValue([]),
      create: jest.fn(),
      findOne: jest.fn(),
    },
    Message: {
      findAll: jest.fn().mockResolvedValue([]),
      create: jest.fn(),
    },
  };
});

jest.mock('../src/config/openai', () => ({}));
jest.mock('../src/socket', () => ({ initSocket: jest.fn() }));

process.env.JWT_SECRET = 'test_secret';
process.env.JWT_EXPIRES_IN = '7d';

const { app } = require('../src/app');

describe('Auth API', () => {
  describe('POST /api/auth/register', () => {
    it('should register a new user', async () => {
      const res = await request(app).post('/api/auth/register').send({
        username: 'testuser',
        email: 'test@example.com',
        password: 'Password123!',
      });

      expect(res.status).toBe(201);
      expect(res.body).toHaveProperty('token');
      expect(res.body.user).toHaveProperty('email', 'test@example.com');
    });

    it('should return 400 if required fields missing', async () => {
      const res = await request(app).post('/api/auth/register').send({
        email: 'test@example.com',
      });

      expect(res.status).toBe(400);
    });
  });

  describe('POST /api/auth/login', () => {
    it('should login with valid credentials', async () => {
      const res = await request(app).post('/api/auth/login').send({
        email: 'test@example.com',
        password: 'Password123!',
      });

      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('token');
    });

    it('should return 400 if fields missing', async () => {
      const res = await request(app).post('/api/auth/login').send({});

      expect(res.status).toBe(400);
    });
  });
});
