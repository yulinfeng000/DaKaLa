import { WingBlank, Card, Button } from 'antd-mobile'
import {runInAction } from 'mobx'
import { observer } from 'mobx-react-lite'
import { useEffect } from 'react'
import Axios from '../../lib/axios'
import {dakaInfo} from "../../store"

function DaKaInfo({ stuid }) {
  useEffect(() => {
    if (!dakaInfo.get()) {
      Axios.get(`/stu/${stuid}/callback`).then((resp) => {
        runInAction(() => dakaInfo.set(resp.ck))
      })
    }
  }, [stuid])

  const handleRefreshBtnClick = ()=>{
    runInAction(()=>dakaInfo.set(""))
    Axios.get(`/stu/${stuid}/callback`).then((resp) => {
      runInAction(() => runInAction(()=>dakaInfo.set(resp.ck)))
    })
  }

  return (
    <WingBlank size="md">
      <Card>
        <Card.Header title="最新打卡信息"></Card.Header>
        <Card.Body>{dakaInfo.get()}</Card.Body>
        <Card.Footer extra={<Button inline size="small" onClick={handleRefreshBtnClick} >刷新</Button>} />
      </Card>
    </WingBlank>
  )
}

export default observer(DaKaInfo)
