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
import { pushKey, pushType, emailKey as _email } from "../../store"

function EmailPushSetting() {
  const [emailKey, setEmailKey] = useState(_email.get())

  const ref = useRef()
  const student = getItem("student")

  const handlerKeySave = () => {
    const data = {
      push_type: "email",
      key: emailKey,
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
          <Card.Header title="Email"></Card.Header>
          <Card.Body>
            <InputItem
              ref={ref}
              value={emailKey}
              onChange={(e) => setEmailKey(e)}
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
          email推送由服务器推送，请确保manager@merborn.fun不在垃圾箱中
        </List.Item>
      </List>
    </>
  )
}

export default observer(EmailPushSetting)
