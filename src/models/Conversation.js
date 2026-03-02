const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const Conversation = sequelize.define('Conversation', {
    id: {
      type: DataTypes.INTEGER.UNSIGNED,
      autoIncrement: true,
      primaryKey: true,
    },
    userId: {
      type: DataTypes.INTEGER.UNSIGNED,
      allowNull: false,
    },
    title: {
      type: DataTypes.STRING(255),
      allowNull: false,
      defaultValue: 'New Conversation',
    },
  }, {
    tableName: 'conversations',
    timestamps: true,
    indexes: [
      { fields: ['userId'] },
    ],
  });

  return Conversation;
};
