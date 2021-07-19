import { observer } from 'mobx-react-lite'
import {
  NavBar,
  Icon,
  List,
  InputItem,
  Picker,
  Button,
  WhiteSpace,
  Toast,
} from 'antd-mobile'
import { useHistory } from 'react-router-dom'
import { observable, runInAction } from 'mobx'
import Axios from '../../lib/axios'
import {
  cityStatusValue,
  workingPlaceValue,
  healthStatusValue,
  livingStatusValue,
  homeStatusValue,
} from '../../lib/util/data'

const stu = observable.object({
  stuid: '',
  password: '',
  cityStatus: ['1'],
  workingPlace: ['1'],
  healthStatus: ['1'],
  livingStatus: ['1'],
  homeStatus: ['1'],
  toDict() {
    return Object.assign({}, this, {
      cityStatus: this.cityStatus[0],
      workingPlace: this.workingPlace[0],
      healthStatus: this.healthStatus[0],
      livingStatus: this.livingStatus[0],
      homeStatus: this.homeStatus[0],
    })
  },
})

function RegisterPage() {
  const history = useHistory()

  const handleRegisterBtnClick = () => {
    console.log(stu.toDict())
    Axios.post('/stu/register', stu.toDict())
      .then((resp) => {
        Toast.success(resp.msg)
        setTimeout(() => {
          history.push('/login')
        }, 2000)
      })
      .catch((err) => {
        if (err.msg) Toast.fail(err.msg)
      })
  }

  return (
    <>
      <NavBar
        icon={<Icon type="left" />}
        onLeftClick={() => history.push('/login')}
      >
        注册
      </NavBar>
      <List renderHeader={() => '基本信息'}>
        <InputItem
          key="0"
          clear
          placeholder="请输入学号"
          value={stu.stuid}
          onChange={(e) => runInAction(() => (stu.stuid = e))}
        >
          学号
        </InputItem>
        <InputItem
          key="1"
          clear
          placeholder="请输入密码"
          value={stu.password}
          onChange={(e) => runInAction(() => (stu.password = e))}
        >
          教务处密码
        </InputItem>
      </List>
      <List renderHeader={() => '打卡信息配置'}>
        <Picker
          title="现居住地城市情况"
          data={cityStatusValue}
          value={stu.cityStatus}
          cols={1}
          onOk={(e) => {
            //console.log(e);
            runInAction(() => (stu.cityStatus = e))
          }}
        >
          <List.Item arrow="horizontal">现居住地城市情况</List.Item>
        </Picker>
        <Picker
          title="今天工作状态"
          data={workingPlaceValue}
          value={stu.workingPlace}
          cols={1}
          onOk={(e) => runInAction(() => (stu.workingPlace = e))}
        >
          <List.Item arrow="horizontal">今天工作状态</List.Item>
        </Picker>
        <Picker
          title="个人健康状况"
          data={healthStatusValue}
          value={stu.healthStatus}
          cols={1}
          onOk={(e) => runInAction(() => (stu.healthStatus = e))}
        >
          <List.Item arrow="horizontal">个人健康状况</List.Item>
        </Picker>
        <Picker
          title="个人生活状态"
          data={livingStatusValue}
          value={stu.livingStatus}
          cols={1}
          onOk={(e) => runInAction(() => (stu.livingStatus = e))}
        >
          <List.Item arrow="horizontal">个人生活状态</List.Item>
        </Picker>
        <Picker
          title="家庭成员状况"
          data={homeStatusValue}
          value={stu.homeStatus}
          cols={1}
          onOk={(e) => runInAction(() => (stu.homeStatus = e))}
        >
          <List.Item arrow="horizontal">家庭成员状况</List.Item>
        </Picker>
      </List>
      <WhiteSpace />

      <Button type="primary" onClick={handleRegisterBtnClick}>
        注册
      </Button>
    </>
  )
}

export default observer(RegisterPage)
