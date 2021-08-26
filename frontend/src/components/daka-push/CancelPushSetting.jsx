import { Button, WhiteSpace, Toast, List } from "antd-mobile"
import { runInAction } from "mobx"
import { observer } from "mobx-react-lite"
import Axios from "../../lib/axios"
import { getItem } from "../../lib/storage"
import { pushKey, pushType } from "../../store"

function CancelPushSetting() {
  const student = getItem("student")
  const handleCancel = () => {
    const data = {
      push_type: "",
      key: "",
    }
    Axios.post(`/stu/${student.stuid}/dknotify`, data)
      .then((resp) => {
        Toast.success(resp.msg)
        runInAction(() => {
          pushType.set(resp.push_type)
          pushKey.set(resp.key)
        })
      })
      .catch((err) => {
        Toast.fail(err.msg)
      })
  }
  return (
    <>
      <WhiteSpace />
      <List renderHeader={() => "推送服务声明"}>
        <List.Item wrap>1.打卡推送只会推送打卡失败消息</List.Item>
        <List.Item wrap>
          2.qq推送与微信推送均使用第三方推送服务，使用第三方服务代表您遵循第三方服务的条款，DaKaLa承诺不会使用您的key发送除打卡失败提醒外的其他信息
        </List.Item>
        <List.Item wrap>
          3.友情提示，第三方推送的免费服务即可满足推送需求，请仔细辨别，避免盲目消费
        </List.Item>
      </List>
      <WhiteSpace />
      <Button onClick={handleCancel} type="warning">
        取消推送
      </Button>
    </>
  )
}

export default observer(CancelPushSetting)
