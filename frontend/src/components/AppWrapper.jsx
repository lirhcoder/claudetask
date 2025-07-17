import React from 'react';
import { message } from 'antd';

// 创建一个上下文来传递 message 实例
export const MessageContext = React.createContext(null);

/**
 * 全局消息处理器
 * 在 App 组件外部使用时的后备方案
 */
export const globalMessage = {
  success: (content) => {
    console.warn('Using global message. Consider using useMessage hook inside App component.');
    return message.success(content);
  },
  error: (content) => {
    console.warn('Using global message. Consider using useMessage hook inside App component.');
    return message.error(content);
  },
  warning: (content) => {
    console.warn('Using global message. Consider using useMessage hook inside App component.');
    return message.warning(content);
  },
  info: (content) => {
    console.warn('Using global message. Consider using useMessage hook inside App component.');
    return message.info(content);
  }
};

export default function AppWrapper({ children }) {
  return (
    <MessageContext.Provider value={globalMessage}>
      {children}
    </MessageContext.Provider>
  );
}