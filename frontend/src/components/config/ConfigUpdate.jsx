import {
  InputItem,
  List,
  Picker,
  DatePicker,
  Button,
  WhiteSpace,
  ActivityIndicator,
  Toast,
  Switch,
} from "antd-mobile"
import dayjs from "../../lib/datetime/date"
import { observable, runInAction } from "mobx"
import { observer } from "mobx-react-lite"
import { useState } from "react"
import {
  cityStatusValue,
  homeStatusValue,
  workingPlaceValue,
  healthStatusValue,
  livingStatusValue,
  applicationStartDayValue,
  applicationEndDayValue,
  applicationStartTimeValue,
  applicationEndTimeValue,
} from "../../lib/util/data"
import Axios from "../../lib/axios"
import { useEffect } from "react"
import { current_stu, student_conf as student } from "../../store"
import { debounce } from "lodash"

export const confLoading = observable.box(true)

function ConfigUpdate({ stuid }) {
  const [password, setPasswd] = useState(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const stu = await Axios.get(`/stu/${stuid}/info`)
        const trigger = (await Axios.get(`/stu/${stuid}/dakatrigger/info`))
          .trigger
        student.replace(stu)
        student.updateTrigger(trigger)
      } catch (err) {
        Toast.fail(err.message)
      } finally {
        runInAction(() => confLoading.set(false))
      }
    }
    fetchData()
  }, [stuid])

  const handleTriggerChange = (e) => {
    student.updateTrigger(e)
    Axios.post(`/stu/${stuid}/dakatrigger/update`, { daka_trigger: e })
      .then((resp) => {
        student.updateTrigger(resp.trigger)
        if (resp.trigger) Toast.success("开启每日打卡")
        else Toast.success("关闭每日打卡")
      })
      .catch((err) => {
        student.updateTrigger(!e)
        if (err.msg) err.message = err.msg
        if (err.message) Toast.fail(err.message)
      })
  }

  const handlerUpdateBtnClick = debounce(() => {
    console.log("do update")
    const data = {
      stuid: student.stuid,
      cityStatus: student.cityStatus[0],
      workingPlace: student.workingPlace[0],
      healthStatus: student.healthStatus[0],
      livingStatus: student.livingStatus[0],
      homeStatus: student.homeStatus[0],
      application_reason: student.application_reason,
      application_location: student.application_location,
      application_start_day: student.application_start_day[0],
      application_start_time: student.application_start_time[0],
      application_end_day: student.application_end_day[0],
      application_end_time: student.application_end_time[0],
      scheduler_start_time: student.scheduler_start_time,
      scheduler_time_segment: student.scheduler_time_segment,
      password: password ? password : null,
    }
    Axios.post(`/stu/${stuid}/info/update`, data).then((resp) => {
      runInAction(() => {
        current_stu.set({ stuid, config: resp.config })
      })
      Toast.success("更新成功")
    })
  }, 500)

  const handleApplicationChange = (flag) => {
    if (!flag) {
      runInAction(() => (student.scheduler_time_segment = -1))
    } else {
      runInAction(() => (student.scheduler_time_segment = 1))
    }
  }

  return (
    <>
      <ActivityIndicator
        toast
        animating={confLoading.get()}
        text="加载用户配置中..."
      />
      <List renderHeader={() => <b>基本信息</b>}>
        <InputItem
          disabled
          key="1-0"
          clear
          placeholder="请输入学号"
          value={student.stuid}
        >
          学号
        </InputItem>
        <InputItem
          key="1-1"
          clear
          placeholder="密码(无需修改请不填)"
          value={password}
          onChange={(e) => setPasswd(e)}
        >
          密码
        </InputItem>
        <List.Item
          extra={
            <Switch
              checked={student.daka_trigger}
              onChange={handleTriggerChange}
            />
          }
        >
          每日打卡开关
        </List.Item>
      </List>
      <List renderHeader={() => <b>基本配置</b>}>
        <Picker
          title="现居住地城市情况"
          data={cityStatusValue}
          value={student.cityStatus}
          cols={1}
          onOk={(e) => {
            //console.log(e);
            runInAction(() => (student.cityStatus = e))
          }}
        >
          <List.Item arrow="horizontal">现居住地城市情况</List.Item>
        </Picker>
        <Picker
          title="今天工作状态"
          data={workingPlaceValue}
          value={student.workingPlace}
          cols={1}
          onOk={(e) => runInAction(() => (student.workingPlace = e))}
        >
          <List.Item arrow="horizontal">今天工作状态</List.Item>
        </Picker>
        <Picker
          title="个人健康状况"
          data={healthStatusValue}
          value={student.healthStatus}
          cols={1}
          onOk={(e) => runInAction(() => (student.healthStatus = e))}
        >
          <List.Item arrow="horizontal">个人健康状况</List.Item>
        </Picker>
        <Picker
          title="个人生活状态"
          data={livingStatusValue}
          value={student.livingStatus}
          cols={1}
          onOk={(e) => runInAction(() => (student.livingStatus = e))}
        >
          <List.Item arrow="horizontal">个人生活状态</List.Item>
        </Picker>
        <Picker
          title="家庭成员状况"
          data={homeStatusValue}
          value={student.homeStatus}
          cols={1}
          onOk={(e) => runInAction(() => (student.homeStatus = e))}
        >
          <List.Item arrow="horizontal">家庭成员状况</List.Item>
        </Picker>
      
      </List>

      <List renderHeader={() => <b>申请出校</b>}>
        <InputItem
          key="2-0"
          clear
          placeholder="请输入原因"
          value={student.application_reason}
          onChange={(e) => runInAction(() => (student.application_reason = e))}
        >
          出校原因
        </InputItem>
        <InputItem
          key="2-1"
          clear
          placeholder="请输入原因"
          value={student.application_location}
          onChange={(e) =>
            runInAction(() => (student.application_location = e))
          }
        >
          出校地点
        </InputItem>

        <Picker
          title="申请出校日"
          data={applicationStartDayValue}
          value={student.application_start_day}
          cols={1}
          onOk={(e) => runInAction(() => (student.application_start_day = e))}
        >
          <List.Item arrow="horizontal">申请出校日</List.Item>
        </Picker>

        <Picker
          title="申请出校时间"
          data={applicationStartTimeValue}
          value={student.application_start_time}
          cols={1}
          onOk={(e) => runInAction(() => (student.application_start_time = e))}
        >
          <List.Item arrow="horizontal">申请出校时间</List.Item>
        </Picker>

        <Picker
          title="回校日"
          data={applicationEndDayValue}
          value={student.application_end_day}
          cols={1}
          onOk={(e) => runInAction(() => (student.application_end_day = e))}
        >
          <List.Item arrow="horizontal">回校日</List.Item>
        </Picker>
        <Picker
          title="回校时间"
          data={applicationEndTimeValue}
          value={student.application_end_time}
          cols={1}
          onOk={(e) => runInAction(() => (student.application_end_time = e))}
        >
          <List.Item arrow="horizontal">回校时间</List.Item>
        </Picker>
      </List>
      <List
        renderHeader={() => (
          <>
            <b>申请出校策略</b>
            <br />
            从“开始时间”开始，每隔“间隔天数”申请一次出校
            <br />
            <div style={{ fontSize: "12px" }}>
              Q:如何预约一次性申请? 设置开始时间并将申请间隔天数设为-1
            </div>
          </>
        )}
      >
        <List.Item
          extra={
            <Switch
              checked={student.applicationEnabled}
              onChange={handleApplicationChange}
            />
          }
        >
          申请出校开关
          <List.Item.Brief style={{ fontSize: "12px" }}>
            关闭后打卡将不会填写申请出校
          </List.Item.Brief>
        </List.Item>
        <DatePicker
          mode="date"
          value={student.get_scheduler_start_time}
          onOk={(e) => {
            runInAction(
              () =>
                (student.scheduler_start_time = dayjs(e).format("YYYY-MM-DD"))
            )
          }}
        >
          <List.Item arrow="horizontal" multipleLine wrap>
            开始时间
          </List.Item>
        </DatePicker>
        <InputItem
          key="3-1"
          value={student.scheduler_time_segment}
          onChange={(e) =>
            runInAction(() => (student.scheduler_time_segment = e))
          }
          type="digit"
          placeholder="请输入数字"
        >
          间隔天数
        </InputItem>
      </List>
      <WhiteSpace />
      <Button type="primary" onClick={handlerUpdateBtnClick}>
        更新配置
      </Button>
    </>
  )
}

export default observer(ConfigUpdate)
