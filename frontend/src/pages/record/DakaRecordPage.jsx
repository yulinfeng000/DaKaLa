import { NavBar, Icon, List, PullToRefresh, Toast } from "antd-mobile"
import { throttle } from "lodash"
import { runInAction } from "mobx"
import { observer } from "mobx-react-lite"
import { useRef } from "react"
import { useEffect } from "react"
import { useHistory } from "react-router-dom"
import Axios from "../../lib/axios"
import { getItem } from "../../lib/storage"
import { dakaCombo, dakaRecords } from "../../store"

function DakaRecordPage() {
  const student = getItem("student")
  const history = useHistory()

  useEffect(() => {
    Axios.get(`/stu/${student.stuid}/dkrecords/info`).then((resp) => {
      console.log(resp)
      runInAction(() => {
        dakaCombo.set(resp.combo)
        dakaRecords.replace(resp.records)
      })
    })
  }, [student.stuid])

  const handleRefreshBtnClick = throttle(() => {
    Axios.post(`/stu/${student.stuid}/dkrecords/reflush`)
      .then((resp) => {
        runInAction(() => {
          dakaRecords.replace(resp.records)
          dakaCombo.set(resp.combo)
        })
        Toast.success(resp.msg)
      })
      .catch((err) => {
        Toast.fail(err.msg)
      })
  }, 5000)

  const renderRecordList = () => {
    return dakaRecords.map((it) => (
      <List.Item extra={it[0]} key={it[1]}>
        {it[1]}
      </List.Item>
    ))
  }
  const ref = useRef()

  return (
    <>
      <NavBar
        icon={<Icon type="left" />}
        onLeftClick={() => history.push("/app/home")}
      >
        打卡记录
      </NavBar>
      <PullToRefresh
        style={{
          height: document.documentElement.clientHeight,
          overflow: "auto",
        }}
        damping={60}
        direction="down"
        distanceToRefresh={window.devicePixelRatio * 25}
        onRefresh={handleRefreshBtnClick}
        ref={ref}
      >
        <List renderHeader={() => "打卡记录"}>{renderRecordList()}</List>
      </PullToRefresh>
    </>
  )
}

export default observer(DakaRecordPage)
