import "antd-mobile/dist/antd-mobile.css"
import { HashRouter as Router, Route, Switch } from "react-router-dom"
import HomePage from "./pages/home/HomePage"
import IndexPage from "./pages/index/IndexPage"
import LoginPage from "./pages/login/LoginPage"
import RegisterPage from "./pages/register/RegisterPage"
import AuthRoute from "./lib/router/AuthRoute"
import ConfigPage from "./pages/config/ConfigPage"
import PhotoPage from "./pages/photo/PhotoPage"
import DakaRecordPage from "./pages/record/DakaRecordPage"
import NotifySettingPage from "./pages/notify/NotifySettingPage"

function App() {
  return (
    <Router>
      <Switch>
        <AuthRoute
          component={HomePage}
          path="/app/home"
          redirect="/login"
          exact
        />
        <AuthRoute
          component={ConfigPage}
          path="/app/conf"
          redirect="/login"
          exact
        />
        <AuthRoute
          component={PhotoPage}
          path="/app/photo"
          redirect="/login"
          exact
        />
        <AuthRoute
          component={DakaRecordPage}
          path="/app/records"
          redirect="/login"
          exact
        />
        <AuthRoute
          component={NotifySettingPage}
          path="/app/notify"
          redirect="/login"
          exact
        />
        <Route component={RegisterPage} path="/register" exact />
        <Route component={LoginPage} path="/login" exact />
        <Route component={IndexPage} path="/" exact />
      </Switch>
    </Router>
  )
}

export default App
