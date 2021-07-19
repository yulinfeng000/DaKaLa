import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
dayjs.extend(duration)
dayjs.locale('zh-cn')

export default dayjs
