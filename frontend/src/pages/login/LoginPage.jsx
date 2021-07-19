import { observer } from 'mobx-react-lite'
import { NavBar, List, InputItem, Button, WhiteSpace, Toast } from 'antd-mobile'
import { useHistory } from 'react-router-dom'
import { useState } from 'react'
import Axios from '../../lib/axios'
import cookies from '../../lib/cookies'
import dayjs from '../../lib/datetime/date'
import { current_stu, dakaInfo, student_conf } from '../../store'
import { runInAction } from 'mobx'
import { setItem } from '../../lib/storage'
import { confLoading } from '../../components/config/ConfigUpdate'
import { debounce } from 'lodash'

function LoginPage() {
  const history = useHistory()

  const [stuid, setStuId] = useState('')
  const [password, setPasswd] = useState('')
  const handleLoginBtnClick = () => {
    console.log('do it do it')
    Axios.post('/stu/login', { stuid, password })
      .then((resp) => {
        console.log(resp)
        cookies.set('token', resp.token, {
          maxAge: dayjs.duration({ days: 1 }).asSeconds(),
        })
        runInAction(() => {
          dakaInfo.set(resp.ck)
          current_stu.set({ stuid: resp.stuid, config: resp.config })
          student_conf.replace({ stuid: resp.stuid, config: resp.config })
          student_conf.updateTrigger(resp.trigger)
          confLoading.set(false)
        })
        setItem(
          'student',
          { stuid: resp.stuid, config: resp.config },
          dayjs.duration({ days: 1 }).asMilliseconds(),
        )

        history.push('/app/home')
      })
      .catch((err) => {
        if (err.msg) Toast.fail(err.msg)
        else if (err.message) Toast.fail(err.message)
        else Toast.fail('发生错误')
      })
  }

  return (
    <>
      <NavBar>登录</NavBar>
      <List renderHeader={() => '基本信息'}>
        <InputItem
          key="0"
          clear
          placeholder="请输入学号"
          value={stuid}
          onChange={(e) => setStuId(e)}
        >
          学号
        </InputItem>
        <InputItem
          type="password"
          key="1"
          clear
          placeholder="请输入密码"
          value={password}
          onChange={(e) => setPasswd(e)}
        >
          教务处密码
        </InputItem>
      </List>
      <WhiteSpace />
      <Button type="primary" onClick={debounce(handleLoginBtnClick, 500)}>
        登录
      </Button>
      <WhiteSpace />
      <Button onClick={() => history.push('/register')}>注册</Button>
    </>
  )
}

export default observer(LoginPage)
