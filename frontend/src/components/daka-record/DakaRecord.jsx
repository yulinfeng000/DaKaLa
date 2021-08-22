import { Button, Card, Toast, WingBlank } from "antd-mobile"
import { throttle } from "lodash"
import { runInAction } from "mobx"
import { observer } from "mobx-react-lite"
import { useEffect } from "react"
import Axios from "../../lib/axios"
import { dakaCombo, dakaRecords } from "../../store"
import { useHistory } from "react-router-dom"

function DakaRecord({ stuid }) {
  const history = useHistory()
  const fetchData = (stuid) => {
    Axios.get(`/stu/${stuid}/dkrecords/info`).then((resp) => {
      console.log(resp)
      runInAction(() => {
        dakaCombo.set(resp.combo)
        dakaRecords.replace(resp.records)
      })
    })
  }
  useEffect(() => {
    fetchData(stuid)
  }, [stuid])

  const handleRefreshBtnClick = throttle(() => {
    Axios.post(`/stu/${stuid}/dkrecords/reflush`)
      .then((resp) => {
        runInAction(() => {
          dakaRecords.replace(resp.records)
          dakaCombo.set(resp.combo)
        })
        Toast.success(resp.msg)
      })
      .catch((err) => {
        Toast.fail("请稍后再点击")
      })
  }, 5000)

  const renderCombo = (combo) => {
    if (combo == null) {
      return "未获取到记录"
    } else {
      return `已经连续打卡 ${dakaCombo.get()} 天!`
    }
  }

  const handleShowBtnClick = () => [history.push("/app/records")]

  return (
    <>
      <WingBlank size="md">
        <Card>
          <Card.Header title="打卡记录"></Card.Header>
          <Card.Body>{renderCombo(dakaCombo.get())}</Card.Body>
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
    </>
  )
}

export default observer(DakaRecord)
