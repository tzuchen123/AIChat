const jwt = require('jsonwebtoken');
const { User, Conversation, Message } = require('../models');
const openai = require('../config/openai');

const initSocket = (io) => {
  // JWT authentication for Socket.io connections
  io.use(async (socket, next) => {
    try {
      const token = socket.handshake.auth.token;
      if (!token) {
        return next(new Error('Authentication token required'));
      }

      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      const user = await User.findByPk(decoded.id);
      if (!user) {
        return next(new Error('User not found'));
      }

      socket.user = user;
      next();
    } catch (err) {
      next(new Error('Invalid or expired token'));
    }
  });

  io.on('connection', (socket) => {
    console.log(`User connected: ${socket.user.id}`);

    // Join a conversation room
    socket.on('join_conversation', async (conversationId) => {
      try {
        const conversation = await Conversation.findOne({
          where: { id: conversationId, userId: socket.user.id },
        });

        if (!conversation) {
          socket.emit('error', { message: 'Conversation not found' });
          return;
        }

        socket.join(`conversation:${conversationId}`);
        socket.emit('joined', { conversationId });
      } catch (err) {
        socket.emit('error', { message: 'Failed to join conversation' });
      }
    });

    // Leave a conversation room
    socket.on('leave_conversation', (conversationId) => {
      socket.leave(`conversation:${conversationId}`);
    });

    // Send a message and receive AI streaming response
    socket.on('send_message', async ({ conversationId, content }) => {
      try {
        if (!conversationId || !content) {
          socket.emit('error', { message: 'conversationId and content are required' });
          return;
        }

        const conversation = await Conversation.findOne({
          where: { id: conversationId, userId: socket.user.id },
        });

        if (!conversation) {
          socket.emit('error', { message: 'Conversation not found' });
          return;
        }

        // Save user message
        await Message.create({
          conversationId,
          role: 'user',
          content,
        });

        // Fetch conversation history for context
        const history = await Message.findAll({
          where: { conversationId },
          order: [['createdAt', 'ASC']],
          limit: 20,
        });

        const messages = history.map((m) => ({ role: m.role, content: m.content }));

        // Stream AI response
        const stream = await openai.chat.completions.create({
          model: 'gpt-4o-mini',
          messages,
          stream: true,
        });

        let fullContent = '';

        for await (const chunk of stream) {
          const delta = chunk.choices[0]?.delta?.content;
          if (delta) {
            fullContent += delta;
            io.to(`conversation:${conversationId}`).emit('ai_stream_chunk', {
              conversationId,
              chunk: delta,
            });
          }
        }

        // Save assistant message
        const assistantMessage = await Message.create({
          conversationId,
          role: 'assistant',
          content: fullContent,
        });

        io.to(`conversation:${conversationId}`).emit('ai_stream_end', {
          conversationId,
          message: assistantMessage,
        });
      } catch (err) {
        console.error('Socket send_message error:', err);
        socket.emit('error', { message: 'Failed to process message' });
      }
    });

    socket.on('disconnect', () => {
      console.log(`User disconnected: ${socket.user.id}`);
    });
  });
};

module.exports = { initSocket };
