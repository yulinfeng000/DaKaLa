import {NavBar, Icon, ActivityIndicator, Toast} from 'antd-mobile'
import {observer} from 'mobx-react-lite'
import {useHistory} from 'react-router-dom'
import {useCurrentStuPhoto} from "../../lib/hook";

function PhotoPage() {
    const history = useHistory()
    const {photo, loading, error} = useCurrentStuPhoto()

    if (error) {
        Toast.fail(error.message)
    }

    return (
        <>
            <NavBar
                icon={<Icon type="left"/>}
                onLeftClick={() => history.push('/app/home')}
            >
                打卡图
            </NavBar>
            <ActivityIndicator toast animating={loading} text="加载用户图片中..."/>
            <img src={`data:image/jpeg;base64,${photo}`} alt="daka_image"/>
        </>
    )
}

export default observer(PhotoPage)
