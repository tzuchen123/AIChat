const { Conversation, Message } = require('../models');

const listConversations = async (req, res, next) => {
  try {
    const conversations = await Conversation.findAll({
      where: { userId: req.user.id },
      order: [['updatedAt', 'DESC']],
    });

    res.json({ conversations });
  } catch (err) {
    next(err);
  }
};

const createConversation = async (req, res, next) => {
  try {
    const { title } = req.body;

    const conversation = await Conversation.create({
      userId: req.user.id,
      title: title || 'New Conversation',
    });

    res.status(201).json({ conversation });
  } catch (err) {
    next(err);
  }
};

const getConversation = async (req, res, next) => {
  try {
    const conversation = await Conversation.findOne({
      where: { id: req.params.id, userId: req.user.id },
      include: [{ model: Message, order: [['createdAt', 'ASC']] }],
    });

    if (!conversation) {
      return res.status(404).json({ message: 'Conversation not found' });
    }

    res.json({ conversation });
  } catch (err) {
    next(err);
  }
};

const updateConversation = async (req, res, next) => {
  try {
    const { title } = req.body;

    if (!title) {
      return res.status(400).json({ message: 'title is required' });
    }

    const conversation = await Conversation.findOne({
      where: { id: req.params.id, userId: req.user.id },
    });

    if (!conversation) {
      return res.status(404).json({ message: 'Conversation not found' });
    }

    await conversation.update({ title });

    res.json({ conversation });
  } catch (err) {
    next(err);
  }
};

const deleteConversation = async (req, res, next) => {
  try {
    const conversation = await Conversation.findOne({
      where: { id: req.params.id, userId: req.user.id },
    });

    if (!conversation) {
      return res.status(404).json({ message: 'Conversation not found' });
    }

    await conversation.destroy();

    res.status(204).send();
  } catch (err) {
    next(err);
  }
};

module.exports = {
  listConversations,
  createConversation,
  getConversation,
  updateConversation,
  deleteConversation,
};
