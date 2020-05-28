import AsyncStorage from '@react-native-community/async-storage';

export const setStringValue = async (key, value) => {
  await AsyncStorage.setItem(key, value);
};

export const getStringValue = async (key) => {
  return await AsyncStorage.getItem(key);
};

export const deleteStringValue = async (key) => {
  return AsyncStorage.removeItem(key);
};
