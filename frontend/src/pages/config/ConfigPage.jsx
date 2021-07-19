import { NavBar, Icon } from 'antd-mobile'
import { observer } from 'mobx-react-lite'
import { useHistory } from 'react-router-dom'
import ConfigUpdate from '../../components/config/ConfigUpdate'
import { getItem } from '../../lib/storage'
function ConfigPage() {
  const history = useHistory()
  const student = getItem('student')
  return (
    <>
      <NavBar
        icon={<Icon type="left" />}
        onLeftClick={() => history.push('/app/home')}
      >
        配置
      </NavBar>
      <ConfigUpdate stuid={student.stuid} />
    </>
  )
}

export default observer(ConfigPage)
