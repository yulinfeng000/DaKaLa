import { NavBar, Icon, List } from "antd-mobile"
import { runInAction } from "mobx"
import { observer } from "mobx-react-lite"
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

  const renderRecordList = () => {
    return dakaRecords.map((it) => <List.Item extra={it[0]}>{it[1]}</List.Item>)
  }

  return (
    <>
      <NavBar
        icon={<Icon type="left" />}
        onLeftClick={() => history.push("/app/home")}
      >
        打卡记录
      </NavBar>
      <List renderHeader={() => "打卡记录"}>{renderRecordList()}</List>
    </>
  )
}

export default observer(DakaRecordPage)
