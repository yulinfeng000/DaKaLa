import useSWR from "swr"
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
