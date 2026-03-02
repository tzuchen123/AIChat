const errorHandler = (err, req, res, next) => {
  console.error(err);

  if (err.name === 'SequelizeValidationError' || err.name === 'SequelizeUniqueConstraintError') {
    const messages = err.errors.map((e) => e.message);
    return res.status(400).json({ message: messages.join(', ') });
  }

  if (err.name === 'SequelizeDatabaseError') {
    return res.status(500).json({ message: 'Database error occurred' });
  }

  const status = err.status || err.statusCode || 500;
  const message = err.expose ? err.message : 'Internal server error';

  res.status(status).json({ message });
};

module.exports = { errorHandler };
