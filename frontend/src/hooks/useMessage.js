import { App } from 'antd';

/**
 * 自定义 hook 用于获取 message 实例
 * 确保在 App 组件内部使用
 */
export const useMessage = () => {
  const { message } = App.useApp();
  return message;
};

export default useMessage;