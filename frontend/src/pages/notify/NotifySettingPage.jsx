import { ActivityIndicator, Icon, NavBar, TabBar } from "antd-mobile"
import { observable, runInAction } from "mobx"
import { observer } from "mobx-react-lite"
import { useHistory } from "react-router-dom"
import CancelPushSetting from "../../components/daka-push/CancelPushSetting"
import QmsgPushSetting from "../../components/daka-push/QmsgPushSetting"
import ServerChanPushSetting from "../../components/daka-push/ServerChanPushSetting"
import { usePushSetting } from "../../lib/hook"

export const selectd = observable.box("")
function NotifySettingPage() {
  const { loading } = usePushSetting()
  const history = useHistory()

  return (
    <>
      <ActivityIndicator
        toast
        animating={loading.get()}
        text="加载推送配置中..."
      />
      <NavBar
        icon={<Icon type="left" />}
        onLeftClick={() => history.push("/app/home")}
      >
        推送设置
      </NavBar>
      <TabBar
        tabBarPosition="top"
        unselectedTintColor="#949494"
        tintColor="#33A3F4"
        barTintColor="white"
      >
        <TabBar.Item
          title="QQ推送"
          key="qmsg"
          icon={
            <div
              style={{
                width: "22px",
                height: "22px",
                background:
                  "url(/icon/qq.svg) center center /  21px 21px no-repeat",
              }}
            />
          }
          selectedIcon={
            <div
              style={{
                width: "22px",
                height: "22px",
                background:
                  "url(/icon/qq.svg) center center /  21px 21px no-repeat",
              }}
            />
          }
          selected={selectd.get() === "qmsg"}
          onPress={() => runInAction(() => selectd.set("qmsg"))}
        >
          <QmsgPushSetting />
        </TabBar.Item>

        <TabBar.Item
          title="微信推送"
          key="serverchan"
          icon={
            <div
              style={{
                width: "22px",
                height: "22px",
                background:
                  "url(/icon/wechat.svg) center center /  21px 21px no-repeat",
              }}
            />
          }
          selectedIcon={
            <div
              style={{
                width: "22px",
                height: "22px",
                background:
                  "url(/icon/wechat.svg) center center /  21px 21px no-repeat",
              }}
            />
          }
          selected={selectd.get() === "serverchan"}
          onPress={() => runInAction(() => selectd.set("serverchan"))}
        >
          <ServerChanPushSetting />
        </TabBar.Item>
        <TabBar.Item
          title="邮箱推送"
          key="email"
          icon={
            <div
              style={{
                width: "22px",
                height: "22px",
                background:
                  "url(/icon/email.svg) center center /  21px 21px no-repeat",
              }}
            />
          }
          selectedIcon={
            <div
              style={{
                width: "22px",
                height: "22px",
                background:
                  "url(/icon/email.svg) center center /  21px 21px no-repeat",
              }}
            />
          }
          selected={selectd.get() === "email"}
          onPress={() => runInAction(() => selectd.set("email"))}
        >
          暂未开通
        </TabBar.Item>
        <TabBar.Item
          title="无推送"
          key="None"
          icon={
            <div
              style={{
                width: "22px",
                height: "22px",
                background:
                  "url(/icon/cancel.svg) center center /  21px 21px no-repeat",
              }}
            />
          }
          selectedIcon={
            <div
              style={{
                width: "22px",
                height: "22px",
                background:
                  "url(/icon/cancel.svg) center center /  21px 21px no-repeat",
              }}
            />
          }
          selected={selectd.get() === "None" || selectd.get() === ""}
          onPress={() => runInAction(() => selectd.set("None"))}
        >
          <CancelPushSetting />
        </TabBar.Item>
      </TabBar>
    </>
  )
}

export default observer(NotifySettingPage)
