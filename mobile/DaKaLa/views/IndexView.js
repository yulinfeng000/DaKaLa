import React from 'react';
import {getStringValue, setStringValue} from '../utils/storage';
import {View, Text, StyleSheet, TextInput, Button, Alert} from 'react-native';
import Axios from 'axios';
import {REGISTER_URL} from '../utils/api';

const styles = StyleSheet.create({
  center: {
    alignItems: 'center',
    marginTop: 150,
  },
});

export default function IndexView({navigation}) {
  const [stuid, onChangeStuId] = React.useState('');
  const [passwd, onChangePasswd] = React.useState('');

  React.useEffect(() => {
    getStringValue('stuid').then((result) => {
      if (result !== null && result !== undefined && result !== '') {
        navigation.replace('infoView', {stuid: result});
      }
    });
  });

  const _handleCommit = () => {
    Alert.alert('注意', '请确定输入准确无误', [
      {
        text: '确定',
        onPress: () => {
          //console.log(`${stuid},${passwd}`);
          setStringValue('stuid', stuid);
          setStringValue('password', passwd);
          Axios.post(REGISTER_URL, {
            stuid: stuid,
            password: passwd,
            cityStatus: '1',
            workingPlace: '5',
            healthStatus: '1',
            livingStatus: '1',
            homeStatus: '1',
          });
          onChangePasswd('');
          navigation.navigate('infoView', {stuid: stuid});
        },
      },
      {
        text: '我再改改',
        onPress: () => console.log('Cancel Pressed'),
        style: 'cancel',
      },
    ]);
  };

  return (
    <View style={styles.center}>
      <Text>学号</Text>
      <TextInput
        style={{height: 40, borderColor: 'gray', borderWidth: 1, width: 100}}
        onChangeText={onChangeStuId}
        value={stuid}
      />

      <Text>密码</Text>
      <TextInput
        style={{height: 40, borderColor: 'gray', borderWidth: 1, width: 100}}
        onChangeText={onChangePasswd}
        value={passwd}
      />
      <Button title="提交" onPress={_handleCommit} />
    </View>
  );
}
