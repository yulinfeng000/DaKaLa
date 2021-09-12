import { NavBar, Icon, ActivityIndicator, Toast, PullToRefresh } from "antd-mobile"
import { throttle } from "lodash"
import { observer } from "mobx-react-lite"
import { useHistory } from "react-router-dom"
import Axios from "../../lib/axios"
import { useCurrentStuPhoto } from "../../lib/hook"
import { getItem } from "../../lib/storage"

function PhotoPage() {
  const history = useHistory()
  const student = getItem("student")
  const { photo, loading, error } = useCurrentStuPhoto()

  if (error) {
    Toast.fail(error.message)
  }

  const handleRefreshBtnClick = throttle(() => {
    Axios.post(`/stu/${student.stuid}/dkphoto/reflush`)
      .then((resp) => {
          
        Toast.success(resp.msg)
      })
      .catch((err) => {
          console.log(err);
        Toast.fail(err.msg)
      })
  }, 5000)


  return (
    <>
      <PullToRefresh
        style={{
          height: document.documentElement.clientHeight,
          overflow: "auto",
        }}
        damping={60}
        direction="down"
        distanceToRefresh={window.devicePixelRatio * 25}
        onRefresh={handleRefreshBtnClick}
      >
        <NavBar
          icon={<Icon type="left" />}
          onLeftClick={() => history.push("/app/home")}
        >
          打卡图
        </NavBar>
        <ActivityIndicator toast animating={loading} text="加载用户图片中..." />
        <img src={`data:image/jpeg;base64,${photo}`} alt="daka_image" />
      </PullToRefresh>
    </>
  )
}

export default observer(PhotoPage)
