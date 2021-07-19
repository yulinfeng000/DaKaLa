import { observer } from 'mobx-react-lite'
import { Modal, Button, NavBar, WhiteSpace, Toast } from 'antd-mobile'
import { useHistory } from 'react-router-dom'
import cookies from '../../lib/cookies'
import { getItem, removeItem } from '../../lib/storage'
import Axios from '../../lib/axios'
import DakaInfo from '../../components/daka-info/DakaInfo'
import dayjs from '../../lib/datetime/date'
import { debounce } from 'lodash'
function HomePage() {
  const history = useHistory()

  const handleDakaBtnClick = () => {
    Axios.post(`/stu/${stu.stuid}/daka`)
      .then((resp) => {
        Toast.success(resp.msg)
      })
      .catch((err) => {
        Toast.fail(err.msg)
      })
  }

  const stu = getItem('student')
  return (
    <>
      <NavBar>主页</NavBar>
      <WhiteSpace />
      <DakaInfo stuid={stu.stuid} />
      <WhiteSpace />
      <Button onClick={debounce(handleDakaBtnClick, 500)}>立即打卡</Button>
      <WhiteSpace />
      <Button onClick={() => history.push('/app/photo')}>查看打卡图</Button>
      <WhiteSpace />
      <Button onClick={() => history.push('/app/conf')}>查看/修改配置</Button>
      <WhiteSpace />
      <Button
        onClick={() => {
          Modal.alert('退出确认', '确认退出？', [
            { text: '取消', style: 'default' },
            {
              text: '确认',
              onPress: () => {
                cookies.remove('token')
                removeItem('student')
                history.push('/login')
              },
            },
          ])
        }}
      >
        退出登录
      </Button>
      <WhiteSpace size="lg" />

      <Button
        type="warning"
        onClick={() => {
          Modal.alert('警告', '确定从服务器中删除信息吗？', [
            { text: '取消', style: 'default' },
            {
              text: '确认',
              onPress: () => {
                Axios.post(`/stu/${stu.stuid}/del`)
                  .then((resp) => {
                    Toast.success(resp.msg)
                    setTimeout(() => {
                      removeItem('student')
                      cookies.remove('token')
                      history.push('/login')
                    }, dayjs.duration({ seconds: 2 }).asMilliseconds())
                  })
                  .catch((err) => {
                    if (err.msg) Toast.fail(err.msg)
                    else if (err.message) Toast.fail(err.message)
                    else Toast.fail('发生错误')
                  })
              },
            },
          ])
        }}
      >
        删除我的信息
      </Button>
    </>
  )
}

export default observer(HomePage)
