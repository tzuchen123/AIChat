const { Conversation, Message } = require('../models');

const listMessages = async (req, res, next) => {
  try {
    const conversation = await Conversation.findOne({
      where: { id: req.params.conversationId, userId: req.user.id },
    });

    if (!conversation) {
      return res.status(404).json({ message: 'Conversation not found' });
    }

    const messages = await Message.findAll({
      where: { conversationId: conversation.id },
      order: [['createdAt', 'ASC']],
    });

    res.json({ messages });
  } catch (err) {
    next(err);
  }
};

const createMessage = async (req, res, next) => {
  try {
    const { content } = req.body;

    if (!content) {
      return res.status(400).json({ message: 'content is required' });
    }

    const conversation = await Conversation.findOne({
      where: { id: req.params.conversationId, userId: req.user.id },
    });

    if (!conversation) {
      return res.status(404).json({ message: 'Conversation not found' });
    }

    const message = await Message.create({
      conversationId: conversation.id,
      role: 'user',
      content,
    });

    res.status(201).json({ message });
  } catch (err) {
    next(err);
  }
};

module.exports = { listMessages, createMessage };
