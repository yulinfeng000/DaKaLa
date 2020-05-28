import React from 'react';
import {View, Button, StyleSheet, Text, Alert} from 'react-native';
import {DELETE_URL, DAKA_URL} from '../utils/api';
import Axios from 'axios';
import {deleteStringValue} from '../utils/storage';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    justifyContent: 'center',
  },
  title: {
    fontSize: 19,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default function InfoView({route, navigation}) {
  const stuid = route.params.stuid;
  const _handleDaka = () => {
    Axios.post(`${DAKA_URL}/${stuid}`).then((resp) => {
      if (resp.status === 200) {
        alert('打卡命令发送成功，最新打卡图请稍等');
      }
    });
  };
  const _handleDelete = () => {
    Alert.alert('删除数据', '你确定要删除数据吗', [
      {
        text: '确定',
        onPress: () => {
          Axios.post(`${DELETE_URL}/${stuid}`);
          deleteStringValue('stuid', null);
          deleteStringValue('passwd', null);
          navigation.navigate('indexView');
        },
      },
      {
        text: '我再想想',
        onPress: () => console.log('Cancel Pressed'),
        style: 'cancel',
      },
    ]);
  };
  return (
    <View style={styles.container}>
      <Text style={styles.title}>学号: {stuid}</Text>
      <Button title="打卡" onPress={_handleDaka} />
      <Button
        title="查看打卡图"
        onPress={() => navigation.navigate('photoView', {stuid: stuid})}
      />
      <Button title="删除信息" onPress={_handleDelete} />
    </View>
  );
}
/*
export function PhotoScreen({route, navigation}) {
  const {stuid} = route.params;
  navigation.title = '成信大打卡';
  //alert(stuid);
  const {width, height} = Dimensions.get('window');
  return (
    <Image
      source={{
        uri: `http://129.28.124.34:8888/static/vc_images/${stuid}_img.png`,
      }}
      style={{width: width, height: height - 20, resizeMode: 'contain'}}
    />
  );
}

export default function InfoView({stuid}) {
  return (
    <NavigationContainer initialRouteName="InfoScreen">
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
        }}>
        <Stack.Screen
          name="InfoScreen"
          component={InfoScreen}
          initialParams={{stuid: stuid}}
        />
        <Stack.Screen
          name="PhotoScreen"
          component={PhotoScreen}
          options={{title: '成信大打卡'}}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
*/
