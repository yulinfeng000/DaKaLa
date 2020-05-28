import React from 'react';
import {StyleSheet, View} from 'react-native';
import {getStringValue} from './utils/storage';
import InfoView from './views/InfoView';
import IndexView from './views/IndexView';
import {NavigationContainer} from '@react-navigation/native';
import {createStackNavigator} from '@react-navigation/stack';
import PhotoView from './views/PhotoView';

const Stack = createStackNavigator();

export default function App() {
  return (
    <View style={styles.container}>
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="indexView"
          screenOptions={{
            headerShown: false,
          }}>
          <Stack.Screen name="indexView" component={IndexView} />
          <Stack.Screen name="infoView" component={InfoView} />
          <Stack.Screen
            name="photoView"
            component={PhotoView}
            options={{title: '成信大打卡'}}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </View>
  );
  /*
  return (
    <View style={styles.container}>
      <InfoView stuid={stuid} />
    </View>
  );

   */
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    borderRadius: 4,
    borderWidth: 0.5,
    borderColor: '#d6d7da',
    justifyContent: 'center',
  },
});
