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
import { pushKey, pushType, serverchanKey as _serverchan } from "../../store"

function ServerChanPushSetting() {
  const [serverChanKey, setServerChanKey] = useState(_serverchan.get())

  const ref = useRef()
  const student = getItem("student")

  const handlerKeySave = () => {
    const data = {
      push_type: "serverchan",
      key: serverChanKey,
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
          <Card.Header title="server酱 KEY"></Card.Header>
          <Card.Body>
            <InputItem
              ref={ref}
              value={serverChanKey}
              onChange={(e) => setServerChanKey(e)}
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
          <b>微信推送服务基于server酱 turbo版</b>
        </List.Item>
        <List.Item wrap>
          1.注册 <a href="https://sct.ftqq.com/login">server 酱</a>
        </List.Item>

        <List.Item wrap>2. 复制send key 到此处并保存</List.Item>
      </List>
      <WhiteSpace />
      <List renderHeader={() => "声明"}>
        <List.Item wrap>
          <div
            style={{
              color: "#72777b",
              fontSize:'15px'
            }}
          >
            server酱属于第三方服务,使用server酱代表您遵循server酱的条款。DaKaLa承诺不会使用您的key发送除打卡失败提醒外的其他信息
          </div>
        </List.Item>
      </List>
    </>
  )
}

export default observer(ServerChanPushSetting)
