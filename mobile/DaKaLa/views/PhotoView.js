import {Dimensions, Image} from 'react-native';
import React from 'react';
export default function PhotoView({route, navigation}) {
  const {stuid} = route.params;
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
