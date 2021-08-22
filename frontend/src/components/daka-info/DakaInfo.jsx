import { WingBlank, Card, Button, Toast } from "antd-mobile"
import { runInAction } from "mobx"
import { observer } from "mobx-react-lite"
import { useEffect } from "react"
import { useHistory } from "react-router-dom"
import Axios from "../../lib/axios"
import { dakaCombo, dakaInfo, dakaRecords } from "../../store"

function DaKaInfo({ stuid }) {
  const history = useHistory()

  const renderCombo = (combo) => {
    if (combo == null) {
      return "目前未获取到记录"
    } else {
      return `目前已经连续打卡 ${dakaCombo.get()} 天!`
    }
  }

  useEffect(() => {
    async function fetchs() {
      try {
        const dkr = await Axios.get(`/stu/${stuid}/dkrecords/info`)
        const dki = await Axios.get(`/stu/${stuid}/callback`)
        runInAction(() => {
          dakaCombo.set(dkr.combo)
          dakaRecords.replace(dkr.records)
          dakaInfo.set(dki.ck)
        })
      } catch (err) {
        if (err.msg) {
          Toast.fail(err.msg)
        }
      }
    }
    fetchs()
  }, [stuid])

  const handleRefreshBtnClick = () => {
    runInAction(() => dakaInfo.set(""))
    Axios.get(`/stu/${stuid}/callback`).then((resp) => {
      runInAction(() => runInAction(() => dakaInfo.set(resp.ck)))
    })
  }

  const handleShowBtnClick = () => [history.push("/app/records")]

  

  return (
    <WingBlank size="md">
      <Card>
        <Card.Header title="最新打卡信息"></Card.Header>
        <Card.Body>
          {dakaInfo.get()},{renderCombo(dakaCombo.get())}
        </Card.Body>
        <Card.Footer
          extra={
            <Button inline size="small" onClick={handleRefreshBtnClick}>
              刷新
            </Button>
          }
          content={
            <Button inline size="small" onClick={handleShowBtnClick}>
              查看记录
            </Button>
          }
        />
      </Card>
    </WingBlank>
  )
}

export default observer(DaKaInfo)
