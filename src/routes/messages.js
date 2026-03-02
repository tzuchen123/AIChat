const express = require('express');
const router = express.Router({ mergeParams: true });
const { listMessages, createMessage } = require('../controllers/messageController');
const { authenticate } = require('../middlewares/auth');

router.use(authenticate);

// GET  /api/conversations/:conversationId/messages
router.get('/', listMessages);

// POST /api/conversations/:conversationId/messages
router.post('/', createMessage);

module.exports = router;
