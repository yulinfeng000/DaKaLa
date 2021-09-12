import { runInAction } from "mobx"
import useSWR from "swr"
import { selectd } from "../../pages/notify/NotifySettingPage"
import { pushKey, pushSettingLoading, pushType } from "../../store"
import Axios from "../axios"
import { getItem } from "../storage"

export const useCurrentStuPhoto = () => {
  const student = getItem("student")
  const { data, error } = useSWR(`/stu/${student.stuid}/photo`, async (url) => {
    const resp = await Axios.get(url, { responseType: "arraybuffer" })
    return Buffer.from(resp.data, "base64").toString("base64")
  })

  return {
    photo: data ? data : "",
    loading: !data,
    error,
  }
}
export const useDakaRecords = () => {
  const student = getItem("student")
  const { data, error } = useSWR(
    `/stu/${student.stuid}/dkrecords/info`,
    async (url) => {
      const resp = await Axios.get(url)
      return {
        //@ts-ignore
        combo: resp.combo,
        //@ts-ignore
        records: resp.records,
      }
    }
  )

  return {
    combo: data.combo,
    records: data.records,
    loading: !data,
    error,
  }
}

export const usePushSetting = () => {
  const student = getItem("student")
  useSWR(`/stu/${student.stuid}/dknotify/info`, async (url) => {
    const resp = await Axios.post(url)
    runInAction(() => {
      pushKey.set(resp.key)
      pushType.set(resp.ptype)
      console.log(resp)
      selectd.set(resp.ptype ? resp.ptype : "")
      pushSettingLoading.set(false)
    })
  })
  return { pushKey, pushType, loading: pushSettingLoading }
}
