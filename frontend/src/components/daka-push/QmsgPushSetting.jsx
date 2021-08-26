import {
  Card,
  InputItem,
  WingBlank,
  Button,
  WhiteSpace,
  Toast,
  List,
} from "antd-mobile"
import { runInAction } from "mobx"
import { observer } from "mobx-react-lite"
import { useRef } from "react"
import { useState } from "react"
import Axios from "../../lib/axios"
import { getItem } from "../../lib/storage"
import { pushKey, pushType, qmsgKey as _qmsg } from "../../store"

function QmsgPushSetting() {
  const [qmsgKey, setQmsgKey] = useState(_qmsg.get())

  const ref = useRef()
  const student = getItem("student")

  const handlerKeySave = () => {
    const data = {
      push_type: "qmsg",
      key: qmsgKey,
    }
    Axios.post(`/stu/${student.stuid}/dknotify`, data)
      .then((resp) => {
        console.log(resp)
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
      <WingBlank size="md">
        <Card
          onClick={() => {
            if (ref.current) ref.current.focus()
          }}
        >
          <Card.Header title="qmsg酱 KEY"></Card.Header>
          <Card.Body>
            <InputItem
              ref={ref}
              value={qmsgKey}
              onChange={(e) => setQmsgKey(e)}
            />
          </Card.Body>
          <Card.Footer
            extra={
              <Button inline size="small" onClick={handlerKeySave}>
                保存
              </Button>
            }
          />
        </Card>
      </WingBlank>
      <WhiteSpace />
      <List>
        <List.Item wrap>
          <b>qq推送服务基于qmsg酱</b>
        </List.Item>
        <List.Item wrap>
          1.注册 <a href="https://qmsg.zendee.cn/me.html">qmsg酱</a>
        </List.Item>

        <List.Item wrap>
          2.添加机器人为好友
          <List.Item.Brief>
            若好友未秒通过，请尝试添加其他机器人
          </List.Item.Brief>
        </List.Item>

        <List.Item wrap>3.在qmsg酱中添加自己的qq到“我的列表”</List.Item>

        <List.Item wrap>4.复制“我的key”到此处并保存</List.Item>
      </List>
      <WhiteSpace />
      <List renderHeader={() => "声明"}>
        <List.Item wrap>
          <div
            style={{
              color: "#72777b",
              fontSize: "15px",
            }}
          >
            qmsg酱属于第三方服务,使用qmsg酱代表您遵循qmsg酱的条款。DaKaLa承诺不会使用您的key发送除打卡失败提醒外的其他信息
          </div>
        </List.Item>
      </List>
    </>
  )
}

export default observer(QmsgPushSetting)
