const express = require('express');
const router = express.Router();
const {
  listConversations,
  createConversation,
  getConversation,
  updateConversation,
  deleteConversation,
} = require('../controllers/conversationController');
const { authenticate } = require('../middlewares/auth');

router.use(authenticate);

// GET  /api/conversations
router.get('/', listConversations);

// POST /api/conversations
router.post('/', createConversation);

// GET  /api/conversations/:id
router.get('/:id', getConversation);

// PUT  /api/conversations/:id
router.put('/:id', updateConversation);

// DELETE /api/conversations/:id
router.delete('/:id', deleteConversation);

module.exports = router;
