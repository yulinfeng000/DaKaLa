import { observer } from 'mobx-react-lite'
import { Redirect } from 'react-router-dom'
import cookies from '../../lib/cookies'
import { getItem } from '../../lib/storage'

function IndexPage() {
  if (getItem('student') && cookies.get('token'))
    return <Redirect to="/app/home" />
  else return <Redirect to="/login" />
}
export default observer(IndexPage)
