import { observable, action, computed } from 'mobx'
import dayjs from '../lib/datetime/date'
export const current_stu = observable.box(null)
export const student_conf = observable.object(
  {
    stuid: '',
    cityStatus: '',
    workingPlace: null,
    healthStatus: null,
    livingStatus: null,
    homeStatus: null,
    application_reason: null,
    application_location: null,
    application_start_day: null,
    application_start_time: null,
    application_end_day: null,
    application_end_time: null,
    scheduler_start_time: null,
    scheduler_time_segment: null,
    daka_trigger: false,
    get get_scheduler_start_time() {
      return this.scheduler_start_time
        ? dayjs(this.scheduler_start_time).toDate()
        : this.scheduler_start_time
    },
    updateTrigger(flag) {
      this.daka_trigger = flag
    },
    replace(stu) {
      this.stuid = stu.stuid
      this.cityStatus = [stu.config.cityStatus]
      this.workingPlace = [stu.config.workingPlace]
      this.healthStatus = [stu.config.healthStatus]
      this.livingStatus = [stu.config.livingStatus]
      this.homeStatus = [stu.config.homeStatus]
      this.application_reason = stu.config.application_reason
      this.application_location = stu.config.application_location
      this.application_start_day = [stu.config.application_start_day]
      this.application_start_time = [stu.config.application_start_time]
      this.application_end_day = [stu.config.application_end_day]
      this.application_end_time = [stu.config.application_end_time]
      this.scheduler_start_time = stu.config.scheduler_start_time
      this.scheduler_time_segment = stu.config.scheduler_time_segment
    },
    get applicationEnabled() {
      return this.scheduler_time_segment && this.scheduler_time_segment >= 0
    },
  },
  {
    replace: action,
    updateTrigger: action,
    applicationEnabled: computed,
  },
)

export const dakaInfo = observable.box(null)
