import { NavBar, Icon, ActivityIndicator } from 'antd-mobile'
import { observer } from 'mobx-react-lite'
import { useState } from 'react'
import { useEffect } from 'react'
import { useHistory } from 'react-router-dom'

import Axios from '../../lib/axios'
import { getItem } from '../../lib/storage'
function PhotoPage() {
  const history = useHistory()
  const student = getItem('student')
  const [b64data, setB64Data] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Axios.get(`/stu/${student.stuid}/photo`, {
      responseType: 'arraybuffer',
    })
      .then((resp) => {
        setB64Data(Buffer.from(resp.data, 'base64').toString('base64'))
      })
      .finally(() => setLoading(false))
  }, [student.stuid])

  return (
    <>
      <NavBar
        icon={<Icon type="left" />}
        onLeftClick={() => history.push('/app/home')}
      >
        打卡图
      </NavBar>
      <ActivityIndicator toast animating={loading} text="加载用户图片中..." />
      <img src={`data:image/jpeg;base64,${b64data}`} alt="daka_image" />
    </>
  )
}

export default observer(PhotoPage)
